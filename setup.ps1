C:\Users\astec\git\snowstream-cli\.venv\scripts\python.exe -m pip install --upgrade pip==25.3
pip uninstall -y snowstream-cli
python -m build ./src
pip install -e src
