# -*- coding: utf-8 -*-
#
# Author: GavinGong aka VisualDust
# Github: github.com/visualDust
# Date:   20230315

import functools
import os
from datetime import date
from enum import Enum
from typing import Callable, Optional, Union

from vdtoys.framing import get_caller_info_traceback
from vdtoys.registry import Registry

from ._formatting import LogStyle, RawLog
from .writers import FileLogWriter

LogWriters = Registry("LOG_WRITERS")


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
    _IDENTITY2LOGGER = {}

    def __init__(
        self,
        name_alias: str = None,
        style: Optional[LogStyle] = LogStyle(),
        log_level: LogLevel = LogLevel.INFO,
        skip_writers_names=[],
    ):
        """create a new logger

        Args:
            name_alias (str, optional): the name alias of the logger. Defaults to None.
            style (Optional[LogStyle], optional): logger's default log style. Defaults to LogStyle().
            log_level (LogLevel, optional): log level. Defaults to LogLevel.INFO.
            skip_writers_names (list, optional): names of writers to be skipped. Defaults to [].
        """

        self.name_alias = name_alias
        self._default_style = style
        self._log_level = log_level
        self.private_writers = {}
        self.skipped_writers_names = skip_writers_names

    def __new__(cls, name_alias: str = None, *args, **kwargs) -> "Logger":
        if name_alias in Logger._IDENTITY2LOGGER:
            return Logger._IDENTITY2LOGGER[name_alias]
        instance = super().__new__(cls)
        Logger._IDENTITY2LOGGER[name_alias] = instance
        return instance

    @property
    def style(self):
        return self._default_style

    @style.setter
    def style(self, style: LogStyle):
        self._default_style = style or LogStyle()

    @property
    def log_level(self):
        return self._log_level

    @log_level.setter
    def log_level(self, level: Union[LogLevel, str]):
        if type(level) is str:
            level = {
                "ALL": LogLevel.ALL,
                "DEBUG": LogLevel.DEBUG,
                "INFO": LogLevel.INFO,
                "WARNING": LogLevel.WARNING,
                "ERROR": LogLevel.ERROR,
            }[level]
        if type(level) is int:
            assert level >= 0 and level <= 3, "log level must be in [0, 3]"
            level = LogLevel(level)
        self._log_level = level

    @classmethod
    def set_global_log_level(cls, level: Union[LogLevel, str]):
        if type(level) is str:
            level = {
                "ALL": LogLevel.ALL,
                "DEBUG": LogLevel.DEBUG,
                "INFO": LogLevel.INFO,
                "WARNING": LogLevel.WARNING,
                "ERROR": LogLevel.ERROR,
            }[level]
        if type(level) is int:
            assert level >= 0 and level <= 3, "log level must be in [0, 3]"
            level = LogLevel(level)
        for logger in cls._IDENTITY2LOGGER.values():
            logger.log_level = level

    def writer(self, name: str):
        def _add_private_writer(name, writer_func: Callable):
            if name in self.private_writers:
                self.warn(f"writer {name} already exist as a private writer. overwrite anyway.")
            self.private_writers[name] = writer_func
            return writer_func

        return functools.partial(_add_private_writer, name=name)

    def skip_writer_name(self, name: str):
        self.skipped_writers_names.append(name)

    def log(
        self,
        *content,
        series: Optional[str] = None,
        skip_writers_names: list[str] = [],
        stack_offset=2,
    ):
        # converting passed message args into a single string
        message = ""
        for msg in content:
            message += str(msg) + " "

        log = RawLog(
            message=message,
            caller_info=get_caller_info_traceback(stack_offset=stack_offset),
            caller_name_alias=self.name_alias,
            series=series,
            style=self._default_style,
        )

        writers = []
        for writer_name, writer_func in LogWriters.items():  # collect global writers
            if writer_name not in self.skipped_writers_names + skip_writers_names:
                writers.append((writer_name, writer_func))

        for writer_name, writer_func in self.private_writers.items():  # collect private writers
            if writer_name not in self.skipped_writers_names + skip_writers_names:
                writers.append((writer_name, writer_func))

        for writer_name, writer_func in writers:
            try:
                writer_func(log)
            except Exception as e:
                print(f"log writer {writer_name} fialed: {e}, original message:")
                print(log)

        return self

    def ok(
        self,
        *content,
        skip_writers_names: list[str] = [],
        stack_offset=2,
    ):
        if self._log_level >= LogLevel.INFO:
            self.log(
                *content,
                series=f"ok",
                skip_writers_names=skip_writers_names,
                stack_offset=stack_offset + 1,
            )
        return self

    def debug(
        self,
        *content,
        skip_writers_names: list[str] = [],
        stack_offset=2,
    ):
        if self._log_level >= LogLevel.INFO:
            self.log(
                *content,
                series=f"debug",
                skip_writers_names=skip_writers_names,
                stack_offset=stack_offset + 1,
            )
        return self

    def info(
        self,
        *content,
        skip_writers_names: list[str] = [],
        stack_offset=2,
    ):
        if self._log_level >= LogLevel.INFO:
            self.log(
                *content,
                series=f"info",
                skip_writers_names=skip_writers_names,
                stack_offset=stack_offset + 1,
            )
        return self

    def warn(
        self,
        *content,
        skip_writers_names: list[str] = [],
        stack_offset=2,
    ):
        if self._log_level >= LogLevel.INFO:
            self.log(
                *content,
                series=f"warning",
                skip_writers_names=skip_writers_names,
                stack_offset=stack_offset + 1,
            )
        return self

    def err(
        self,
        err,
        skip_writers_names: list[str] = [],
        stack_offset=2,
        reraise=False,
    ):
        if self._log_level >= LogLevel.ERROR:
            self.log(
                str(err),
                series=f"error",
                skip_writers_names=skip_writers_names,
                stack_offset=stack_offset + 1,
            )
        if reraise:
            if not isinstance(err, Exception):
                err = RuntimeError(err)
            raise err
        return self

    def mention(
        self,
        mention_args=True,
        mention_result=True,
        skip_writers_names=[],
    ):
        def with_logging(func):
            @functools.wraps(func)
            def _with_logging(*args, **kwargs):
                self.log(
                    f"Entering: {func.__name__}" + f", args={args}, kwargs={kwargs}"
                    if mention_args
                    else "",
                    series=f"mention",
                    skip_writers_names=skip_writers_names,
                    stack_offset=4,
                )
                try:
                    result = func(*args, **kwargs)
                except Exception as e:
                    raise e
                self.log(
                    f"Leaving: {func.__name__}" + f", with returned value {result}"
                    if mention_result
                    else "",
                    series=f"mention",
                    skip_writers_names=skip_writers_names,
                    stack_offset=4,
                )
                return result

            return _with_logging

        return with_logging

    def set_log_dir(self, path, dedicated_file=False):
        if os.path.isfile(path):
            raise FileExistsError("Target path is not a directory.")
        if not os.path.exists(path):
            try:
                os.makedirs(path)
            except Exception:
                raise OSError(f"Failed when trying to create directory {path}")
        filename = ""
        filename += self.name_alias or "" if dedicated_file else ""
        filename += str(date.today()) + ".log"
        file_writer = FileLogWriter(os.path.join(path, filename))
        self.private_writers["file"] = file_writer.write
        return self


DEFAULT_LOGGER = Logger(None)
