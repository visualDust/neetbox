# -*- coding: utf-8 -*-
#
# Author: GavinGong aka VisualDust
# URL:    https://gong.host
# Date:   20230315

import functools
import os
from datetime import date, datetime
from enum import Enum
from random import randint
from typing import Any, Optional, Union

from rich import print as rprint
from rich.panel import Panel

from neetbox.config import get_module_level_config
from neetbox.logging._writer import (
    FileLogWriter,
    JsonLogWriter,
    RawLog,
    consoleLogWriter,
    webSocketLogWriter,
)
from neetbox.logging.formatting import LogStyle, colored_text, styled_text
from neetbox.utils import formatting
from neetbox.utils.framing import get_caller_identity_traceback


class LogLevel(Enum):
    ALL = 4
    DEBUG = 3
    INFO = 2
    WARNING = 1
    ERROR = 0

    def __lt__(self, other):
        return self.value < other.value

    def __le__(self, other):
        return self.value <= other.value

    def __eq__(self, other):
        return self.value == other.value

    def __ne__(self, other):
        return self.value != other.value

    def __gt__(self, other):
        return self.value > other.value

    def __ge__(self, other):
        return self.value >= other.value


_GLOBAL_LOG_LEVEL = LogLevel.ALL


def set_log_level(level: LogLevel):
    if type(level) is str:
        level = {
            "ALL": LogLevel.ALL,
            "DEBUG": LogLevel.DEBUG,
            "INFO": LogLevel.INFO,
            "WARNING": LogLevel.WARNING,
            "ERROR": LogLevel.ERROR,
        }[level]
    if type(level) is int:
        assert level >= 0 and level <= 3
        level = LogLevel(level)
    global _GLOBAL_LOG_LEVEL
    _GLOBAL_LOG_LEVEL = level


class Logger:
    # global static
    __WHOM_2_LOGGER = {}
    __WHOM_2_STYLE = {}

    def __init__(self, whom=None, style: Optional[LogStyle] = None):
        self.whom: Any = whom
        if style and style.console_color is None:
            style.randcolor()
        self.style: Optional[LogStyle] = style
        # default writing to console and ws
        self.console_writer = consoleLogWriter
        self.ws_writer = webSocketLogWriter
        self.file_writer = None

        _cfg = get_module_level_config()
        self.set_log_dir(_cfg["logdir"])
        set_log_level(_cfg["level"])

    def __call__(self, whom: Any = None, style: Optional[LogStyle] = None) -> "Logger":
        if whom is None:
            return DEFAULT_LOGGER
        if whom in Logger.__WHOM_2_LOGGER:
            return Logger.__WHOM_2_LOGGER[whom]
        Logger.__WHOM_2_LOGGER[whom] = Logger(whom=whom, style=style)
        return Logger.__WHOM_2_LOGGER[whom]

    def log(
        self,
        *content,
        prefix: Optional[str] = None,
        datetime_format: Optional[str] = None,
        with_identifier: Optional[bool] = None,
        with_datetime: Optional[bool] = None,
        skip_writers: list[str] = [],
        traceback=2,
    ):
        _caller_identity = get_caller_identity_traceback(traceback=traceback)

        # converting args into a single string
        _pure_str_message = ""
        for msg in content:
            _pure_str_message += str(msg) + " "

        if type(skip_writers) is str:
            skip_writers = [skip_writers]

        _style = self.style
        if not _style:  # if style not set
            _style_index = str(_caller_identity)
            if _style_index in Logger.__WHOM_2_STYLE:  # check for previous style
                _style = Logger.__WHOM_2_STYLE[_style_index]
            else:
                _style = LogStyle().randcolor()
                Logger.__WHOM_2_STYLE[_style_index] = _style

        raw_log = RawLog(
            rich_msg=_pure_str_message,
            caller_identity=_caller_identity,
            whom=self.whom,
            style=_style,
            prefix=prefix,
            datetime_format=datetime_format,
            with_identifier=with_identifier,
            with_datetime=with_datetime,
            skip_writers=skip_writers,
        )

        for writer in [self.console_writer, self.ws_writer, self.file_writer]:
            if writer:
                raw_log.write_by(writer)

        return self

    def ok(
        self,
        *content,
        datetime_format: Optional[str] = None,
        with_identifier: Optional[bool] = None,
        with_datetime: Optional[bool] = None,
        skip_writers: list[str] = [],
    ):
        if _GLOBAL_LOG_LEVEL >= LogLevel.INFO:
            self.log(
                *content,
                prefix=f"[{colored_text('ok', 'green')}]",
                skip_writers=["file", "ws"] + skip_writers,
                traceback=3,
                datetime_format=datetime_format,
                with_identifier=with_identifier,
                with_datetime=with_datetime,
            )
            self.log(
                *content,
                prefix="ok",
                skip_writers=["stdout"] + skip_writers,
                traceback=3,
                datetime_format=datetime_format,
                with_identifier=with_identifier,
                with_datetime=with_datetime,
            )
        return self

    def debug(
        self,
        *content,
        datetime_format: Optional[str] = None,
        with_identifier: Optional[bool] = None,
        with_datetime: Optional[bool] = None,
        skip_writers: list[str] = [],
    ):
        if _GLOBAL_LOG_LEVEL >= LogLevel.DEBUG:
            self.log(
                *content,
                prefix=f"[{colored_text('debug', 'cyan')}]",
                skip_writers=["file", "ws"] + skip_writers,
                traceback=3,
                datetime_format=datetime_format,
                with_identifier=with_identifier,
                with_datetime=with_datetime,
            )
            self.log(
                *content,
                prefix="debug",
                skip_writers=["stdout"] + skip_writers,
                traceback=3,
                datetime_format=datetime_format,
                with_identifier=with_identifier,
                with_datetime=with_datetime,
            )
        return self

    def info(
        self,
        *message,
        datetime_format: Optional[str] = None,
        with_identifier: Optional[bool] = None,
        with_datetime: Optional[bool] = None,
        skip_writers: list[str] = [],
    ):
        if _GLOBAL_LOG_LEVEL >= LogLevel.INFO:
            self.log(
                *message,
                prefix=f"[{colored_text('info', 'white')}]",
                skip_writers=["file", "ws"] + skip_writers,
                traceback=3,
                datetime_format=datetime_format,
                with_identifier=with_identifier,
                with_datetime=with_datetime,
            )
            self.log(
                *message,
                prefix="info",
                skip_writers=["stdout"] + skip_writers,
                traceback=3,
                datetime_format=datetime_format,
                with_identifier=with_identifier,
                with_datetime=with_datetime,
            )
        return self

    def warn(
        self,
        *message,
        datetime_format: Optional[str] = None,
        with_identifier: Optional[bool] = None,
        with_datetime: Optional[bool] = None,
        skip_writers: list[str] = [],
    ):
        if _GLOBAL_LOG_LEVEL >= LogLevel.WARNING:
            self.log(
                *message,
                prefix=f"[{colored_text('warning', 'yellow')}]",
                skip_writers=["file", "ws"] + skip_writers,
                traceback=3,
                datetime_format=datetime_format,
                with_identifier=with_identifier,
                with_datetime=with_datetime,
            )
            self.log(
                *message,
                prefix="warning",
                skip_writers=["stdout"],
                traceback=3,
                datetime_format=datetime_format,
                with_identifier=with_identifier,
                with_datetime=with_datetime,
            )
        return self

    def err(
        self,
        err,
        datetime_format: Optional[str] = None,
        with_identifier: Optional[bool] = None,
        with_datetime: Optional[bool] = None,
        skip_writers: list[str] = [],
        reraise=False,
    ):
        if type(err) is not Exception:
            err = RuntimeError(str(err))
        if _GLOBAL_LOG_LEVEL >= LogLevel.ERROR:
            self.log(
                str(err),
                prefix=f"[{colored_text('error','red')}]",
                skip_writers=["file", "ws"] + skip_writers,
                traceback=3,
                datetime_format=datetime_format,
                with_identifier=with_identifier,
                with_datetime=with_datetime,
            )
            self.log(
                str(err),
                prefix="error",
                skip_writers=["stdout"],
                traceback=3,
                datetime_format=datetime_format,
                with_identifier=with_identifier,
                with_datetime=with_datetime,
            )
        if reraise or _GLOBAL_LOG_LEVEL >= LogLevel.DEBUG:
            raise err
        return self

    def mention(self, func):
        @functools.wraps(func)
        def with_logging(*args, **kwargs):
            self.log(f"Currently running: {func.__name__}", traceback=3)
            return func(*args, **kwargs)

        return with_logging

    def console_banner(self, text, font: Optional[str] = None):
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
                assert os.path.isfile(
                    font
                ), "The provided font is not a fontname or a font file path."
                file_name = os.path.basename(font)
                file = os.path.splitext(file_name)
                if file[0] not in FigletFont.getFonts():  # no installed file match the file name
                    try:
                        self.info(f"{file[0]} is not installed. Trying to install as a fontfile.")
                        FigletFont.installFonts(f"res/flfs/{font}.flf")
                    except Exception:
                        self.err("Could not install font {font}. Fallback to default.")
                        font = None
                else:
                    font = file[0]
        f = Figlet(font)
        rendered_text = f.renderText(text)
        rprint(Panel.fit(f"{rendered_text}", border_style="green"))
        return self

    def skip_lines(self, line_cnt=1, skip_writers: list[str] = []):
        """Let the logger log some empty lines

        Args:
            line_cnt (int, optional): how many empty line. Defaults to 1.

        Returns:
            _Logger : the logger instance itself
        """
        self.log(
            "\n" * line_cnt, with_datetime=False, with_identifier=False, skip_writers=skip_writers
        )
        return self

    def log_txt_file(self, file, skip_writers: list[str] = []):
        if isinstance(file, str):
            file = open(file)
        context = ""
        for line in file.readlines():
            context += line
        self.log(context, with_datetime=False, with_identifier=False, skip_writers=skip_writers)
        return self

    def set_log_dir(self, path, independent=False):
        if not path:
            self._bind_file(None)
            return self
        if not path:
            self._bind_file(None)
            return self
        if os.path.isfile(path):
            raise Exception("Target path is not a directory.")
        if not os.path.exists(path):
            DEFAULT_LOGGER.info(f"Directory {path} not found, trying to create.")
            try:
                os.makedirs(path)
            except Exception:
                DEFAULT_LOGGER.err(f"Failed when trying to create directory {path}")
                raise Exception(f"Failed when trying to create directory {path}")
        log_file_name = ""
        if independent:
            log_file_name += self.whom
        log_file_name += str(date.today()) + ".log"
        self._bind_file(os.path.join(path, log_file_name))
        return self

    def _bind_file(self, path):
        if not path:
            self.file_writer = None
            return self
        self.file_writer = FileLogWriter(path=path)
        return self

    def file_bend(self) -> bool:
        return self.file_writer is not None


DEFAULT_LOGGER = Logger(None)
