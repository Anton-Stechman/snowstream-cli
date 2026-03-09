import argparse

def main() -> None:
    """
    Main CLI handler
    """
    parser = argparse.ArgumentParser(
        prog="snowstream",
        description="Example CLI tool"
    )

    parser.add_argument(
        "--name",
        default="World",
        help="Name to greet"
    )

    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Enable verbose output"
    )

    args = parser.parse_args()

    if args.verbose:
        print("Verbose mode enabled")

    print(f"Hello {args.name}!")
