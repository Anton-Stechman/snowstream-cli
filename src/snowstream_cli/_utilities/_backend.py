import os
import re
import json
from enum import Enum
from importlib.resources import files
from typing import Literal, Any, Callable
import yaml
import toml
from colorama import Fore, Style, init as colorama_init

colorama_init(autoreset=True)

COLOR_OPTIONS: dict = {
    "info": Fore.WHITE
    , "warning": Fore.YELLOW
    , "error": Fore.RED
    , "success": Fore.GREEN
}

class MessageType(Enum):
    INFO = "info"
    WARN = "warning"
    ERROR = "error"
    SUCCESS = "success"

    def __str__(self):
        return str(self.value)

    def color(self):
        return COLOR_OPTIONS[self.value]

class DirectoryNotFoundError(FileNotFoundError):
    """
    Raised when a target directory does not exist and auto-creation is not enabled.

    ### Inherits
        - `FileNotFoundError`
    """
    def __init__(self, *args):
        super().__init__(*args)

class SnowstreamInternalError(TypeError, ValueError, Exception):
    """
    Raised when an internal Snowstream error occurs, typically due to an unexpected type or value.

    ### Inherits
        - `TypeError`
        - `ValueError`
        - `Exception`
    """
    def __init__(self, *args):
        super().__init__(*args)

class InvalidInput(Exception):
    """
    Raised when a user provides an invalid input value.

    ### Inherits
        - `Exception`
    """
    def __init__(self, *args):
        super().__init__(*args)

def dir_exists(directory: str | None = None) -> bool:
    """
    Check if a directory exists at the given path.

    ### Inputs
        - directory (optional) `<type=str | None>` <default=`None`>: Path to the directory to check. Returns `False` if `None` or empty.

    ### Returns
        `bool`: `True` if the directory exists, `False` otherwise.

    ### Raises
        None
    """
    if not directory:
        return False
    return os.path.isdir(directory)

def header(text: str) -> str:
    """
    Uniformed CLI menu header

    ### Inputs
        - text `<type=str>`: Header text to be displayed in the terminal

    ### Returns
        `str`: fomratted string for printing in the terminal

    ### Raises
        None
    """
    banner: str = "=" * 40
    return f"{banner}\n{text}\n{banner}"

def file_exists(*args, filepath: str | None = None) -> bool:
    """
    Check if a file exists at the given path.

    ### Inputs
        - *args `<type=str>`: Path components to join into a full filepath (e.g. `"path/to"`, `"file.txt"`).
        - filepath (optional) `<type=str | None>` <default=`None`>: Final path component or standalone filepath. If provided, appended to any `*args` components.

    ### Returns
        `bool`: `True` if the file exists, `False` otherwise.

    ### Raises
        None
    """
    filepath = os.path.join(*args, filepath) if filepath else os.path.join(*args)
    if not filepath:
        return False
    return os.path.isfile(filepath)

def get_abs_path(directory: str, auto_create: bool = False) -> str:
    """
    Resolve the absolute path of a directory, optionally creating it if it does not exist.

    ### Inputs
        - directory `<type=str>`: Path to the directory to resolve.
        - auto_create (optional) `<type=bool>` <default=`False`>: When `True`, the directory will be created if it does not exist.

    ### Returns
        `str`: The absolute path of the directory.

    ### Raises
        - `DirectoryNotFoundError`: If the directory does not exist and `auto_create` is `False`.
    """
    if not dir_exists(directory):
        if not auto_create:
            raise DirectoryNotFoundError(f"{directory} is not a valid path, please use --auto-create")
        os.makedirs(directory, exist_ok=True)
        return get_abs_path(directory)
    return os.path.abspath(directory)

def terminal_print(*args: str, message_type: MessageType = MessageType.INFO) -> None:
    """
    Print formatted messages to the terminal with colorama colour coding.

    ### Inputs
        - *args `<type=str>`: One or more messages to print. Each arg is printed on a new line.
        - message_type (optional) `<type=MessageType>` <default=`MessageType.INFO`>: Controls the colour of the output. `"info"` prints white, `"warning"` yellow, `"error"` red, `"success"` green.

    ### Returns
        `None`

    ### Raises
        - `SnowstreamInternalError`: If `message_type` is not a valid key in the colour options map.
    """
    for arg in args:
        print(f"{message_type.color()}{arg}{Style.RESET_ALL}")
    return None

def save_file(*args: str, content: Any, auto_create: bool = True, parser: Callable = str) -> bool:
    """
    Write content to a file at the given path, optionally creating the directory if it does not exist.

    ### Inputs
        - *args `<type=str>`: Path components to join into a full filepath (e.g. `"path/to"`, `"file.json"`).
        - content `<type=Any>`: The content to write to the file. Will be serialised using `parser` before writing.
        - auto_create (optional) `<type=bool>` <default=`True`>: When `True`, the parent directory will be created if it does not exist.
        - parser (optional) `<type=Callable>` <default=`str`>: A callable used to serialise `content` before writing (e.g. `json.dumps`, `yaml.dump`). Defaults to `str`.

    ### Returns
        `bool`: `True` if the file was written successfully, `False` otherwise.

    ### Raises
        - `DirectoryNotFoundError`: If the parent directory does not exist and `auto_create` is `False`.
    """
    try:
        filepath: str = os.path.join(*args)
        parent: str = os.path.dirname(filepath)
        if not dir_exists(parent):
            if not auto_create:
                raise DirectoryNotFoundError(f"{parent} does not exist, use auto_create=True to create it")
            os.makedirs(parent, exist_ok=True)
        if isinstance(content, dict):
            if parser in (json.dumps, yaml.dump, toml.dumps):
                serialised: str = parser(content)
            else:
                serialised: str = parser(content)  # trust the caller
        else:
            serialised: str = parser(content)
        with open(filepath, "w") as f:
            f.write(serialised)
        return True
    except DirectoryNotFoundError:
        raise
    except Exception:
        return False

def terminal_prompt(
        prompt: str
        , expected_type: type = str
        , expected_values: list[str] = ["y", "n"]
        , case: Callable = str.lower
        , message_type: MessageType = MessageType.INFO
        , on_error: Literal["raise", "ignore"] = "raise") -> Any:
    """
    Display a coloured terminal prompt and return a validated user response.

    ### Inputs
        - prompt `<type=str>`: The message displayed to the user before the input cursor.
        - expected_type (optional) `<type=type>` <default=`str`>: The expected type of the response. If the raw input is not of this type, a cast is attempted.
        - expected_values (optional) `<type=list[str]>` <default=`["y", "n"]`>: Allowlist of valid responses. If the response is not in this list, `InvalidInput` is raised.
        - case (optional) `<type=Callable>` <default=`str.lower`>: A string method applied to the raw input before validation (e.g. `str.lower`, `str.upper`).
        - message_type (optional) `<type=Literal["info", "warning", "error", "success"]>` <default=`"info"`>: Controls the colour of the prompt text.

    ### Returns
        `Any`: The validated and type-coerced user response.

    ### Raises
        - `InvalidInput`: If the response cannot be coerced to `expected_type`, or if the response is not in `expected_values`.
        - `SnowstreamInternalError`: If `message_type` is not a valid key in the colour options map.
    """
    response = input(f"{message_type.color()}{prompt}: {Style.RESET_ALL}").strip()
    response = case(response)
    if not isinstance(response, expected_type) and on_error == "raise":
        try:
            response = expected_type(response)
        except (ValueError, Exception) as ex:
            raise InvalidInput(f"Excepted type {expected_type} for value {response}, got {type(response)}")
    if response not in [case(v) for v in expected_values] and on_error == "raise":
        raise InvalidInput(f"Excepted values {expected_values} got {response}")
    return response

def get_file(*args: str, parser: Callable = str, internal: bool = True) -> Any:
    """
    Read a file and return its content.

    ### Inputs
        - *args `<type=str>`: Path components to the target file. If `internal=True`, paths are relative to the `snowstream_cli` package root (e.g. `"templates"`, `"structure.yml"`). If `internal=False`, components are joined as a standard filesystem path.
        - parser (optional) `<type=Callable>` <default=`str`>: A callable applied to the raw file content before returning. Use `yaml.safe_load` for YAML, `json.loads` for JSON, etc.
        - internal (optional) `<type=bool>` <default=`True`>: When `True`, resolves the path relative to the `snowstream_cli` package root. When `False`, resolves as an absolute or relative filesystem path.

    ### Returns
        `Any`: The file content after applying `parser`.

    ### Raises
        - `FileNotFoundError`: If the resolved path does not exist.
    """
    if internal:
        content = files("snowstream_cli").joinpath(*args).read_text()
    else:
        path: str = os.path.join(*args)
        with open(path, "r") as f:
            content = f.read()
    return parser(content)

def resolve_template_placeholders(content: str) -> str:
    """
    Detect and resolve {{ placeholder }} values in a template string via user prompts.

    ### Inputs
        - content `<type=str>`: Raw template string containing zero or more `{{ placeholder }}` tokens.

    ### Returns
        `str`: The template string with all `{{ placeholder }}` tokens replaced by user-provided values or `null`.

    ### Raises
        None
    """
    placeholders: list[str] = re.findall(r"\{\{\s*([\w\-]+)\s*\}\}", content)

    if not placeholders:
        return content

    terminal_print("Template requires the following values (press Enter to skip):", message_type=MessageType.INFO)

    resolved: dict[str, str] = {}
    for placeholder in list(set(placeholders)):
        if placeholder in resolved:
            continue
        raw = terminal_prompt(placeholder, on_error="ignore", case=lambda x: x)
        resolved[placeholder] = raw if raw else "null"

    # replace {{ placeholder }} in content with resolved value
    for placeholder, value in resolved.items():
        content = content.replace(concatenate("{{", placeholder, "}}", sep=" "), value)
        content = content.replace(concatenate("{{", placeholder, "}}"), value)

    return content  # returned content has no {{ }} tokens remaining

def concatenate(*args: Any, sep: str | None = None) -> str:
    """
    Join a sequence of strings with an optional separator.

    ### Inputs
        - *args `<type=Any>`: One or more values to join. Each value will be coerced to `str`.
        - sep (optional) `<type=str | None>` <default=`None`>: Separator to insert between each string. If `None` or not provided, strings are joined with no separator.

    ### Returns
        `str`: The concatenated string.

    ### Raises
        None
    """
    sep = sep if sep else ""
    return sep.join([str(arg) for arg in args])
