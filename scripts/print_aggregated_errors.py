import os
import json

ERROR_DIR = "test_output"  # or "." if your files are in the current folder

def load_error_files():
    return [
        f for f in os.listdir(ERROR_DIR)
        if f.startswith("errors_Node_") and f.endswith(".json")
    ]

def print_error_summary():
    print("\n\n📊 Global Error Summary:\n")

    error_files = load_error_files()

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

if __name__ == "__main__":
    print_error_summary()
