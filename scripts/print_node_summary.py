import os
import json

node_to_test = os.getenv("NODE_TO_TEST")

if not node_to_test:
    print("⚠️ NODE_TO_TEST environment variable is missing.")
    exit(1)

summary_file = f"test_output/summary_{node_to_test.replace(' ', '_')}.json"
error_file = f"test_output/errors_{node_to_test.replace(' ', '_')}.json"

print("\n📊 Global Publish Summary:\n")

if os.path.exists(summary_file):
    with open(summary_file) as f:
        summary = json.load(f)
    
    print(f"🔗 Blockchain: {summary['blockchain_name']}")
    print(f"  • {summary['node_name']}:")
    print(f"    🔸 Publish: ✅ {summary['success']} / ❌ {summary['failed']} -> {summary['publish_success_rate']}%")
    print(f"    🔸 Query:   ✅ {summary['query_success_rate']}%")
    print(f"    🔸 Local Get: ✅ {summary['publisher_get_success_rate']}%")
    print(f"    🔸 Get: ✅ {summary['non_publisher_get_success_rate']}%")
    print(f"    ⏱️ Avg Publish Time: {summary['average_publish_time']} seconds")
    print(f"    ⏱️ Avg Query Time: {summary['average_query_time']} seconds")
    print(f"    ⏱️ Avg Local Get Time: {summary['average_publisher_get_time']} seconds")
    print(f"    ⏱️ Avg Get Time: {summary['average_non_publisher_get_time']} seconds")
else:
    print(f"⚠️ Summary file not found: {summary_file}")

print("\n📊 Error Breakdown by Node:\n")

if os.path.exists(error_file):
    with open(error_file) as f:
        errors = json.load(f)

    print(f"🔧 {node_to_test}")
    if not errors:
        print("  ✅ No errors")
    else:
        for msg, count in errors.items():
            print(f"  • {count}x {msg}")
else:
    print(f"⚠️ Error file not found: {error_file}")