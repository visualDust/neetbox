import json
import os

import click

import neetbox
import neetbox.daemon.server as server_module
from neetbox.config import get_module_level_config
from neetbox.daemon.client._client_apis import *
from neetbox.daemon.server._server import server_process
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


def _try_load_workspace_if_applicable():
    if neetbox._is_in_workspace():
        success = neetbox._load_workspace()
        if not success:
            os._exit(255)


@main.command(name="list")
def list_command():
    """Show list of connected project names"""
    _try_load_workspace_if_applicable()
    try:
        _list_json = get_list()
        click.echo(json.dumps(_list_json))
    except Exception as e:  # noqa
        logger.log("Could not fetch data. Is there any project with NEETBOX running?")


@main.command(name="status")
@click.argument("name")
def status_command(name):
    """Show the working tree status"""
    _try_load_workspace_if_applicable()
    _stat_json = None
    try:
        _stat_json = get_status_of(name)
        click.echo(json.dumps(_stat_json))
    except Exception as e:  # noqa
        logger.log("Could not fetch data. Is there any project with NEETBOX running?")


@main.command(name="serve")
@click.option("--port", "-p", help="specify which port to launch", metavar="port", required=False)
def serve(port: int):
    """serve neetbox server in attached mode"""
    _try_load_workspace_if_applicable()
    try:
        server_config = get_module_level_config(server_module)
        logger.log(f"Launching server using config: {server_config}")
        server_process(cfg=server_config)
    except Exception as e:
        logger.err(f"Failed to launch a neetbox server: {e}")


@main.command()
@click.option("--name", "-n", help="set project name", metavar="name", required=False)
def init(name: str):
    """initialize current folder as workspace and generate the config file from defaults"""
    try:
        if neetbox._init_workspace(name=name):
            logger.console_banner("neetbox", font="ansishadow")
            logger.log("Welcome to NEETBOX")
    except Exception as e:
        logger.err(f"Failed to init here: {e}")


if __name__ == "__main__":
    main()
