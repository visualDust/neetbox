# -*- coding: utf-8 -*-
#
# Author: GavinGong aka VisualDust
# URL:    https://gong.host
# Date:   20230318

import warnings
import os
from colorama import Fore, Back, Style
from random import random
from ._colorama import *
from typing import Optional, Union

# todo use @cache when migrate to python 3.9
def get_supported_colors():
    supported_colors = []
    for color in AnsiColor:
        supported_colors.append(color)
    return supported_colors

def get_supported_styles():
    supported_styles = []
    for style in AnsiStyle:
        supported_styles.append(style)
    return supported_styles


class LogStyle:
    def __init__(self) -> None:
        self.fore: Optional[AnsiColor] = None
        self.back: Optional[AnsiColor] = None
        self.prefix: str = ""
        self.pattern = ""  # todo default pattern
        self.datetime_format: str = "%Y-%m-%d-%H:%M:%S"
        self.with_identifier: bool = True
        self.trace_level = 3
        self.with_datetime: bool = True
        self.split_char_cmd = " > "
        self.split_char_identity = "/"
        self.split_char_txt = " | "
        
    def parse(self,pattern:str):
        # todo
        pass

    def set_foreground_color(self, color: AnsiColor):
        self.fore = color
        return self

    def set_background_color(self, color: AnsiColor):
        self.back = color
        return self

    def set_prefix(self, prefix: str):
        self.prefix = prefix
        return self

    def set_datetime_format(self, datetime_format: str):
        self.datetime_format = datetime_format
        return self

    def randcolor(self):
        colors = get_supported_colors()
        split_index = int(random() * len(colors) / 2)
        index_offset = -1
        while index_offset == 0:  # fore and back shoud not be the same
            index_offset = int(random() * len(colors) / 2)
        self.back = colors[(split_index + index_offset) % len(colors)]
        self.fore = colors[(split_index - index_offset) % len(colors)]
        return self


DEFAULT_STYLE = LogStyle()


def colored(
    text, color_foreground: Optional[Union[AnsiColor,str]] = None, color_background: Optional[Union[AnsiColor,str]] = None
):
    """_summary_

    Args:
        text (str): original raw string
        color (AnsiColor): which color

    Raises: Nothing

    Returns:
        str: colored string
    """
    if "ANSI_COLORS_DISABLED" in os.environ or "NO_COLOR" in os.environ:
        warnings.warn(
            "Notice that current running environment does not supported colored text. NEETBOX logging facilities will still work but may not output colored text in console."
        )

    # Resolving foreground color
    if color_foreground:
        if type(color_foreground) is AnsiColor:
            color_foreground = color_foreground.value
        if hasattr(Fore, color_foreground.upper()):
            text = getattr(Fore, color_foreground.upper()) + text + Fore.RESET
        else:
            raise ValueError("Wrong color was inputed in colored func.")

    # Resolving background color
    if color_background:
        if type(color_background) is AnsiColor:
            color_background = color_background.value
        color_background = color_background.value
        if hasattr(Back, color_background.upper()):
            text = getattr(Back, color_background.upper()) + text + Fore.RESET
        else:
            raise ValueError("Wrong color was inputed in colored func.")

    return text


def colored_by_style(text, style: LogStyle):
    if style.fore is not None:  # applied foreground color
        return colored(text, color_foreground=style.fore)
    if style.back is not None:  # applied background color
        return colored(text, color_background=style.back)
    return text  # nothing applied
