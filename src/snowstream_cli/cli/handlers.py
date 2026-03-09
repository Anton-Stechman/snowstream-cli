from snowstream_cli.helpers.system import dir_exists, get_abs_path

def initialise(auto_create: bool = False, force: bool | None = None, dir: str | None = None) -> None:
    """
    Initialise new snowstream project
    """
    print("Initialising New Snowstream Project")
    fullpath: str | None = None
    if dir_exists(dir) and not force:
        reponse: str = input(f"Directory {dir} already exists.. overwrite? [Y/N]: ").lower()
        if not isinstance(reponse, str):
            print(f"Invalid Reponse, expected type {str} got: {type(reponse)}")
            return None
        elif reponse not in ["y", "n"]:
            print(f"Invalid Reponse, expected 'Y' or 'N', got: {reponse}")
            return None
        if reponse == "n":
            return None
        fullpath = get_abs_path(dir, True)
    if not fullpath:
        fullpath = get_abs_path(dir, auto_create)
