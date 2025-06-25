import os
import json

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

def print_error_summary():
    print("\n\n📊 Global Error Summary:\n")

    # Try individual files first (preferred method)
    error_files = load_error_files()
    
    if error_files:
        print("📁 Using individual node error files:")
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
