import logging

from . import add_sections, cli, log

__project_name__ = "itshire"


def main() -> int:
    args = cli.parse_args()
    log.configure_logging(args.verbose)
    logging.debug("Starting itshire")

    if args.command == "addstores":
        try:
            add_sections.main(args.directory)
        except Exception as e:
            logging.error(f"An error occurred: {str(e)}")
            return 1
    else:
        print("Unknown command")
        return 1

    return 0
