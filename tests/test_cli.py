import os
from snowstream_cli._cli._handlers import initialise
from unittest.mock import patch
# Helper to check directory structure recursively

def assert_scaffold_structure(base_dir):
    # .gitignore
    assert (base_dir / ".gitignore").is_file()
    # .locals/profile.yml
    assert (base_dir / ".locals" / "profile.yml").is_file()
    # .manifest (directory)
    assert (base_dir / ".manifest").is_dir()
    # snowstream/project.yml
    assert (base_dir / "snowstream" / "project.yml").is_file()
    # snowstream/apps (directory)
    assert (base_dir / "snowstream" / "apps").is_dir()


def test_initialise_creates_scaffold(tmp_path):
    project_dir = tmp_path / "myproj"
    assert not project_dir.exists()
    with patch("builtins.input", return_value=""):
        for _ in initialise(project_dir=str(project_dir), force=True):
            pass
    scaffold_root = project_dir / "snowstream"
    assert scaffold_root.exists() and scaffold_root.is_dir()
    assert_scaffold_structure(scaffold_root)

def test_initialise_overwrites_existing(tmp_path):
    project_dir = tmp_path / "myproj"
    os.makedirs(project_dir, exist_ok=True)
    dummy = project_dir / "snowstream"
    dummy.mkdir(parents=True, exist_ok=True)
    (dummy / "oldfile.txt").write_text("old")
    with patch("builtins.input", return_value=""):
        for _ in initialise(project_dir=str(project_dir), force=True):
            pass
    scaffold_root = project_dir / "snowstream"
    assert scaffold_root.exists() and scaffold_root.is_dir()
    assert_scaffold_structure(scaffold_root)
