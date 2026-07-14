"""
Core CLI handlers for the Snowstream CLI.

This module provides the implementation of the `version`, `init`, `manifest`, and `run`
commands exposed by the `snowstream` console script.
"""

import inspect
import json
import os
import shutil
from typing import Generator, Literal, Callable
from importlib.metadata import metadata

import toml
import yaml

from snowstream_cli._backend._deploy import generate_manifest
from snowstream_cli._backend._util import (
    dir_exists
    , is_cwd
    , save_file
    , header
    , get_abs_path
    , get_project_dir
    , terminal_prompt
    , get_file
    , get_scaffold
    , is_valid_snowstream_project
    , resolve_template_placeholders
    , MessageType
)

def _cli_header(func: Callable, frame) -> Generator:
    """
    Yield a formatted parameter summary and begin marker for a CLI handler.

    ### Inputs
        - func `<type=Callable>`: The handler function whose signature will be introspected to list parameter names.
        - frame `<type=FrameType>`: The current stack frame of the calling function, used to resolve live parameter values via `f_locals`.

    ### Returns
        `Generator`: Yields `tuple[str, MessageType]` pairs — one per parameter, followed by a begin marker and separator line.

    ### Raises
        None
    """
    caller_locals = frame.f_locals
    yield f"> cmd: {func.__name__}", MessageType.INFO
    for name in inspect.signature(func).parameters:
        yield f">> {name}: {caller_locals.get(name)}", MessageType.INFO
    yield "\nBegin...", MessageType.INFO
    yield "=" * 30, MessageType.INFO

def version(verbose: bool = False) -> Generator:
    """
    Display the installed version of snowstream-cli.

    ### Inputs
        - verbose (optional) `<type=bool>` <default=`False`>: When `True`, displays additional package metadata.

    ### Returns
        `Generator`: Yields `tuple[str, MessageType]` pairs.

    ### Raises
        None
    """
    yield header("Displaying Version: snowstream-cli"), MessageType.INFO
    yield from _cli_header(version, inspect.currentframe())

    meta = metadata("snowstream-cli")
    if verbose:
        yield f"Name:     {meta['Name']}", MessageType.INFO
        yield f"Summary:  {meta['Summary']}", MessageType.INFO
        yield f"Version:  {meta['Version']}", MessageType.INFO
        yield f"Python:   {meta['Requires-Python']}", MessageType.INFO
        yield f"Author:   {meta['Author-email']}", MessageType.INFO
        yield f"License:  {meta['License-Expression']}", MessageType.INFO
        return
    yield f"snowstream-cli v{meta['Version']}", MessageType.INFO

def initialise(force: bool | None = None, project_dir: str | None = None) -> Generator:  # pylint: disable=too-many-branches,too-many-statements
    """
    Initialise new snowstream project

    ### Inputs
        - force (optional) `<type=bool | None>` <default=`None`>: When `True` existing directory will be overwritten without prompting. When `False` or `None` user is prompted before overwriting.
        - project_dir (optional) `<type=str | None>` <default=`None`>: Target directory path.

    ### Returns
        `Generator`: Yields `tuple[str, MessageType]` pairs.

    ### Raises
        - `ValueError`: If no value is provided for `project_dir`.
    """
    if not project_dir:
        raise ValueError("No value provided for parameter `project_dir`")
    yield header("Initialising New Snowstream Project"), MessageType.INFO
    yield from _cli_header(initialise, inspect.currentframe())
    if dir_exists(project_dir) and not is_cwd(project_dir):
        if force:
            shutil.rmtree(project_dir)
        else:
            response: str = terminal_prompt(
                f"Directory {project_dir} already exists. Overwrite? [Y/N]"
                , expected_values=["y", "n"]
                , message_type=MessageType.WARN
            )
            if response == "n":
                yield f"'{response}' selected, cannot resume initialisation", MessageType.WARN
                return
            shutil.rmtree(project_dir)

    fullpath: str = get_abs_path(project_dir, True)
    gitignore_entries: list[str] = []

    def __process_node(node: dict, current_path: str) -> Generator:
        type_extensions: dict[str, str | None] = {
            "yaml": "yml"
            , "toml": "toml"
            , "json": "json"
            , "text": None
        }

        # process files
        for file in node.get("files") or []:
            if not isinstance(file, dict):
                continue
            file_name: str = file["name"]
            file_type: str = file.get("type")
            template_name: str = file.get("template")

            ext = type_extensions.get(file_type)
            if ext:
                full_name = f"{file_name}.{ext}"
            else:
                full_name = file_name

            file_path = os.path.join(current_path, full_name)

            if template_name:
                content = get_file("templates", "files", template_name)
                if file_type in ["yaml", "toml"]:
                    content = resolve_template_placeholders(content)
            else:
                content = ""

            with open(file_path, "w",encoding="utf-8") as f:
                if file_type == "yaml":
                    yaml.dump(yaml.safe_load(content), f, sort_keys=False)
                elif file_type == "toml":
                    toml.dump(toml.loads(content), f)
                elif file_type == "json":
                    json.dump(json.loads(content), f, indent=4)
                else:
                    f.write(content)

            yield f"  [file] {file_path}", MessageType.SUCCESS

            if file.get("git-ignore"):
                gitignore_entries.append(os.path.relpath(file_path, fullpath))

        # process folders
        for folder in node.get("folders") or []:
            folder_name: str = folder["name"]
            folder_path = os.path.join(current_path, folder["name"])
            os.makedirs(folder_path, exist_ok=True)
            yield f"  [dir]  {folder_path}", MessageType.SUCCESS

            if folder.get("git-ignore"):
                gitignore_entries.append(f"*{folder_name}/")

            yield from __process_node(folder, folder_path)

    scaffold: dict = get_scaffold("root")
    yield from __process_node(scaffold, fullpath)

    # write .gitignore once after full tree is processed
    gitignore_path = os.path.join(fullpath, ".gitignore")
    if os.path.exists(gitignore_path):
        with open(gitignore_path, "r", encoding="utf-8") as f:
            gitignore_content = f.read()
        ignore_block = "\n".join(gitignore_entries)
        gitignore_content = gitignore_content.replace("{{ ignore }}", ignore_block)
        with open(gitignore_path, "w", encoding="utf-8") as f:
            f.write(gitignore_content)
        yield f"  [.gitignore] updated with {len(gitignore_entries)} entries", MessageType.INFO

    yield f"Project initialised at: {fullpath}", MessageType.SUCCESS
    return

def manifest(project_dir: str | None = None, target_app: str | None = None, call_type: Literal["cli", "internal"] = "cli") -> Generator:
    """
    Generate a manifest.json file for the given project directory and target app.

    ### Inputs
        - project_dir (optional) `<type=str | None>` <default=`None`>: Path to the project directory. Defaults to the current working directory if not provided.
        - target_app (optional) `<type=str | None>` <default=`None`>: The target app to generate the manifest for. Defaults to `"all"` if not provided.
        - call_type (optional) `<type=Literal["cli", "internal"]>` <default=`"cli"`>: When `"cli"`, a formatted header and input summary are yielded before processing.
            When `"internal"`, output is suppressed and only manifest data and errors are yielded.

    ### Returns
        `Generator`: Yields `tuple[str, MessageType]` pairs.

    ### Raises
        - `TypeError`: If `generate_manifest` does not return a `dict` as its final response.
    """
    project_dir = get_project_dir(project_dir)
    target_app = target_app or "all"
    manifest_data: dict | None = None
    if call_type == "cli":
        yield header("Generating manifest.json"), MessageType.INFO
        yield from _cli_header(manifest, inspect.currentframe())

    for response, status in generate_manifest(project_dir, target_app):
        if isinstance(response, dict):
            manifest_data = response
            break
        if not isinstance(status, MessageType) or not isinstance(response, str):
            yield f"ERROR: Unexpected Response Signature. Expected <{str}, {MessageType}> got <{type(response)}, {type(status)}>", MessageType.ERROR
            return
        yield response, status

    manifest_path = os.path.join(project_dir, ".manifest")
    if not manifest_data:
        # yield f"No apps found in project {project_dir}\\", MessageType.INFO
        return
    if not isinstance(manifest_data, dict):
        raise TypeError(f"expected type {dict} got {type(manifest_data)} for {manifest_data}")

    if save_file(manifest_path, "manifest.json", content=manifest_data, parser=lambda x: json.dumps(x, indent=4)):
        yield f"Manifest Created at {manifest_path}", MessageType.SUCCESS
        return

    yield f"ERROR: Failed to create manifest in directory {manifest_path}", MessageType.ERROR

def run(project_dir: str | None = None, target_app: str | None = None, target: Literal["dev", "test", "prod"] = "dev") -> Generator:
    """
    Run a Snowstream build for the given project directory, target app, and target environment.

    ### Inputs
        - project_dir (optional) `<type=str | None>` <default=`None`>: Path to the project directory. Defaults to the current working directory if not provided.
        - target_app (optional) `<type=str | None>` <default=`None`>: The app to build. Defaults to `"all"` if not provided.
        - target (optional) `<type=Literal["dev", "test", "prod"]>` <default=`"dev"`>: The target environment to build against.

    ### Returns
        `Generator`: Yields `tuple[str, MessageType]` pairs.

    ### Raises
        None
    """
    project_dir = get_project_dir(project_dir)
    target_app = target_app or "all"

    yield header("Running Snowstream build"), MessageType.INFO
    yield from _cli_header(run, inspect.currentframe())
    yield f"Build Target={target}", MessageType.INFO
    if not is_valid_snowstream_project(project_dir):
        yield f"ERROR: could not find snowstream project in {project_dir}", MessageType.ERROR
        yield "Run: 'snowstream init' to create a new project", MessageType.WARN
        return
    yield "Building manifest.json", MessageType.INFO
    for response, status in manifest(project_dir, target_app, "internal"):
        yield response, status
    yield "Complete!", MessageType.SUCCESS
