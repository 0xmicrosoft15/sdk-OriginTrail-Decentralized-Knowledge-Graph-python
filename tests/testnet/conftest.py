# tests/testnet/conftest.py

import os
import json
from .stats_tracker import global_stats, error_stats
import pytest
import time
from datetime import datetime

def pytest_configure(config):
    """Configure pytest to collect custom markers"""
    config.addinivalue_line("markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')")

def pytest_collection_modifyitems(config, items):
    """Add markers to tests based on their names"""
    for item in items:
        if "testnet" in item.nodeid.lower():
            item.add_marker(pytest.mark.testnet)
        if "mainnet" in item.nodeid.lower():
            item.add_marker(pytest.mark.mainnet)

@pytest.fixture(scope="session", autouse=True)
def setup_test_environment():
    """Setup test environment before running tests"""
    # Create test_output directory if it doesn't exist
    os.makedirs("test_output", exist_ok=True)
    
    # Clear any existing error files at the start of the session
    error_files = [
        "test_output/error_stats.json",
        "test_output/global_stats.json"
    ]
    
    for error_file in error_files:
        if os.path.exists(error_file):
            try:
                os.remove(error_file)
            except:
                pass

def get_error_breakdown(node_name):
    """Get error breakdown for a specific node from multiple sources"""
    all_errors = {}
    
    # Source 1: Aggregated error file
    aggregated_file = "test_output/error_stats.json"
    if os.path.exists(aggregated_file):
        try:
            with open(aggregated_file, 'r') as f:
                aggregated_errors = json.load(f)
                if node_name in aggregated_errors:
                    all_errors.update(aggregated_errors[node_name])
        except Exception:
            pass
    
    # Source 2: Individual node error file
    node_file = f"test_output/errors_{node_name.replace(' ', '_')}.json"
    if os.path.exists(node_file):
        try:
            with open(node_file, 'r') as f:
                node_errors = json.load(f)
                all_errors.update(node_errors)
        except Exception:
            pass
    
    # Source 3: In-memory error stats (if available)
    try:
        from tests.testnet.stats_tracker import error_stats
        if node_name in error_stats:
            all_errors.update(error_stats[node_name])
    except ImportError:
        pass
    
    return all_errors

def pytest_terminal_summary(terminalreporter, exitstatus, config):
    """Generate a comprehensive test summary at the end"""
    print("\n" + "="*80)
    print("🎯 COMPREHENSIVE TEST SUMMARY")
    print("="*80)
    
    # Wait a moment for any pending file writes
    time.sleep(1)
    
    # Get all test nodes from the environment
    node_to_test = os.getenv("NODE_TO_TEST")
    
    if node_to_test:
        # Test specific nodes
        nodes_to_check = [node.strip() for node in node_to_test.split(",")]
    else:
        # Check all possible nodes
        nodes_to_check = [
            "Node 01", "Node 04", "Node 05", "Node 06", "Node 07", "Node 08", 
            "Node 09", "Node 10", "Node 13", "Node 14", "Node 21", "Node 23", "Node 37"
        ]
    
    # Get global stats
    global_stats_file = "test_output/global_stats.json"
    global_stats = {}
    if os.path.exists(global_stats_file):
        try:
            with open(global_stats_file, 'r') as f:
                global_stats = json.load(f)
        except Exception:
            pass
    
    # Process each node
    for node_name in nodes_to_check:
        print(f"\n🔧 {node_name}")
        
        # Get errors for this node
        errors = get_error_breakdown(node_name)
        
        if errors:
            for error_key, count in errors.items():
                print(f"  • {count}x {error_key}")
        else:
            print("  • No errors")
        
        # Get performance stats if available
        for blockchain, nodes in global_stats.items():
            if node_name in nodes:
                node_stats = nodes[node_name]
                print(f"  📊 Performance:")
                print(f"    - Publish: {node_stats.get('publish_success', 0)}/{node_stats.get('publish_success', 0) + node_stats.get('publish_failed', 0)}")
                print(f"    - Query: {node_stats.get('query_success', 0)}/{node_stats.get('query_success', 0) + node_stats.get('query_failed', 0)}")
                print(f"    - Local Get: {node_stats.get('local_get_success', 0)}/{node_stats.get('local_get_success', 0) + node_stats.get('local_get_failed', 0)}")
                print(f"    - Remote Get: {node_stats.get('remote_get_success', 0)}/{node_stats.get('remote_get_success', 0) + node_stats.get('remote_get_failed', 0)}")
                break
    
    print(f"\n⏰ Summary generated at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80)