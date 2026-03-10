import os
import subprocess
import re

# Get branch name from environment or default to main
branch = os.environ.get("GITHUB_REF", "main").split("/")[-1]

# Get all PR commit messages for the branch
git_log_cmd = [
    "git", "log", branch, "--pretty=%B"
]
result = subprocess.run(git_log_cmd, capture_output=True, text=True)
commit_messages = result.stdout.splitlines()

major, minor, patch = 0, 0, 0

for msg in commit_messages:
    msg = msg.strip()
    if re.match(r"^BREAKING-CHANGE", msg):
        major += 1
        minor = 0
        patch = 0
    elif re.match(r"^FEATURE", msg):
        minor += 1
        patch = 0
    elif re.match(r"^PATCH", msg):
        patch += 1

version = f"{major}.{minor}.{patch}"
print(f"Calculated version: {version}")

# Optionally update pyproject.toml
pyproject_path = os.path.join("src", "pyproject.toml")
if os.path.exists(pyproject_path):
    with open(pyproject_path, "r", encoding="utf-8") as f:
        content = f.read()
    content = re.sub(r'version = ".*"', f'version = "{version}"', content)
    with open(pyproject_path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"Updated version in {pyproject_path}")
