import argparse
import os
import json
import neetbox
from neetbox.logging.logger import Logger
from neetbox.logging.formatting import LogStyle
from neetbox.daemon._apis import get_status_of

_log_style = LogStyle()
_log_style.with_datetime = False
logger = Logger("NEETBOX", style=_log_style)  # builtin standalone logger


def handle_status(args):
    _stat_json = None
    try:
        _stat_json = get_status_of()
        print(json.dumps(_stat_json))
    except Exception as e:
        logger.log("Could not fetch data. Is there any project with NEETBOX running?")


def handle_init(args):
    name = vars(args)["name"]
    try:
        if neetbox.init(name=name):
            logger.skip_lines(2)
            logger.banner("neetbox", font="ansishadow")
            logger.log("Welcome to NEETBOX")
    except Exception as e:
        logger.err(f"Failed to init here: {e}")


def handle_archive(args):
    logger.err(
        "This feature is not availiable. CLI Features are still under construction."
    )
    pass


def handle_list(args):
    logger.err(
        "This feature is not availiable. CLI Features are still under construction."
    )
    pass


def handle_dataset(args):
    logger.err(
        "This feature is not availiable. CLI Features are still under construction."
    )
    pass


parser = argparse.ArgumentParser(
    prog="NEETBOX", description="This is NEETBOX cli", epilog="NEETBOX would help?"
)
parser.add_argument(
    "-v", "--verbose", help="set verbose flag to True", action="store_true"
)  # on/off flag

subparsers = parser.add_subparsers(
    title="These are common NEEBOX commands used in various situations",
    metavar="command",
)

status_parser = subparsers.add_parser("status", help="Show the working tree status")
status_parser.set_defaults(handle=handle_status)

init_parser = subparsers.add_parser(
    "init",
    help="initialize current folder as workspace and generate the config file from defaults",
)
init_parser.add_argument(
    "--name",
    "-n",
    help="set project name",
    metavar="name",
    required=False,
    default=None,
)
init_parser.set_defaults(handle=handle_init)

commit_parser = subparsers.add_parser(
    "archive", help="Record changes to the repository"
)
commit_parser.add_argument(
    "--message",
    "-m",
    help="Use the given <msg> as the commit message",
    metavar="msg",
    required=True,
)
commit_parser.add_argument(
    "--delete",
    "-d",
    help="Delete files after archive done.",
    default=False,
    required=False,
)
commit_parser.set_defaults(handle=handle_archive)

list_parser = subparsers.add_parser(
    "list", help="List all the resources connected to NEETBOX"
)
list_parser.set_defaults(handle=handle_list)


def parse():
    args = parser.parse_args()
    if hasattr(args, "handle"):
        args.handle(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    parse()
