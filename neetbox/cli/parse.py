import json

import click

import neetbox
from neetbox.daemon.client._client_apis import *
from neetbox.logging.formatting import LogStyle
from neetbox.logging.logger import Logger

logger = Logger("NEETBOX", style=LogStyle(with_datetime=False, skip_writers=["ws"]))


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


@main.command(name="list")
def list_command():
    """Show list of connected project names"""
    try:
        _list_json = get_list()
        click.echo(json.dumps(_list_json))
    except Exception as e:  # noqa
        logger.log("Could not fetch data. Is there any project with NEETBOX running?")


@main.command(name="status")
@click.argument("name")
def status_command(name):
    """Show the working tree status"""
    _stat_json = None
    try:
        _stat_json = get_status_of(name)
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
            logger.console_banner("neetbox", font="ansishadow")
            logger.log("Welcome to NEETBOX")
    except Exception as e:
        logger.err(f"Failed to init here: {e}")


if __name__ == "__main__":
    main()
