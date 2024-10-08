# -*- coding: utf-8 -*-
#
# Author: GavinGong aka VisualDust
# Github: github.com/visualDust
# Date:   20231013

import os
from random import randint
from typing import Optional

import click
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from neetbox._protocol import VERSION
from neetbox.client._client_web_apis import *
from neetbox.config.project import (
    _get_module_level_config,
    _init_workspace,
    _load_workspace_config,
)
from neetbox.config.user import get as get_global_config
from neetbox.config.user import set as set_global_config
from neetbox.logging import Logger
from neetbox.utils.localstorage import get_create_neetbox_config_directory
from neetbox.utils.massive import check_read_toml

console = Console()

logger = Logger("NEETBOX CLI", skip_writers_names=["ws", "file"])


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
@click.option("--detach", "-d", is_flag=True, help="Run in detached mode", default=False)
def serve(port, detach):
    """serve neetbox server in attached mode"""
    _try_load_workspace_if_applicable()
    _daemon_config = get_client_config()
    try:
        if port:
            _daemon_config["port"] = port
        logger.log(f"Launching server using config: {_daemon_config}")
        import neetbox.server._daemon_server_launch_script as server_launcher

        if detach:
            server_launcher.start(_daemon_config)
        else:
            server_launcher.run(_daemon_config)
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


def console_banner(text, font: Optional[str] = None):
    from pyfiglet import Figlet, FigletFont

    builtin_font_list = [
        "ansiregular",
        "ansishadow",
        "isometrixc2",
        "nscripts",
        "nvscript",
    ]
    if not font:
        font = builtin_font_list[randint(0, len(builtin_font_list)) - 1]

    if font not in FigletFont.getFonts():
        if font in builtin_font_list:  # builtin but not installed
            module_path = os.path.dirname(__file__)
            FigletFont.installFonts(f"{module_path}/flfs/{font}.flf")
        else:  # path?
            assert os.path.isfile(font), "The provided font is not a fontname or a font file path."
            file_name = os.path.basename(font)
            file = os.path.splitext(file_name)
            if file[0] not in FigletFont.getFonts():  # no installed file match the file name
                try:
                    FigletFont.installFonts(f"res/flfs/{font}.flf")
                except Exception:
                    font = None
            else:
                font = file[0]
    f = Figlet(font)
    rendered_text = f.renderText(text)
    console.print(Panel.fit(f"{rendered_text}", border_style="green"))


@main.command(name="init")
@click.option("--name", "-n", help="set project name", metavar="name", required=False)
def init(name: str):
    """initialize current folder as workspace and generate the config file from defaults"""
    try:
        init_succeed = _init_workspace(name=name)
        if init_succeed:
            console_banner("neetbox", font="ansishadow")
            logger.log("Welcome to NEETBOX")
    except Exception as e:
        logger.err(f"Failed to init here: {e}")


@main.command(name="config")
@click.option(
    "--set",
    "kvs",
    type=(str, str),
    multiple=True,
    help="specify which config name to modify as well as target value",
    metavar="name value",
    required=False,
    default=None,
)
@click.option("--force", "-f", is_flag=True, help="force set", default=False)
def configs(kvs, force):
    """list or set global config"""
    if kvs:
        current_configs = get_global_config()
        for k, v in kvs:
            if k not in current_configs and not force:
                logger.warn(
                    f"config key {k} not exist in current config file and will not be writen into config. if you want to write anyway, try --force."
                )
            else:
                set_global_config(k, v)
    table = Table(title="current global configs")
    table.add_column("name", style="green", no_wrap=True)
    table.add_column("current value")
    for k, v in get_global_config().items():
        table.add_row(str(k), str(v))
    console.print(table)
    logger.info(f"from config file folder: {get_create_neetbox_config_directory()}")


if __name__ == "__main__":
    main()
