# -*- coding: utf-8 -*-
#
# Author: GavinGong aka VisualDust
# URL:    https://gong.host
# Date:   20230318

from dataclasses import dataclass
from random import random
from typing import Optional

DATETIME_FORMAT = "%Y-%m-%dT%H:%M:%S.%f"  # YYYY-MM-DDTHH:MM:SS.SSS


@dataclass
class LogStyle:
    console_color: Optional[str] = None
    prefix: str = ""
    text_style: Optional[str] = None
    datetime_format: str = DATETIME_FORMAT
    with_identifier: bool = True
    trace_level = 3
    with_datetime: bool = True
    split_char_cmd = " > "
    split_char_identity = "/"
    split_char_txt = " | "
    skip_writers: list[str] = None

    @classmethod
    def get_supported_colors(cls):
        return ["red", "green", "blue", "cyan", "yellow", "magenta"]

    @classmethod
    def get_supported_text_style(cls):
        return ["bold", "italic", "blink"]

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
        self.console_color = colors[int(random() * len(colors))]
        return self


DEFAULT_STYLE = LogStyle()


def styled_text(text, style: LogStyle):
    attributes = []
    if style.console_color:
        attributes.append(style.console_color)
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
    text = text.replace("[", "\[")
    return f"[{color}]{text}[/{color}]"
