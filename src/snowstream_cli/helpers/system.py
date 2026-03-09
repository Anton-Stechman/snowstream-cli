import os

class DirectoryNotFoundError(FileNotFoundError):
    def __init__(self, *args):
        super().__init__(*args)

def dir_exists(directory: str | None = None) -> bool:
    """
    Validate if a directory exisits
    """
    if not directory:
        return False
    return os.path.isdir(directory)

def get_abs_path(directory: str, auto_create: bool = False) -> str:
    """
    """
    if not dir_exists(directory):
        if not auto_create:
            raise DirectoryNotFoundError(f"{directory} is not a valid path, please use --auto-create")
        os.makedirs(directory, exist_ok=True)
        return get_abs_path(directory)
    return os.path.abspath(directory)
