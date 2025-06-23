# tests/mainnet/conftest.py

import os
import json
from .stats_tracker import global_stats, error_stats

def pytest_sessionstart(session):
    """Clear error stats at the start of each test session"""
    error_file = "test_output/error_stats.json"
    stats_file = "test_output/global_stats.json"
    
    if os.path.exists(error_file):
        os.remove(error_file)
    if os.path.exists(stats_file):
        os.remove(stats_file)

def pytest_sessionfinish(session, exitstatus):
    print("\n\n📊 Global Publish Summary:")

    # Read global stats from the temporary file
    stats_file = "test_output/global_stats.json"
    
    if os.path.exists(stats_file):
        with open(stats_file, 'r') as f:
            try:
                global_stats = json.load(f)
            except:
                global_stats = {}
    else:
        global_stats = {}

    for blockchain, node_data in global_stats.items():
        print(f"\n🔗 Blockchain: {blockchain}")
        for node_name, results in node_data.items():
            print(f"  • {node_name}:")
            
            # Publish stats
            p_success = results.get("publish_success", 0)
            p_failed = results.get("publish_failed", 0)
            p_rate = round(p_success / (p_success + p_failed) * 100, 2) if (p_success + p_failed) > 0 else 0.0
            print(f"    🔸 Publish: ✅ {p_success} / ❌ {p_failed} -> {p_rate}%")
            
            # Query stats
            q_success = results.get("query_success", 0)
            q_failed = results.get("query_failed", 0)
            q_rate = round(q_success / (q_success + q_failed) * 100, 2) if (q_success + q_failed) > 0 else 0.0
            print(f"    🔸 Query:   ✅ {q_success} / ❌ {q_failed} -> {q_rate}%")
            
            # Local Get stats
            lg_success = results.get("local_get_success", 0)
            lg_failed = results.get("local_get_failed", 0)
            lg_rate = round(lg_success / (lg_success + lg_failed) * 100, 2) if (lg_success + lg_failed) > 0 else 0.0
            print(f"    🔸 Local Get: ✅ {lg_success} / ❌ {lg_failed} -> {lg_rate}%")
            
            # Remote Get stats
            rg_success = results.get("remote_get_success", 0)
            rg_failed = results.get("remote_get_failed", 0)
            rg_rate = round(rg_success / (rg_success + rg_failed) * 100, 2) if (rg_success + rg_failed) > 0 else 0.0
            print(f"    🔸 Get: ✅ {rg_success} / ❌ {rg_failed} -> {rg_rate}%")
            
            # Average times
            p_times = results.get("publish_times", [])
            q_times = results.get("query_times", [])
            lg_times = results.get("local_get_times", [])
            rg_times = results.get("remote_get_times", [])
            
            def format_time(seconds):
                if seconds >= 60:
                    minutes = int(seconds // 60)
                    secs = seconds % 60
                    return f"{minutes} min {secs:.2f} sec"
                else:
                    return f"{seconds:.2f} seconds"
            
            def avg_time(times):
                return sum(times) / len(times) if times else 0.0
            
            print(f"    ⏱️ Avg Publish Time: {format_time(avg_time(p_times))}")
            print(f"    ⏱️ Avg Query Time: {format_time(avg_time(q_times))}")
            print(f"    ⏱️ Avg Local Get Time: {format_time(avg_time(lg_times))}")
            print(f"    ⏱️ Avg Get Time: {format_time(avg_time(rg_times))}")

    print("\n📊 Error Breakdown by Node:")
    
    # Read errors from the temporary file
    error_file = "test_output/error_stats.json"
    
    if os.path.exists(error_file):
        with open(error_file, 'r') as f:
            try:
                error_data = json.load(f)
            except:
                error_data = {}
    else:
        error_data = {}
    
    if not error_data:
        print("✅ No errors recorded.")
    else:
        for node_name, errors in error_data.items():
            if errors:  # Only show nodes that have errors
                print(f"\n🔧 {node_name}")
                for message, count in errors.items():
                    print(f"  • {count}x {message}")
            else:
                print(f"✅ {node_name}: No errors")
    
    # Clean up the temporary files
    if os.path.exists(error_file):
        os.remove(error_file)
    if os.path.exists(stats_file):
        os.remove(stats_file) 