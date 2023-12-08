# -*- coding: utf-8 -*-
#
# Author: GavinGong aka VisualDust
# URL:    https://gong.host
# Date:   20230315

import functools
import os
from datetime import date
from enum import Enum
from random import randint
from typing import Any, Optional

from rich.console import Console
from rich.panel import Panel

from neetbox.config._workspace import (
    _get_module_level_config as get_module_level_config,
)
from neetbox.logging._writer import (
    FileLogWriter,
    JsonLogWriter,
    RawLog,
    consoleLogWriter,
    webSocketLogWriter,
)
from neetbox.logging.formatting import LogStyle
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


class Logger:
    # global static
    __WHOM_2_LOGGER = {}
    __WHOM_2_STYLE = {}
    _console = Console()

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
        self.set_log_level(_cfg["level"])

    def __call__(self, whom: Any = None, style: Optional[LogStyle] = None) -> "Logger":
        """Attention! do not call this logger instance unless you know what are you doing. Users should use the default logger by import logger from neetbox.logging.

        Args:
            whom (Any, optional): who is logging, could be anything. Defaults to None(neetbox will automatically trace who is creating this logger if set to None).
            style (Optional[LogStyle], optional): overwrite default logger style. Defaults to None(neetbox will create a default style if set to None).

        Returns:
            Logger: a new logger
        """
        if whom is None:
            return DEFAULT_LOGGER
        if whom in Logger.__WHOM_2_LOGGER:
            return Logger.__WHOM_2_LOGGER[whom]
        Logger.__WHOM_2_LOGGER[whom] = Logger(whom=whom, style=style)
        return Logger.__WHOM_2_LOGGER[whom]

    def set_log_level(self, level: LogLevel):
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
        self.log_level = level

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
        """log something

        Args:
            prefix (Optional[str], optional): prefix shows at the start of console log while it shows as a tag on frontend. Defaults to None.
            datetime_format (Optional[str], optional): change the format neetbox displays time. Defaults to None("%Y-%m-%dT%H:%M:%S.%f").
            with_identifier (Optional[bool], optional): whether to show who is logging, note that this option has noting todo with traceback. Defaults to None(True).
            with_datetime (Optional[bool], optional): whether to show datetime in logs. Defaults to None(True).
            skip_writers (list[str], optional): writers to skip, possible writes are 'stdout'(write into console), 'file'(write into file), 'ws'(write to frontend). Defaults to [], which means write to all writers.
            traceback (int, optional): level of traceback. Defaults to 2.

        Returns:
            _type_: _description_
        """
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
        if self.log_level >= LogLevel.INFO:
            self.log(
                *content,
                prefix=f"ok",
                skip_writers=skip_writers,
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
        if self.log_level >= LogLevel.DEBUG:
            self.log(
                *content,
                prefix=f"debug",
                skip_writers=skip_writers,
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
        if self.log_level >= LogLevel.INFO:
            self.log(
                *message,
                prefix=f"info",
                skip_writers=skip_writers,
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
        if self.log_level >= LogLevel.WARNING:
            self.log(
                *message,
                prefix=f"warning",
                skip_writers=skip_writers,
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
        if self.log_level >= LogLevel.ERROR:
            self.log(
                str(err),
                prefix=f"error",
                skip_writers=skip_writers,
                traceback=3,
                datetime_format=datetime_format,
                with_identifier=with_identifier,
                with_datetime=with_datetime,
            )
        if type(err) is Exception:
            if reraise:
                raise err
            elif self.log_level >= LogLevel.DEBUG:
                Logger._console.print_exception(err)
        return self

    def mention(
        self,
        mention_args=True,
        mention_result=True,
        skip_writers=[],
        datetime_format=None,
        with_identifier=None,
        with_datetime=None,
    ):
        def with_logging(func):
            @functools.wraps(func)
            def _with_logging(*args, **kwargs):
                self.log(
                    f"Entering: {func.__name__}" + f", args={args}, kwargs={kwargs}"
                    if mention_args
                    else "",
                    prefix=f"mention",
                    skip_writers=skip_writers,
                    traceback=4,
                    datetime_format=datetime_format,
                    with_identifier=with_identifier,
                    with_datetime=with_datetime,
                )
                try:
                    result = func(*args, **kwargs)
                except Exception as e:
                    raise e
                self.log(
                    f"Leaving: {func.__name__}" + f", with returned value {result}"
                    if mention_result
                    else "",
                    prefix=f"mention",
                    skip_writers=skip_writers,
                    traceback=4,
                    datetime_format=datetime_format,
                    with_identifier=with_identifier,
                    with_datetime=with_datetime,
                )
                return result

            return _with_logging

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
        Logger._console.print(Panel.fit(f"{rendered_text}", border_style="green"))
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
            try:
                os.makedirs(path)
            except Exception:
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
