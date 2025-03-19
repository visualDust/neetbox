# -*- coding: utf-8 -*-
#
# Author: GavinGong aka VisualDust
# Github: github.com/visualDust
# Date:   20240111

from random import random

from rich.console import Console
from rich.table import Table
from rich.text import Text
from vdtoys.mvc import Singleton
from vdtoys.registry import Registry

from .._formatting import RawLog

LogWriters = Registry("LOG_WRITERS")


console = Console()
whom2color = {}

supported_colors = ["red", "green", "blue", "cyan", "yellow", "magenta"]
supported_text_styles = ["bold", "italic", "blink", "dim"]


@LogWriters.register(name="stdout")
def log_write_stdout(log: RawLog):
    series = (
        {
            "ok": Text("[ok]", style="green"),
            "debug": Text("[debug]", style="cyan"),
            "info": Text("[info]", style="white"),
            "warning": Text("[warning]", style="yellow"),
            "mention": Text("[mention]", style="yellow"),
            "error": Text("[error]", style="red"),
        }.get(log.series, Text(log.series))
        if log.series
        else Text("")
    )
    table = Table(show_header=False, box=None, expand=True)
    table.add_column(justify="left")
    table.add_column(justify="right")
    whom = log.caller_name_alias or log.caller_info_formatted
    if whom not in whom2color:
        whom2color[whom] = supported_colors[int(random() * len(supported_colors))]
    color = whom2color[whom]
    whom_text = Text(whom, color)
    split_text = Text(" > ", style="dim " + color)
    message_text = Text(log.message, style="default")
    time_text = Text(log.timestamp.strftime(r"%H:%M:%S"), style="default dim")
    table.add_row(
        whom_text + split_text + message_text, series + " " + time_text if series else time_text
    )
    console.print(table)
