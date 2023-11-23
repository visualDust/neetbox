import json

import click

import neetbox
from neetbox.daemon.client._client_apis import get_status_of
from neetbox.logging.formatting import LogStyle
from neetbox.logging.logger import Logger

_log_style = LogStyle()
_log_style.with_datetime = False
logger = Logger("NEETBOX", style=_log_style)  # builtin standalone logger


@click.group()
@click.option(
    "--verbose",
    "-v",
    help="set verbose flag to True",
    default=False,
)
@click.pass_context
def main(ctx, verbose: bool):
    ctx.ensure_object(dict)
    """This is NEETBOX cli"""
    ctx.obj["verbose"] = verbose


@main.command()
def status():
    """Show the working tree status"""
    _stat_json = None
    try:
        _stat_json = get_status_of()
        click.echo(json.dumps(_stat_json))
    except Exception as e:  # noqa
        logger.log("Could not fetch data. Is there any project with NEETBOX running?")


@main.command()
@click.option("--name", "-n", help="set project name", metavar="name", required=False)
def init(name: str):
    """initialize current folder as workspace and generate the config file from defaults"""
    try:
        if neetbox.init(name=name):
            logger.skip_lines(2)
            logger.banner("neetbox", font="ansishadow")
            logger.log("Welcome to NEETBOX")
    except Exception as e:
        logger.err(f"Failed to init here: {e}")


@main.command()
@click.option(
    "--message",
    "-m",
    help="Use the given <msg> as the commit message",
    metavar="message",
    required=True,
)
@click.option(
    "--delete",
    "-d",
    help="Delete files after archive done.",
    default=False,
    required=False,
)
def archive(message: str, delete: bool):
    """Record changes to the repository"""
    pass


@main.command()
def list():
    """List all the resources connected to NEETBOX"""
    pass


if __name__ == "__main__":
    main()
