import os
import subprocess
import argparse
from snowstream_cli._cli._handlers import initialise, run, manifest
from snowstream_cli._utilities._backend import terminal_print

def main() -> None:
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

    args = parser.parse_args()

    if args.command == "init":
        for message, status in initialise(force=args.force, project_dir=args.project_dir):
            terminal_print(message, message_type=status)
    elif args.command == "run":
        for message, status in run(project_dir=args.project_dir, target_app=args.app, target=str(args.target).lower()):
            terminal_print(message, message_type=status)
    elif args.command == "manifest":
        for message, status in manifest(project_dir=args.project_dir, target_app=args.app, call_type="cli"):
            terminal_print(message, message_type=status)
    elif args.command is None:
        parser.print_help()
