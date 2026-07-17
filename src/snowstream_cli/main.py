"""
Entrypoint module for the Snowstream CLI.

This module is responsible for parsing command-line arguments and dispatching
commands to the underlying Snowstream CLI handlers.

Available commands:
- init: scaffold a new Snowstream project
- manifest: generate a snowstream_manifest.json for a project
- run: validate and build a target environment manifest
"""

import os
import json
import subprocess
import argparse
from snowstream_cli._cli._handlers import initialise, run, manifest, version
from snowstream_cli._backend._util import terminal_print, get_file, MessageType

COMMAND_MAPPING: dict = {
    "function": {
        "initialise": initialise
        , "run": run
        , "manifest": manifest
        , "version": version
    }
    , "defaults": {
        "cwd": os.getcwd
    }
    , "types": {
        "str": str
        , "bool": bool
        , "int": int
        , "list": list
        , "dict": dict
    }
}


def main() -> None:
    """
    Dynamic CLI handler using commands.json metadata
    """
    def __get_arg(arg: dict | None) -> tuple:
        if not arg or not isinstance(arg, dict):
            return [], {}
        arg_names = [arg["name"]]
        if "aliases" in arg:
            arg_names += arg["aliases"]
        arg_kwargs = {k: v for k, v in arg.items() if k not in ("name", "aliases")}
        # Handle type and default special cases
        if "type" in arg_kwargs:
            arg_kwargs["type"] = COMMAND_MAPPING["types"].get(arg_kwargs["type"], str)
        if "default" in arg_kwargs and isinstance(arg_kwargs["default"], str):
            _resolved = COMMAND_MAPPING["defaults"].get(arg_kwargs["default"], arg_kwargs["default"])
            arg_kwargs["default"] = _resolved() if callable(_resolved) else _resolved
        return arg_names, arg_kwargs

    command_metadata = get_file("data", "commands.json", parser=json.loads)
    subprocess.run(["cls"], check=True, shell=True)
    parser = argparse.ArgumentParser(
        prog="snowstream"
        , description="Snowstream CLI"
    )
    subparsers = parser.add_subparsers(dest="command")

    # Build subparsers and arguments from metadata
    for cmd in command_metadata:
        if not isinstance(cmd, dict):
            continue
        subparser = subparsers.add_parser(cmd["command"], help=cmd.get("help", ""))
        for arg in cmd.get("arguments", []):
            arg_names, arg_kwargs = __get_arg(arg)
            subparser.add_argument(*arg_names, **arg_kwargs)
    args = parser.parse_args()

    for command in command_metadata:
        if not isinstance(command, dict):
            terminal_print(
                "Warning: Internal Process error"
                , f"Expected type {dict}, got {type(command)} for value {command}"
                , message_type=MessageType.WARN
            )
            continue
        if args.command == command["command"]:
            func = COMMAND_MAPPING["function"][command["func"]]
            for response, status in func(**{k: v for k, v in vars(args).items() if k != "command"}):
                terminal_print(response, message_type=status)
            return

    # Dispatch to the correct handler
    if args.command is None:
        parser.print_help()
        return




def deprecated_main() -> None:
    """
    Main CLI handler
    """
    subprocess.run(["cls"], check=True, shell=True)
    parser = argparse.ArgumentParser(
        prog="snowstream"
        , description="Snowstream CLI"
    )

    subparsers = parser.add_subparsers(dest="command")

    init_parser = subparsers.add_parser("init", help="Initialise a new snowstream project")
    run_parser = subparsers.add_parser("run", help="Run a build")
    manifest_parser = subparsers.add_parser("manifest", help="Generate snowstream manifest")
    version_parser = subparsers.add_parser("version", help="Display library version")

    init_parser.add_argument(
        "--force"
        , action="store_true"
        , default=False
        , help="Overwrite existing project without prompting"
    )

    init_parser.add_argument(
        "--project-dir"
        , type=str
        , default=os.getcwd()
        , metavar="PATH"
        , help="Target directory to initialise project in (default: current directory)"
    )

    run_parser.add_argument(
        "--project-dir"
        , type=str
        , default=os.getcwd()
        , metavar="PATH"
        , help="Path to the snowstream project directory (default: current directory)"
    )

    run_parser.add_argument(
        "--app"
        , type=str
        , default=None
        , help="Target app to run (default: all)"
    )

    run_parser.add_argument(
        "--target"
        , type=str
        , default="dev"
        , choices=["dev", "test", "prod"]
        , help="Target environment (default: dev)"
    )

    manifest_parser.add_argument(
        "--project-dir"
        , type=str
        , default=os.getcwd()
        , metavar="PATH"
        , help="Path to the snowstream project directory (default: current directory)"
    )

    manifest_parser.add_argument(
        "--app"
        , type=str
        , default=None
        , help="Target app to generate manifest for (default: all)"
    )

    version_parser.add_argument(
        "--verbose", "-v"
        , action="store_true"
        , default=False
        , help="Display verbose version information"
    )

    args = parser.parse_args()

    if args.command == "version":
        for message, status in version(
            verbose=args.verbose
        ):
            terminal_print(message, message_type=status)
    elif args.command == "init":
        for message, status in initialise(
            force=args.force
            , project_dir=args.project_dir
        ):
            terminal_print(message, message_type=status)
    elif args.command == "run":
        for message, status in run(
            project_dir=args.project_dir
            , target_app=args.app
            , target=str(args.target).lower()
        ):
            terminal_print(message, message_type=status)
    elif args.command == "manifest":
        for message, status in manifest(
            project_dir=args.project_dir
            , target_app=args.app
            , call_type="cli"
        ):
            terminal_print(message, message_type=status)
    elif args.command is None:
        parser.print_help()
