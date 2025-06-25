import os
import json
import sys
import glob

ERROR_DIR = "test_output"  # Directory where error files are stored

def load_error_files():
    """Load individual error files for each node"""
    if not os.path.exists(ERROR_DIR):
        print(f"⚠️ Error directory not found: {ERROR_DIR}")
        return []
    
    return [
        f for f in os.listdir(ERROR_DIR)
        if f.startswith("errors_Node_") and f.endswith(".json")
    ]

def load_aggregated_error_file():
    """Load the aggregated error file if it exists"""
    error_file_path = os.path.join(ERROR_DIR, "error_stats.json")
    
    if os.path.exists(error_file_path):
        try:
            with open(error_file_path, "r") as f:
                return json.load(f)
        except Exception as e:
            print(f"⚠️ Failed to read aggregated error file: {str(e)}")
    
    return {}

def combine_error_files():
    """Combine all error files from parallel Jenkins stages"""
    combined_errors = {}
    
    # Look for error files in the current directory and subdirectories
    error_patterns = [
        "test_output/errors_*.json",
        "*/test_output/errors_*.json",  # For archived workspaces
        "**/test_output/errors_*.json"  # For nested archived workspaces
    ]
    
    for pattern in error_patterns:
        for error_file in glob.glob(pattern, recursive=True):
            try:
                with open(error_file, 'r') as f:
                    node_errors = json.load(f)
                    
                # Extract node name from filename
                filename = os.path.basename(error_file)
                node_name = filename.replace("errors_", "").replace(".json", "").replace("_", " ")
                
                if node_name not in combined_errors:
                    combined_errors[node_name] = {}
                
                # Merge errors
                for error_key, count in node_errors.items():
                    if error_key in combined_errors[node_name]:
                        combined_errors[node_name][error_key] += count
                    else:
                        combined_errors[node_name][error_key] = count
                        
            except Exception as e:
                print(f"⚠️ Failed to read {error_file}: {str(e)}")
    
    return combined_errors

def print_error_summary():
    print("\n\n📊 Error Breakdown by Node:\n")

    # Check if a specific node is being tested
    node_to_test = os.getenv("NODE_TO_TEST")
    
    # First try to combine all error files from parallel execution
    combined_errors = combine_error_files()
    
    if combined_errors:
        print("📁 Using combined error files from parallel execution:")
        
        # If a specific node is being tested, only show that node's errors
        if node_to_test:
            if node_to_test in combined_errors:
                print(f"🔧 {node_to_test}")
                node_errors = combined_errors[node_to_test]
                
                if not node_errors:
                    print("  ✅ No errors")
                else:
                    for error_key, count in node_errors.items():
                        print(f"  • {count}x {error_key}")
                print()
            else:
                print(f"🔧 {node_to_test}")
                print("  ✅ No errors")
                print()
        else:
            # Show all nodes
            for node_name in sorted(combined_errors.keys()):
                print(f"🔧 {node_name}")

                node_errors = combined_errors[node_name]
                
                if not node_errors:
                    print("  ✅ No errors")
                else:
                    for error_key, count in node_errors.items():
                        print(f"  • {count}x {error_key}")

                print()
        return
    
    # Fallback to original logic
    error_files = load_error_files()
    
    if error_files:
        print("📁 Using individual node error files:")
        
        # If a specific node is being tested, only show that node's errors
        if node_to_test:
            target_filename = f"errors_{node_to_test.replace(' ', '_')}.json"
            error_files = [f for f in error_files if f == target_filename]
        
        for filename in sorted(error_files):
            node_name = filename.replace("errors_", "").replace(".json", "").replace("_", " ")
            print(f"🔧 {node_name}")

            try:
                with open(os.path.join(ERROR_DIR, filename), "r") as f:
                    errors = json.load(f)

                if not errors:
                    print("  ✅ No errors")
                else:
                    for message, count in errors.items():
                        print(f"  • {count}x {message}")

            except Exception as e:
                print(f"  ⚠️ Failed to read or parse {filename}: {str(e)}")

            print()
    
    else:
        # Fallback to aggregated file
        print("📁 Using aggregated error file:")
        error_data = load_aggregated_error_file()
        
        if not error_data:
            print("✅ No error data found")
            return

        # If a specific node is being tested, only show that node's errors
        if node_to_test:
            if node_to_test in error_data:
                print(f"🔧 {node_to_test}")
                node_errors = error_data[node_to_test]
                
                if not node_errors:
                    print("  ✅ No errors")
                else:
                    for error_key, count in node_errors.items():
                        print(f"  • {count}x {error_key}")
                print()
            else:
                print(f"🔧 {node_to_test}")
                print("  ✅ No errors")
                print()
        else:
            # Show all nodes
            for node_name in sorted(error_data.keys()):
                print(f"🔧 {node_name}")

                node_errors = error_data[node_name]
                
                if not node_errors:
                    print("  ✅ No errors")
                else:
                    for error_key, count in node_errors.items():
                        print(f"  • {count}x {error_key}")

                print()

if __name__ == "__main__":
    print_error_summary()
