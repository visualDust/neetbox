# -*- coding: utf-8 -*-
#
# Author: GavinGong aka VisualDust
# URL:    https://gong.host
# Date:   20230318

import warnings
import os
from random import random
from typing import Optional


class LogStyle:
    @classmethod
    def get_supported_colors(cls):
        return ["red", "green", "blue", "cyan", "yellow", "magenta"]

    @classmethod
    def get_supported_text_style(cls):
        return ["bold", "italic", "blink"]

    def __init__(self) -> None:
        self.color: Optional[str] = None
        self.prefix: str = ""
        self.text_style: Optional[str] = None
        self.datetime_format: str = "%Y-%m-%d-%H:%M:%S"
        self.with_identifier: bool = True
        self.trace_level = 3
        self.with_datetime: bool = True
        self.split_char_cmd = " > "
        self.split_char_identity = "/"
        self.split_char_txt = " | "

    def parse(self, pattern: str):
        # todo
        pass

    def set_color(self, color: str):
        self.fore = color
        return self

    def set_text_style(self, text_style: str):
        self.text_style = text_style
        return self

    def set_prefix(self, prefix: str):
        self.prefix = prefix
        return self

    def set_datetime_format(self, datetime_format: str):
        self.datetime_format = datetime_format
        return self

    def randcolor(self):
        colors = LogStyle.get_supported_colors()
        # split_index = int(random() * len(colors) / 2)
        # index_offset = -1
        # while index_offset == 0:  # fore and back shoud not be the same
        #     index_offset = int(random() * len(colors) / 2)
        # self.back = colors[(split_index + index_offset) % len(colors)]
        # self.fore = colors[(split_index - index_offset) % len(colors)]
        self.color = colors[int(random() * len(colors))]
        return self


DEFAULT_STYLE = LogStyle()


def styled_text(text, style: LogStyle):
    attributes = []
    if style.color:
        attributes.append(style.color)
    if style.text_style:
        attributes.append(style.text_style)
    render_stack = []
    _prefix = ""
    _postfix = ""
    while len(attributes):
        attr = attributes.pop(-1)
        _prefix += f"[{attr}]"
        render_stack.append(attr)
    while len(render_stack):
        _postfix += f"[/{render_stack.pop(-1)}]"
    return f"{_prefix}{text}{_postfix}"


def colored_text(text: str, color):
    return f"[{color}]{text}[/{color}]"
