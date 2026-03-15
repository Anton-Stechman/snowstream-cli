import os
import subprocess
import re

def version_gte(new_version: str, current_version: str) -> bool:
    """
    Compare two semantic version strings and return True if new_version >= current_version.

    ### Inputs
        - new_version `<type=str>`: The new version string to compare (e.g. `"1.2.3"`).
        - current_version `<type=str>`: The current version string to compare against (e.g. `"1.2.1"`).

    ### Returns
        `bool`: `True` if `new_version` is greater than or equal to `current_version`, `False` otherwise.

    ### Raises
        - `ValueError`: If either version string is not a valid semantic version.
    """
    try:
        new = tuple(int(x) for x in new_version.split("."))
        current = tuple(int(x) for x in current_version.split("."))
    except (ValueError, AttributeError) as ex:
        raise ValueError(f"Invalid version string: {ex}") from ex
    return new >= current

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
    ["git", "log", "origin/main", "--pretty=%B", "--reverse"]
    , capture_output=True
    , text=True
)

commit_messages = result.stdout.splitlines()

# Append PR title from env var
pr_title = os.environ.get("PR_TITLE", "")
write_to_file: bool = os.environ.get("WRITE_VERSION", "true").upper() == "TRUE"

if pr_title:
    commit_messages.append(pr_title)

for msg in commit_messages:
    msg = msg.strip()
    new_version = f"{major}.{minor}.{patch}"
    if re.match(r"BREAKING-CHANGE:", msg, flags=re.IGNORECASE):
        major += 1
        minor = 0
        patch = 0
        print(f"Commit: {msg} (v{current_version} => v{new_version})")
    elif re.match(r"FEATURE:", msg, flags=re.IGNORECASE):
        minor += 1
        patch = 0
        print(f"Commit: {msg} (v{current_version} => v{new_version})")
    elif re.match(r"PATCH:", msg, flags=re.IGNORECASE):
        patch += 1
        print(f"Commit: {msg} (v{current_version} => v{new_version})")

new_version = f"{major}.{minor}.{patch}"
if not version_gte(new_version, current_version):
    new_version = current_version
version_summary = f"{current_version} => {new_version}"
new_content = re.sub(r'version = ".*"', f'version = "{new_version}"', content)

if write_to_file:
    with open(VERSION_FILE, "w", encoding="utf-8") as f:
        f.write(new_content)

print(f"Updated version to {new_version} in {VERSION_FILE}")

# write to GitHub env file
with open(os.environ["GITHUB_OUTPUT"], "a") as f:
    f.write(f"version_summary={version_summary}\n")
    f.write(f"new_version={new_version}\n")
