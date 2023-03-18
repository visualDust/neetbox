import argparse
import os

def handle_status(working_path, args):
    pass


def handle_init(working_path, args):
    pass


def handle_archive(working_path, args):
    pass


def handle_list(working_path, args):
    pass

def handle_dataset(working_path, args):
    pass


parser = argparse.ArgumentParser(
    prog="NEETBOX", description="This is NEETBOX cli", epilog="NEETBOX would help?"
)
parser.add_argument("-v", "--verbose",help='set verbose flag to True', action="store_true")  # on/off flag

subparsers = parser.add_subparsers(
    title="These are common NEEBOX commands used in various situations", metavar="command"
)
status_parser = subparsers.add_parser("status", help="Show the working tree status")
status_parser.set_defaults(handle=handle_status)
add_parser = subparsers.add_parser("init", help="initialize current folder as NEETBOX workspace")
add_parser.add_argument("pathspec", help="Files to add content from", nargs="*")
add_parser.set_defaults(handle=handle_init)
commit_parser = subparsers.add_parser("archive", help="Record changes to the repository")
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

class NBWorkspace:
    def __init__(self) -> None:
        pass

def parse():
    args = parser.parse_args()
    if hasattr(args, 'handle'):
        args.handle(NBWorkspace(), args)
    else:
        parser.print_help()


if __name__ == "__main__":
    parse()
