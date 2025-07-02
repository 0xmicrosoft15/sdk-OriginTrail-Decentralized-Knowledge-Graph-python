# scripts/print_aggregated_errors.py

import os
import json

ERROR_DIR = "test_output"

def safe_rate(success, fail):
    total = success + fail
    return round((success / total) * 100, 2) if total > 0 else 0.0

def avg(times):
    return round(sum(times) / len(times), 2) if times else 0.0

def create_aggregated_error_file():
    """Create aggregated error_stats.json from individual node files"""
    aggregated_errors = {}
    
    # Define all possible nodes
    testnet_nodes = [
        "Node 01", "Node 04", "Node 05", "Node 06", "Node 07", "Node 08", 
        "Node 09", "Node 10", "Node 13", "Node 14", "Node 21", "Node 23", "Node 37"
    ]
    
    mainnet_nodes = [
        "Node 25", "Node 26", "Node 27", "Node 28", "Node 29", "Node 30"
    ]
    
    all_nodes = testnet_nodes + mainnet_nodes
    
    # Read each individual node error file
    for node_name in all_nodes:
        node_file = os.path.join(ERROR_DIR, f"errors_{node_name.replace(' ', '_')}.json")
        if os.path.exists(node_file):
            try:
                with open(node_file, 'r') as f:
                    node_errors = json.load(f)
                    if node_errors:  # Only add if there are errors
                        aggregated_errors[node_name] = node_errors
            except Exception as e:
                print(f"⚠️ Warning: Could not read {node_file}: {e}")
    
    # Write aggregated file
    aggregated_file = os.path.join(ERROR_DIR, "error_stats.json")
    with open(aggregated_file, 'w') as f:
        json.dump(aggregated_errors, f, indent=2)
    
    return aggregated_errors

def get_all_errors_for_node(node_name):
    """Get all errors for a specific node from multiple sources"""
    all_errors = {}
    
    # Source 1: Aggregated error file
    aggregated_file = os.path.join(ERROR_DIR, "error_stats.json")
    if os.path.exists(aggregated_file):
        try:
            with open(aggregated_file, 'r') as f:
                aggregated_errors = json.load(f)
                if node_name in aggregated_errors:
                    all_errors.update(aggregated_errors[node_name])
        except Exception:
            pass
    
    # Source 2: Individual node error file
    node_file = os.path.join(ERROR_DIR, f"errors_{node_name.replace(' ', '_')}.json")
    if os.path.exists(node_file):
        try:
            with open(node_file, 'r') as f:
                node_errors = json.load(f)
                all_errors.update(node_errors)
        except Exception:
            pass
    
    # Source 3: Check for any other error files that might contain this node's errors
    # This handles cases where errors might be stored in different formats
    for filename in os.listdir(ERROR_DIR):
        if filename.endswith('.json') and 'error' in filename.lower():
            file_path = os.path.join(ERROR_DIR, filename)
            try:
                with open(file_path, 'r') as f:
                    file_data = json.load(f)
                    if isinstance(file_data, dict) and node_name in file_data:
                        if isinstance(file_data[node_name], dict):
                            all_errors.update(file_data[node_name])
            except Exception:
                pass
    
    return all_errors

def print_all_errors():
    print("\n📊 Error Breakdown by Node:\n")
    
    # Create aggregated error file from individual files
    aggregated_errors = create_aggregated_error_file()
    
    # Define all possible nodes for both testnet and mainnet
    testnet_nodes = [
        "Node 01", "Node 04", "Node 05", "Node 06", "Node 07", "Node 08", 
        "Node 09", "Node 10", "Node 13", "Node 14", "Node 21", "Node 23", "Node 37"
    ]
    
    mainnet_nodes = [
        "Node 25", "Node 26", "Node 27", "Node 28", "Node 29", "Node 30"
    ]
    
    all_nodes = testnet_nodes + mainnet_nodes
    
    # Get nodes that have errors
    nodes_with_errors = list(aggregated_errors.keys())
    
    # If no aggregated errors, check individual files
    if not nodes_with_errors:
        for node_name in all_nodes:
            node_file = os.path.join(ERROR_DIR, f"errors_{node_name.replace(' ', '_')}.json")
            if os.path.exists(node_file):
                try:
                    with open(node_file, 'r') as f:
                        node_errors = json.load(f)
                        if node_errors:
                            nodes_with_errors.append(node_name)
                except Exception:
                    pass
    
    # If still no nodes with errors, check all nodes anyway
    if not nodes_with_errors:
        nodes_with_errors = all_nodes
    
    # Process each node
    for node_name in nodes_with_errors:
        errors = get_all_errors_for_node(node_name)
        
        if errors:
            print(f"🔧 {node_name}")
            for error_key, count in errors.items():
                print(f"  • {count}x {error_key}")
            print()
        else:
            print(f"✅ {node_name}: No errors\n")

def print_error_for_node():
    node_to_test = os.getenv("NODE_TO_TEST")
    if not node_to_test:
        return  # Skip if not running in per-node context

    print("\n📊 Error Breakdown by Node:\n")

    errors = get_all_errors_for_node(node_to_test)
    
    print(f"🔧 {node_to_test}")
    if not errors:
        print("  ✅ No errors\n")
    else:
        for error_key, count in errors.items():
            print(f"  • {count}x {error_key}")
        print()

if __name__ == "__main__":
    if os.getenv("AGGREGATE_MODE") == "true":
        print_all_errors()
    else:
        print_error_for_node()
