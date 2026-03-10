import os
import subprocess
import re

# Get current version from pyproject.toml
VERSION_FILE = os.path.join("src", "pyproject.toml")
with open(VERSION_FILE, "r", encoding="utf-8") as f:
    content = f.read()
current_version = re.search(r'version = "(\d+)\.(\d+)\.(\d+)"', content)
if current_version:
    cv_major, cv_minor, cv_patch = map(int, current_version.groups())
else:
    cv_major, cv_minor, cv_patch = 0, 0, 0
current_version: str = f"{cv_major}.{cv_minor}.{cv_patch}"
major, minor, patch = 0, 0, 0

# Get all commit messages in the branch
result = subprocess.run(
    ["git", "log", "origin/main", "--pretty=%B"]
    , capture_output=True
    , text=True
)

commit_messages = result.stdout.splitlines()

# Append PR title from env var
pr_title = os.environ.get("PR_TITLE", "")
if pr_title:
    commit_messages.append(pr_title)

for msg in commit_messages:
    msg = msg.strip()
    if re.match(r"^BREAKING-CHANGE", msg, flags=re.IGNORECASE):
        major += 1
        minor = 0
        patch = 0
    elif re.match(r"^FEATURE", msg, flags=re.IGNORECASE):
        minor += 1
        patch = 0
    elif re.match(r"^PATCH", msg, flags=re.IGNORECASE):
        patch += 1
    print(f"Commit: {msg} (v{current_version} => v{major}.{minor}.{patch})")

new_version = f"{major}.{minor}.{patch}"
if major < cv_major:
    raise Exception(f"Incorrect Version Signature {new_version} < {current_version}")
if major == cv_major and minor < cv_minor:
    raise Exception(f"Incorrect Version Signature {new_version} < {current_version}")
if major == cv_major and minor == cv_minor and patch < cv_patch:
    raise Exception(f"Incorrect Version Signature {new_version} < {current_version}")

version_summary = f"{current_version} => {new_version}"
new_content = re.sub(r'version = ".*"', f'version = "{new_version}"', content)

with open(VERSION_FILE, "w", encoding="utf-8") as f:
    f.write(new_content)

print(f"Updated version to {new_version} in {VERSION_FILE}")

# write to GitHub env file
with open(os.environ["GITHUB_OUTPUT"], "a") as f:
    f.write(f"version_summary={version_summary}\n")
    f.write(f"new_version={new_version}\n")
