import os

def setup_project():
    os.system("powershell -ExecutionPolicy Bypass -File .tools/setup.ps1")

def run_pytest():
    os.system("pytest")

def run_pylint():
    os.system("pylint src/")

def build_package():
    os.system("python -m build ./src")

MENU_ITEMS: list[dict] = [
    {"name": "Run Setup", "action": setup_project}
    , {"name": "Run PyLint", "action": run_pylint}
    , {"name": "Run PyTest", "action": run_pytest}
    , {"name": "Build Package", "action": build_package}
] if os.path.isdir(".venv") else [{"name": "Run Setup", "action": setup_project}]

def run_option(index: int):
    if index < 0 or index > len(MENU_ITEMS) - 1:
        raise IndexError(index)
    item = MENU_ITEMS[index]

    if not isinstance(item, dict):
        raise ValueError(item)

    action = item["action"]
    action()
    input("Complete! press Enter to continue")

def print_items():
    for i, item in enumerate(MENU_ITEMS):
        i = i + 1
        if not isinstance(item, dict):
            continue
        name: str = item["name"]
        print(f"- [{i}] {name}")

def main():
    while True:
        os.system("cls")
        print("=" * 40)
        print("Snowstream CLI Dev Menu")
        print("=" * 40)
        print_items()
        print("- [0] exit")
        resonse = input("\nSelect an option : ").strip()
        try:
            resonse = int(resonse)

            if resonse == 0:
                print("Exiting the menu...")
                break
            else:
                run_option(resonse - 1)
        except (ValueError, IndexError, KeyError, TypeError):
            print(f"Selection '{resonse}' is invalid")
            input("press enter to continue")
            continue

if __name__ == "__main__":
    main()
