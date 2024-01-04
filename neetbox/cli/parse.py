# -*- coding: utf-8 -*-
#
# Author: GavinGong aka VisualDust
# Github: github.com/visualDust
# Date:   20231013

import json
import os

import click
from rich.console import Console
from rich.table import Table

import neetbox.config._global as global_config
from neetbox._protocol import VERSION
from neetbox.client._client_web_apis import *
from neetbox.config._workspace import (
    _get_module_level_config,
    _init_workspace,
    _load_workspace_config,
)
from neetbox.logging.formatting import LogStyle
from neetbox.logging.logger import Logger
from neetbox.utils.massive import check_read_toml

console = Console()

logger = Logger("NEETBOX CLI", style=LogStyle(with_datetime=False, skip_writers=["ws", "file"]))


def get_client_config():
    return _get_module_level_config("client")


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
        _load_workspace_config(load_only=True)


@main.command(name="version")
def version_command():
    print(VERSION)


@main.command(name="serve")
@click.option(
    "--port", "-p", help="specify which port to launch", metavar="port", required=False, default=0
)
@click.option("--debug", "-d", is_flag=True, help="Run with debug mode", default=False)
def serve(port, debug):
    """serve neetbox server in attached mode"""
    _try_load_workspace_if_applicable()
    _daemon_config = get_client_config()
    try:
        logger.log(f"Launching server using config: {_daemon_config}")
        if port:
            _daemon_config["port"] = port
        from neetbox.server._server import server_process

        server_process(cfg=_daemon_config, debug=debug)
    except Exception as e:
        logger.err(f"Failed to launch a neetbox server: {e}", reraise=True)


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
        daemon_config = get_client_config()
        if port:
            daemon_config["port"] = port
        _response = shutdown()
        click.echo(_response)
    except Exception as e:
        logger.err(
            f"Failed to shutdown the neetbox server: {e}. Is the server running on port {daemon_config['port']}?"
        )


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
