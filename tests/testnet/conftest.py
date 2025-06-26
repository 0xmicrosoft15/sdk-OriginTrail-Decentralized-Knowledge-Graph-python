# tests/testnet/conftest.py

import os
import json
from .stats_tracker import global_stats, error_stats

def pytest_sessionstart(session):
    """Clear error stats at the start of each test session (if they exist)"""
    error_file = "test_output/error_stats.json"
    stats_file = "test_output/global_stats.json"
    
    if os.path.exists(error_file):
        os.remove(error_file)
    if os.path.exists(stats_file):
        os.remove(stats_file)

def pytest_sessionfinish(session, exitstatus):
    print("\n\n📊 Global Publish Summary:")

    stats_file = "test_output/global_stats.json"
    error_file = "test_output/error_stats.json"

    global_data = {}
    if os.path.exists(stats_file):
        with open(stats_file, 'r') as f:
            try:
                global_data = json.load(f)
            except json.JSONDecodeError:
                global_data = {}

    for blockchain, node_data in global_data.items():
        print(f"\n🔗 Blockchain: {blockchain}")
        for node_name, results in node_data.items():
            print(f"  • {node_name}:")

            # Publish
            p_success = results.get("publish_success", 0)
            p_failed = results.get("publish_failed", 0)
            p_rate = round(p_success / (p_success + p_failed) * 100, 2) if (p_success + p_failed) > 0 else 0.0
            print(f"    🔸 Publish: ✅ {p_success} / ❌ {p_failed} -> {p_rate}%")

            # Query
            q_success = results.get("query_success", 0)
            q_failed = results.get("query_failed", 0)
            q_rate = round(q_success / (q_success + q_failed) * 100, 2) if (q_success + q_failed) > 0 else 0.0
            print(f"    🔸 Query:   ✅ {q_success} / ❌ {q_failed} -> {q_rate}%")

            # Local Get
            lg_success = results.get("local_get_success", 0)
            lg_failed = results.get("local_get_failed", 0)
            lg_rate = round(lg_success / (lg_success + lg_failed) * 100, 2) if (lg_success + lg_failed) > 0 else 0.0
            print(f"    🔸 Local Get: ✅ {lg_success} / ❌ {lg_failed} -> {lg_rate}%")

            # Remote Get
            rg_success = results.get("remote_get_success", 0)
            rg_failed = results.get("remote_get_failed", 0)
            rg_rate = round(rg_success / (rg_success + rg_failed) * 100, 2) if (rg_success + rg_failed) > 0 else 0.0
            print(f"    🔸 Get: ✅ {rg_success} / ❌ {rg_failed} -> {rg_rate}%")

            # Timing
            def format_time(seconds):
                return f"{int(seconds // 60)} min {seconds % 60:.2f} sec" if seconds >= 60 else f"{seconds:.2f} seconds"

            def avg_time(times):
                return sum(times) / len(times) if times else 0.0

            print(f"    ⏱️ Avg Publish Time: {format_time(avg_time(results.get('publish_times', [])))}")
            print(f"    ⏱️ Avg Query Time: {format_time(avg_time(results.get('query_times', [])))}")
            print(f"    ⏱️ Avg Local Get Time: {format_time(avg_time(results.get('local_get_times', [])))}")
            print(f"    ⏱️ Avg Get Time: {format_time(avg_time(results.get('remote_get_times', [])))}")

    print("\n📊 Error Breakdown by Node:")

    node_to_test = os.getenv("NODE_TO_TEST")
    if node_to_test:
        # Try to get errors from multiple sources to ensure we capture everything
        all_errors = {}
        
        print(f"DEBUG: Looking for errors for {node_to_test}")
        
        # Source 1: Aggregated error file
        if os.path.exists(error_file):
            print(f"DEBUG: Found aggregated error file: {error_file}")
            with open(error_file, 'r') as f:
                try:
                    aggregated_errors = json.load(f)
                    print(f"DEBUG: Aggregated file contains {len(aggregated_errors)} nodes: {list(aggregated_errors.keys())}")
                    if node_to_test in aggregated_errors:
                        node_errors = aggregated_errors[node_to_test]
                        print(f"DEBUG: Found {len(node_errors)} errors for {node_to_test} in aggregated file")
                        all_errors.update(node_errors)
                    else:
                        print(f"DEBUG: {node_to_test} not found in aggregated file")
                except json.JSONDecodeError as e:
                    print(f"DEBUG: Failed to parse aggregated file: {e}")
        else:
            print(f"DEBUG: Aggregated error file not found: {error_file}")
        
        # Source 2: Individual node error file
        node_error_file = f"test_output/errors_{node_to_test.replace(' ', '_')}.json"
        if os.path.exists(node_error_file):
            print(f"DEBUG: Found individual error file: {node_error_file}")
            with open(node_error_file, 'r') as f:
                try:
                    node_errors = json.load(f)
                    print(f"DEBUG: Individual file contains {len(node_errors)} errors for {node_to_test}")
                    all_errors.update(node_errors)
                except json.JSONDecodeError as e:
                    print(f"DEBUG: Failed to parse individual file: {e}")
        else:
            print(f"DEBUG: Individual error file not found: {node_error_file}")
        
        # Source 3: Global error_stats from memory (if available)
        if hasattr(error_stats, 'get') and node_to_test in error_stats:
            print(f"DEBUG: Found {len(error_stats[node_to_test])} errors in memory for {node_to_test}")
            all_errors.update(error_stats[node_to_test])
        else:
            print(f"DEBUG: No errors found in memory for {node_to_test}")
        
        print(f"DEBUG: Total errors collected: {len(all_errors)}")
        for key, count in all_errors.items():
            print(f"DEBUG: Error key: {key} (count: {count})")
        
        if all_errors:
            print(f"🔧 {node_to_test}")
            for message, count in all_errors.items():
                print(f"  • {count}x {message}")
        else:
            print(f"✅ {node_to_test}: No errors")
    else:
        # Fallback to global if no specific node is targeted
        print("\n📊 Error Breakdown by Node:")
        error_data = {}
        if os.path.exists(error_file):
            with open(error_file, 'r') as f:
                try:
                    error_data = json.load(f)
                except json.JSONDecodeError:
                    error_data = {}

        if not error_data:
            print("✅ No errors recorded.")
        else:
            for node_name, errors in error_data.items():
                if errors:
                    print(f"\n🔧 {node_name}")
                    for message, count in errors.items():
                        print(f"  • {count}x {message}")
                else:
                    print(f"✅ {node_name}: No errors")

    # Clean up after printing
    if os.path.exists(error_file):
        os.remove(error_file)
    if os.path.exists(stats_file):
        os.remove(stats_file)