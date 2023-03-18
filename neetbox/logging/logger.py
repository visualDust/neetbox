# -*- coding: utf-8 -*-
#
# Author: GavinGong aka VisualDust
# URL:    https://gong.host
# Date:   20230315

import getpass
import inspect
import os, re
import platform
from datetime import date, datetime
from enum import Enum
from neetbox.core.framing import *
from neetbox.logging.formatting import *


class LogLevel(Enum):
    ALL = 4
    INFO = 3
    DEBUG = 2
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


writers_dict = {}
style_dict = {}
loggers_dict = {}

_global_log_level = LogLevel.ALL


def set_log_level(level: LogLevel):
    if type(level) is int:
        assert level >= 0 and level <= 3
        level = LogLevel(level)
    _global_log_level = level


class Logger:
    def __init__(self, whom, style: LogStyle = None):
        self.whom: any = whom
        self.style: LogStyle = style
        self.file_writer = None

    def log(
        self,
        *content,
        prefix: str = None,
        datetime_format: str = None,
        with_identifier: bool = None,
        with_datetime: bool = None,
        into_file: bool = True,
        into_stdout: bool = True,
    ):
        _caller_identity = get_caller_identity_traceback(traceback=2)

        # getting style
        _style = self.style
        if not _style:  # if style not set
            _style_index = str(_caller_identity)
            if _style_index in style_dict:  # check for previous style
                _style = style_dict[_style_index]
            else:
                _style = LogStyle().randcolor()
                style_dict[_style_index] = _style

        # composing prefix
        _prefix = _style.prefix
        if prefix is not None:  # if using specific prefix
            _prefix = prefix

        # composing datetime
        _with_datetime = _style.with_datetime
        _datetime = ""
        if (
            with_datetime is not None
        ):  # if explicitly determined wether to log with datetime
            _with_datetime = with_datetime
        if _with_datetime:
            _datetime_fmt = (
                datetime_format if datetime_format else _style.datetime_format
            )
            _datetime = datetime.now().strftime(_datetime_fmt)

        # if with identifier
        _whom = ""
        _with_identifier = _style.with_identifier
        if (
            with_identifier is not None
        ):  # if explicitly determined wether to log with identifier
            _with_identifier = with_identifier
        if _with_identifier:
            _whom = self.whom  # check identity
            if _whom is None:  # if using default logger, tracing back to the caller
                id_seq = []
                file_level = True
                if _caller_identity.module_name and _style.trace_level >= 2:
                    id_seq.append(_caller_identity.module_name)  # trace as module level
                    file_level = False
                if _caller_identity.class_name and _style.trace_level >= 1:
                    id_seq.append(_caller_identity.class_name)  # trace as class level
                    file_level = False
                if file_level and _style.trace_level >= 1:
                    id_seq.append(
                        _caller_identity.filename
                    )  # not module level and class level
                if _caller_identity.func_name != "<module>":
                    id_seq.append(_caller_identity.func_name)  # skip for jupyters
                _whom = ""
                for i in range(len(id_seq)):
                    _whom += id_seq[i]
                    if i < len(id_seq) - 1:
                        _whom += _style.split_char_identity

        # converting args into a single string
        _message = ""
        for msg in content:
            _message += str(msg) + " "

        # perform log
        if into_stdout:
            print(
                _prefix
                + _datetime
                + _style.split_char_cmd * min(len(_datetime), 1)
                + colored_by_style(_whom, style=_style)
                + _style.split_char_cmd * min(len(_whom), 1)
                + _message
            )
        if into_file and self.file_writer:
            self.file_writer.write(
                _prefix
                + _datetime
                + _style.split_char_txt * min(len(_datetime), 1)
                + _whom
                + _style.split_char_txt * min(len(_whom), 1)
                + _message
                + '\n'
            )
        return self

    def debug(self, info, flag=f"DEBUG"):
        if _global_log_level >= LogLevel.DEBUG:
            self.log(info, prefix=f"[{colored(flag, AnsiColor.CYAN)}]", into_file=False)
            self.log(info, prefix=flag, into_stdout=False)
        return self

    def info(self, message, flag="INFO"):
        if _global_log_level >= LogLevel.INFO:
            self.log(
                message, prefix=f"[{colored(flag, AnsiColor.GREEN)}]", into_file=False
            )
            self.log(message, prefix=flag, into_stdout=False)
        return self

    def warn(self, message, flag="WARNING"):
        if _global_log_level >= LogLevel.WARNING:
            self.log(
                message, prefix=f"[{colored(flag, AnsiColor.YELLOW)}]", into_file=False
            )
            self.log(message, prefix=flag, into_stdout=False)
        return self

    def err(self, err, flag="ERROR"):
        if _global_log_level >= LogLevel.ERROR:
            self.log(err, prefix=f"[{colored(flag,AnsiColor.RED)}]", into_file=False)
            self.log(err, prefix=flag, into_stdout=False)
        return self

    def os_info(self):
        """Log some maybe-useful os info

        Returns:
            _Logger : the logger instance itself
        """
        message = (
            f"whom\t\t|\t" + getpass.getuser() + " using " + str(platform.node()) + "\n"
        )
        message += (
            "machine\t\t|\t"
            + str(platform.machine())
            + " on "
            + str(platform.processor())
            + "\n"
        )
        message += (
            "system\t\t|\t" + str(platform.system()) + str(platform.version()) + "\n"
        )
        message += (
            "python\t\t|\t"
            + str(platform.python_build())
            + ", ver "
            + platform.python_version()
            + "\n"
        )
        self.log(message, with_datetime=False, with_identifier=False)
        return self

    def skip_lines(self, line_cnt=1):
        """Let the logger log some empty lines

        Args:
            line_cnt (int, optional): how many empty line. Defaults to 1.

        Returns:
            _Logger : the logger instance itself
        """
        self.log("\n" * line_cnt, with_datetime=False, with_identifier=False)
        return self

    def log_txt_file(self, file):
        if isinstance(file, str):
            file = open(file)
        context = ""
        for line in file.readlines():
            context += line
        self.log(context, with_datetime=False, with_identifier=False)
        return self

    def set_log_dir(self, path, independent=False):
        if os.path.isfile(path):
            raise "Target path is not a directory."
        if not os.path.exists(path):
            DEFAULT_LOGGER.info(f"Directory {path} not found, trying to create.")
            try:
                os.makedirs(path)
            except:
                DEFAULT_LOGGER.err(f"Failed when trying to create directory {path}")
                raise Exception(f"Failed when trying to create directory {path}")
        log_file_name = ""
        if independent:
            log_file_name += self.whom
        log_file_name += str(date.today()) + ".log"
        self._bind_file(os.path.join(path, log_file_name))
        return self

    def _bind_file(self, path):
        log_file_identity = os.path.abspath(path)
        if os.path.isdir(log_file_identity):
            raise Exception("Target path is not a file.")
        filename = validateTitle(os.path.basename(path))
        dirname = os.path.dirname(path) if len(os.path.dirname(path)) != 0 else "."
        if not os.path.exists(dirname):
            raise Exception(f"Could not find dictionary {dirname}")
        real_path = os.path.join(dirname, filename)
        if log_file_identity not in writers_dict:
            # todo add fflush buffer size or time
            writers_dict[log_file_identity] = open(
                real_path, "a", encoding="utf-8", buffering=1
            )
        self.file_writer = writers_dict[log_file_identity]
        return self

    def file_bend(self) -> bool:
        return self.file_writer == None


DEFAULT_LOGGER = Logger(None)


def get_logger(whom: any = None, icon=None, style: LogStyle = None) -> Logger:
    if whom is None:
        return DEFAULT_LOGGER
    if whom in loggers_dict:
        return loggers_dict[whom]
    loggers_dict[whom] = Logger(whom=whom, style=style)
    return loggers_dict[whom]


def validateTitle(text: str):
    """Remove invalid characters for windows file systems

    Args:
        title (str): the given title

    Returns:
        str: valid text
    """
    if platform.system().lower() == "windows":
        rstr = r"[\/\\\:\*\?\"\<\>\|]"  # '/ \ : * ? " < > |'
        new_title = re.sub(rstr, "_", text)  # replace with '_'
        return new_title
    return text
