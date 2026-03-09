pip uninstall -y snowstream-cli
python -m build ./src
pip install -e src
