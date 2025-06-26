import os
import json
import glob

ERROR_DIR = "test_output"


def safe_rate(success, fail):
    total = success + fail
    return round((success / total) * 100, 2) if total > 0 else 0.0


def avg(times):
    return round(sum(times) / len(times), 2) if times else 0.0


def print_summary_for_node():
    summary_file = os.path.join(ERROR_DIR, "global_stats.json")
    node_to_test = os.getenv("NODE_TO_TEST")

    if not os.path.exists(summary_file):
        print("⚠️ global_stats.json not found.")
        return

    try:
        with open(summary_file, "r") as f:
            summary_data = json.load(f)
    except Exception as e:
        print(f"⚠️ Failed to read global_stats.json: {str(e)}")
        return

    if not node_to_test:
        print("⚠️ NODE_TO_TEST not defined in environment.")
        return

    for blockchain, nodes in summary_data.items():
        if node_to_test not in nodes:
            continue
        node = nodes[node_to_test]
        print("\n\n📊 Global Publish Summary:\n")
        print(f"🔗 Blockchain: {blockchain}")
        print(f"  • {node_to_test}:")
        print(f"    🔸 Publish: ✅ {node['publish_success']} / ❌ {node['publish_failed']} -> {safe_rate(node['publish_success'], node['publish_failed'])}%")
        print(f"    🔸 Query:   ✅ {node['query_success']} / ❌ {node['query_failed']} -> {safe_rate(node['query_success'], node['query_failed'])}%")
        print(f"    🔸 Local Get: ✅ {node['local_get_success']} / ❌ {node['local_get_failed']} -> {safe_rate(node['local_get_success'], node['local_get_failed'])}%")
        print(f"    🔸 Get: ✅ {node['remote_get_success']} / ❌ {node['remote_get_failed']} -> {safe_rate(node['remote_get_success'], node['remote_get_failed'])}%")
        print(f"    ⏱️ Avg Publish Time: {avg(node['publish_times'])} seconds")
        print(f"    ⏱️ Avg Query Time: {avg(node['query_times'])} seconds")
        print(f"    ⏱️ Avg Local Get Time: {avg(node['local_get_times'])} seconds")
        print(f"    ⏱️ Avg Get Time: {avg(node['remote_get_times'])} seconds")


def print_error_for_node():
    print("\n📊 Error Breakdown by Node:\n")
    node_to_test = os.getenv("NODE_TO_TEST")
    if not node_to_test:
        print("⚠️ NODE_TO_TEST not defined in environment.")
        return

    error_file = os.path.join(ERROR_DIR, f"errors_{node_to_test.replace(' ', '_')}.json")
    if not os.path.exists(error_file):
        print(f"🔧 {node_to_test}\n  ✅ No errors\n")
        return

    try:
        with open(error_file, 'r') as f:
            node_errors = json.load(f)

        print(f"🔧 {node_to_test}")
        if not node_errors:
            print("  ✅ No errors\n")
        else:
            for error_key, count in node_errors.items():
                print(f"  • {count}x {error_key}")
        print()
    except Exception as e:
        print(f"⚠️ Failed to read or parse {error_file}: {str(e)}")


if __name__ == "__main__":
    print_summary_for_node()
    print_error_for_node()
