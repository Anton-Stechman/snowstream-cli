import os
import subprocess

PYEXE: str = r".venv\Scripts\python.exe"

def setup_project():
    subprocess.run("powershell -ExecutionPolicy Bypass -File .tools/setup.ps1", shell=True)
    subprocess.run([PYEXE, "-m", "pip", "install", "-e", "./src"], check=True)

def run_pytest():
    subprocess.run([PYEXE, "-m", "pytest"], check=True)

def run_pylint():
    subprocess.run([PYEXE, "-m", "pylint src/"], check=True)

def build_package():
    subprocess.run([PYEXE, "-m", "python -m build ./src"], check=True)

MENU_ITEMS: list[dict] = [
    {"name": "Run Setup", "action": setup_project}
    , {"name": "Run PyLint", "action": run_pylint}
    , {"name": "Run PyTest", "action": run_pytest}
    , {"name": "Build Package", "action": build_package}
] if os.path.isdir(".venv") else [{"name": "Run Setup", "action": setup_project}]

# If project has not been initialised yet - force user to initialise
ACCESSABLE_MENU_ITEMS: list[dict] = (
    MENU_ITEMS if os.path.isdir(".venv")
    else [MENU_ITEMS[0]]
)

def run_option(index: int):
    if index < 0 or index > len(ACCESSABLE_MENU_ITEMS) - 1:
        raise IndexError(index)
    item = ACCESSABLE_MENU_ITEMS[index]

    if not isinstance(item, dict):
        raise ValueError(item)

    action = item["action"]
    action()
    input("Complete! press Enter to continue")

def print_items():
    for i, item in enumerate(ACCESSABLE_MENU_ITEMS):
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

            # Re-initialize menu if .venv now exists
            global ACCESSABLE_MENU_ITEMS
            if os.path.isdir(".venv"):
                ACCESSABLE_MENU_ITEMS = MENU_ITEMS
            continue

if __name__ == "__main__":
    main()
