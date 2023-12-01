import json
import os

import click
from rich.console import Console
from rich.table import Table

import neetbox
import neetbox.daemon as daemon_module
from neetbox.config import get_module_level_config
from neetbox.daemon.client._client_web_apis import *
from neetbox.daemon.server._server import server_process
from neetbox.logging.formatting import LogStyle
from neetbox.logging.logger import Logger

console = Console()

logger = Logger("NEETBOX", style=LogStyle(with_datetime=False, skip_writers=["ws"]))


def get_daemon_config():
    return get_module_level_config(daemon_module)


def get_base_addr(port=0):
    daemon_config = get_daemon_config()
    _port = port or daemon_config["port"]
    daemon_address = f"{daemon_config['host']}:{_port}"
    return f"http://{daemon_address}/"


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
@click.option(
    "--port",
    "-p",
    help="specify which port to fetch list",
    metavar="port",
    required=False,
    default=0,
)
def list_command(port):
    """Show list of connected project names"""
    _try_load_workspace_if_applicable()
    try:
        _response = get_list(base_addr=get_base_addr(port=port))

        table = Table(title="Running NEETBOX Projects")

        table.add_column("name", justify="center", style="cyan")
        table.add_column("workspace-id", justify="center", style="magenta", no_wrap=True)
        table.add_column("config", justify="center", style="green")

        for pjt in _response:
            config = pjt["config"]["value"]
            table.add_row(config["name"], pjt["id"], json.dumps(config))

        console.print(table)

    except Exception as e:  # noqa
        logger.log("Could not fetch data. Is there any project with NEETBOX running?")
        raise e


@main.command(name="status")
@click.argument("name", metavar="name", required=True)
@click.option(
    "--port",
    "-p",
    help="specify which port to fetch status",
    metavar="port",
    required=False,
    default=0,
)
def status_command(name, port):
    """Show running project status of given name"""
    _try_load_workspace_if_applicable()
    _response = None
    try:
        _response = get_status_of(base_addr=get_base_addr(port=port), workspace_id=name)
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
        _response = shutdown(base_addr=get_base_addr(port=port))
        click.echo(_response)
    except Exception as e:
        logger.err(f"Failed to shutdown the neetbox server: {e}")
        raise e


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
