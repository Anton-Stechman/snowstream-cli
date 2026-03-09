import os
import argparse
from snowstream_cli.cli.handlers import initialise

class InitialiseAction(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        initialise(values)

def main() -> None:
    """
    Main CLI handler
    """
    parser = argparse.ArgumentParser(
        prog="snowstream"
        , description="Snowstream CLI"
    )

    subparsers = parser.add_subparsers(dest="command")

    init_parser = subparsers.add_parser("init", help="Initialise a new snowstream project")

    init_parser.add_argument(
        "--auto-create"
        , action="store_true"
        , default=False
        , help="Auto-Create Target directory to initialise project in if it does no exist"
    )

    init_parser.add_argument(
        "--force"
        , action="store_true"
        , default=False
        , help="Overwrite existing files without prompting"
    )

    init_parser.add_argument(
        "--dir"
        , type=str
        , default=os.getcwd()
        , metavar="PATH"
        , help="Target directory to initialise project in (default: current directory)"
    )
    args = parser.parse_args()

    if args.command == "init":
        initialise(auto_create=args.auto_create, force=args.force, dir=args.dir)
    elif args.command is None:
        parser.print_help()
