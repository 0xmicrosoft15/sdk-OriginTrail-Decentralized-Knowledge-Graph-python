# tests/testnet/conftest.py
import importlib
import os

def pytest_sessionfinish(session, exitstatus):
    # Try to get the test module path from any collected test item
    test_file = None
    for item in session.items:
        if item.location:
            test_file = item.location[0]  # Get the filename of the test
            break

    if not test_file:
        print("❌ Could not determine which test file ran.")
        return

    module_path = (
        test_file.replace("/", ".")
                 .replace("\\", ".")
                 .replace(".py", "")
    )

    try:
        test_module = importlib.import_module(module_path)
    except ModuleNotFoundError as e:
        print(f"❌ Could not import test module: {module_path}")
        print(e)
        return

    error_stats = getattr(test_module, "error_stats", {})
    global_stats = getattr(test_module, "global_stats", {})

    print("\n\n📊 Global Publish Summary:")

    for blockchain, node_data in global_stats.items():
        print(f"\n🔗 Blockchain: {blockchain}")
        total_success = 0
        total_failed = 0
        for node_name, results in node_data.items():
            s, f = results["success"], results["failed"]
            total_success += s
            total_failed += f
            rate = round(s / (s + f) * 100, 2)
            print(f"  • {node_name}: ✅ {s} / ❌ {f} ({rate}%)")

        total = total_success + total_failed
        total_rate = round(total_success / total * 100, 2) if total > 0 else 0
        print(f"  📦 TOTAL: ✅ {total_success} / ❌ {total_failed} -> {total_rate}%")

    print("\n📊 Error Breakdown by Node:")
    if not error_stats:
        print("✅ No errors recorded.")
    else:
        for node_name, errors in error_stats.items():
            print(f"\n🔧 {node_name}")
            for message, count in errors.items():
                print(f"  • {count}x {message}")



