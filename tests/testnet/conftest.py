# tests/testnet/conftest.py

import sys
import importlib

def pytest_sessionfinish(session, exitstatus):
    # Dynamically import the module to avoid relative import issues
    try:
        neuroweb_testnet = importlib.import_module("tests.testnet.Neuroweb_Testnet")
    except ModuleNotFoundError:
        print("❌ Could not import Neuroweb_Testnet.py")
        return

    error_stats = getattr(neuroweb_testnet, "error_stats", {})
    global_stats = getattr(neuroweb_testnet, "global_stats", {})

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


