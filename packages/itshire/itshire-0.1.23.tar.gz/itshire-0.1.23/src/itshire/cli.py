import argparse


def parse_args():
    parser = argparse.ArgumentParser(description="Add sections to markdown files.")
    parser.add_argument(
        "-v", "--verbose", action="store_true", help="Enable verbose output"
    )

    subparsers = parser.add_subparsers(dest="command")

    addstores_parser = subparsers.add_parser(
        "addstores", help="Add stores as sections to markdown files"
    )
    addstores_parser.add_argument(
        "directory", help="Directory to search for Markdown files"
    )
    addstores_parser.add_argument(
        "-v", "--verbose", action="store_true", help="Enable verbose output"
    )

    args = parser.parse_args()
    return args
