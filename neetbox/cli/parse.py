import json
import os

import click
from rich.console import Console
from rich.table import Table

import neetbox._daemon as daemon_module
import neetbox.config._cli_user_config as cliconfig
from neetbox._daemon.server._server import server_process
from neetbox.config._workspace import (
    _get_module_level_config,
    _init_workspace,
    _load_workspace_config,
)
from neetbox.logging.formatting import LogStyle
from neetbox.logging.logger import Logger
from neetbox.utils.massive import check_read_toml

from ._client_web_apis import *

console = Console()

logger = Logger("NEETBOX", style=LogStyle(with_datetime=False, skip_writers=["ws"]))


def get_daemon_config():
    return _get_module_level_config(daemon_module)


# def get_base_addr(port=0):
#     daemon_config = get_daemon_config()
#     _port = port or daemon_config["port"]
#     daemon_address = f"{daemon_config['host']}:{_port}"
#     return f"http://{daemon_address}/"


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
    CONFIG_FILE_NAME = f"neetbox.toml"
    is_workspace = check_read_toml(CONFIG_FILE_NAME)
    if is_workspace:
        _load_workspace_config()


@main.command(name="list")
def list_command():
    """Show list of connected project names"""
    _try_load_workspace_if_applicable()
    try:
        _response = get_list()
        table = Table(title="Running NEETBOX Projects")
        table.add_column(NAME_KEY, justify="center", style="magenta", no_wrap=True)
        table.add_column("online", justify="center", style="cyan")
        table.add_column("project id", justify="center", no_wrap=True)
        table.add_column("runs", justify="center", style="green")

        for pjt in _response:
            table.add_row(
                pjt[NAME_KEY],
                str(pjt["online"]),
                pjt[PROJECT_ID_KEY],
                "\n".join(pjt[STATUS_TABLE_NAME].keys()),
            )

        console.print(table)

        if not len(_response):
            console.print("*There is project no server")

    except Exception as e:  # noqa
        logger.log("Could not fetch data. Is there any project with NEETBOX running?")
        raise e


@main.command(name="status")
@click.argument("name", metavar="name", required=True)
def status_command(name):
    """Show running project status of given name"""
    _try_load_workspace_if_applicable()
    _response = None
    try:
        _response = get_status_of(project_id=name)
        click.echo(json.dumps(_response))
    except Exception as e:  # noqa
        logger.log("Could not fetch data. Is there any project with NEETBOX running?")


@main.command(name="serve")
@click.option(
    "--port", "-p", help="specify which port to launch", metavar="port", required=False, default=0
)
@click.option("--debug", "-d", is_flag=True, help="Run with debug mode", default=False)
def serve(port, debug):
    """serve neetbox server in attached mode"""
    _try_load_workspace_if_applicable()
    _daemon_config = get_daemon_config()
    try:
        logger.log(f"Launching server using config: {_daemon_config}")
        if port:
            _daemon_config["port"] = port
        server_process(cfg=_daemon_config, debug=debug)
    except Exception as e:
        logger.err(f"Failed to launch a neetbox server: {e}")
        raise e


@main.command(name="shutdown")
@click.option(
    "--port",
    "-p",
    help="specify which port to send shutdown",
    metavar="port",
    required=False,
    default=0,
)
def shutdown_server(port):
    """shutdown neetbox server on specific port"""
    _try_load_workspace_if_applicable()
    try:
        daemon_config = get_daemon_config()
        if port:
            daemon_config["port"] = port
        _response = shutdown()
        click.echo(_response)
    except Exception as e:
        logger.err(f"Failed to shutdown the neetbox server: {e}")
        raise e


@main.command()
@click.option("--name", "-n", help="set project name", metavar="name", required=False)
def init(name: str):
    """initialize current folder as workspace and generate the config file from defaults"""
    try:
        init_succeed = _init_workspace(name=name)
        if init_succeed:
            logger.console_banner("neetbox", font="ansishadow")
            logger.log("Welcome to NEETBOX")
    except Exception as e:
        logger.err(f"Failed to init here: {e}")


if __name__ == "__main__":
    main()
