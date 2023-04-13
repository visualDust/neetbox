# -*- coding: utf-8 -*-
#
# Author: GavinGong aka VisualDust
# URL:    https://gong.host
# Date:   20230315

import os
import io
from datetime import date, datetime
from enum import Enum
from neetbox.utils.framing import *
from pyfiglet import Figlet, FigletFont
from neetbox.utils import utils
from neetbox.logging.formatting import *
from inspect import isclass, iscoroutinefunction, isgeneratorfunction
import functools
import pathlib
from random import randint
from typing import *


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
    global _global_log_level
    _global_log_level = level


class LogMetadata:
    def __init__(self, writer: "_AutoSplitLogWriter"):
        self.written_bytes = 0
        self.log_writer = writer


SplitStrategyCallable = Callable[[LogMetadata], Union[str, Iterable[str]]]


class LogSplitStrategies:
    @staticmethod
    def by_date() -> SplitStrategyCallable:
        def _split_strategy(metadata: LogMetadata):
            return date.today().strftime("%Y%m%d")

        return _split_strategy

    @staticmethod
    def by_hour() -> SplitStrategyCallable:
        def _split_strategy(metadata: LogMetadata):
            return datetime.now().strftime("%Y%m%d-%H")

        return _split_strategy

    @staticmethod
    def by_date_and_size(size_in_bytes: int) -> SplitStrategyCallable:
        class DateSizeSplitStrategy:
            def __init__(self):
                self.file_id = None

            def _already_exists(self, metadata: LogMetadata, file_id: int) -> bool:
                f = metadata.log_writer.make_logfile_path(self.make_result(file_id))
                return f.exists()

            def make_result(self, file_id):
                return date.today().strftime("%Y%m%d"), str(file_id)

            def __call__(self, metadata: LogMetadata):
                if self.file_id is None:
                    self.file_id = 0
                    while self._already_exists(metadata, self.file_id):
                        self.file_id += 1
                return self.make_result(
                    self.file_id + metadata.written_bytes // size_in_bytes
                )

        return DateSizeSplitStrategy()


class _AutoSplitLogWriter(io.TextIOBase):
    class ReentrantCounter:
        def __init__(self):
            self._count = 0

        def __enter__(self):
            self._count += 1

        def __exit__(self, exc_type, exc_val, exc_tb):
            self._count -= 1

        def __bool__(self):
            return self._count > 0

    _writer: io.IOBase
    _filename_template: str
    _split_strategy: SplitStrategyCallable
    _current_logfile: pathlib.Path

    def __init__(
        self,
        base_dir,
        filename_template,
        split_strategy: Optional[SplitStrategyCallable],
        *,
        encoding="utf-8",
        open_on_creation=True,
        overwrite_existing=False,
    ) -> None:
        self._writer = None
        self._current_logfile = None
        self._filename_template = filename_template
        self._base_dir = pathlib.Path(str(base_dir))
        self._encoding = encoding
        self._open_mode = "wb" if overwrite_existing else "ab"
        self._split_lock = _AutoSplitLogWriter.ReentrantCounter()

        self._split_strategy = (
            (lambda *_: None) if split_strategy is None else split_strategy
        )

        self._stats = LogMetadata(self)

        if open_on_creation:
            self.open()

    def _apply_filename_template(self, provider_supplied):
        if provider_supplied is None:
            return self._filename_template
        if isinstance(provider_supplied, str):
            return provider_supplied
        if isinstance(provider_supplied, Iterable):
            return self._filename_template.format(*provider_supplied)

        raise ValueError(
            "Filename provider must return either a string or an iterable of strings"
        )

    def make_logfile_path(self, provider_supplied):
        return self._base_dir / self._apply_filename_template(provider_supplied)

    def _create_logfile(self):
        expected_logfile = self.make_logfile_path(self._split_strategy(self._stats))
        if expected_logfile != self._current_logfile:
            if self._writer is not None:
                self._writer.close()
            expected_logfile.parent.mkdir(parents=True, exist_ok=True)
            self._current_logfile = expected_logfile
            self._writer = open(self._current_logfile, self._open_mode)

    def _check_open(self):
        if self._writer is None:
            raise ValueError("Writer not opened")

    def write(self, __s):
        self._check_open()
        if not self._split_lock:
            self._create_logfile()

        print("writing")
        bytes = __s.encode(self._encoding)
        self._stats.written_bytes += len(bytes)
        self._writer.write(bytes)

    def writelines(self, __lines: Iterable[str]) -> None:
        for line in __lines:
            self.write(line + "\n")

    def open(self):
        self._create_logfile()

    def __enter__(self):
        if self._writer is None:
            self.open()

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.close()

    def flush(self):
        self._writer.flush()

    def close(self):
        if self._writer is not None:
            self._writer.close()

    def split_lock(self):
        return self._split_lock


class Logger:
    def __init__(self, whom, style: LogStyle = None):
        self.whom: any = whom
        self.style: LogStyle = style
        self.file_writer = None

    def __call__(self, whom: any = None, style: LogStyle = None) -> "Logger":
        if whom is None:
            return DEFAULT_LOGGER
        if whom in loggers_dict:
            return loggers_dict[whom]
        loggers_dict[whom] = Logger(whom=whom, style=style)
        return loggers_dict[whom]

    def log(
        self,
        *content,
        prefix: str = None,
        datetime_format: str = None,
        with_identifier: bool = None,
        with_datetime: bool = None,
        into_file: bool = True,
        into_stdout: bool = True,
        traceback=2,
    ):
        _caller_identity = get_caller_identity_traceback(traceback=traceback)

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
            _whom = str(self.whom)  # check identity
            id_seq = []
            if self.whom is None:  # if using default logger, tracing back to the caller
                file_level = True
                _whom = ""
                if _caller_identity.module_name and _style.trace_level >= 2:
                    # trace as module level
                    id_seq.append(_caller_identity.module_name)
                    file_level = False
                if _caller_identity.class_name and _style.trace_level >= 1:
                    # trace as class level
                    id_seq.append(_caller_identity.class_name)
                    file_level = False
                if file_level and _style.trace_level >= 1:
                    id_seq.append(
                        _caller_identity.filename
                    )  # not module level and class level
            if _caller_identity.func_name != "<module>":
                id_seq.append(_caller_identity.func_name)  # skip for jupyters
            for i in range(len(id_seq)):
                if len(_whom) != 0:
                    _whom += _style.split_char_identity
                _whom += id_seq[i]

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
                + "\n"
            )
        return self

    def ok(self, *message, flag="OK"):
        if _global_log_level >= LogLevel.INFO:
            self.log(
                *message,
                prefix=f"[{colored(flag, AnsiColor.GREEN)}]",
                into_file=False,
                traceback=3,
            )
            self.log(*message, prefix=flag, into_stdout=False, traceback=3)
        return self

    def debug(self, *message, flag=f"DEBUG"):
        if _global_log_level >= LogLevel.DEBUG:
            self.log(
                *message,
                prefix=f"[{colored(flag, AnsiColor.CYAN)}]",
                into_file=False,
                traceback=3,
            )
            self.log(*message, prefix=flag, into_stdout=False, traceback=3)
        return self

    def info(self, *message, flag="INFO"):
        if _global_log_level >= LogLevel.INFO:
            self.log(
                *message,
                prefix=f"[{colored(flag, AnsiColor.WHITE)}]",
                into_file=False,
                traceback=3,
            )
            self.log(*message, prefix=flag, into_stdout=False, traceback=3)
        return self

    def warn(self, *message, flag="WARNING"):
        if _global_log_level >= LogLevel.WARNING:
            self.log(
                *message,
                prefix=f"[{colored(flag, AnsiColor.YELLOW)}]",
                into_file=False,
                traceback=3,
            )
            self.log(*message, prefix=flag, into_stdout=False, traceback=3)
        return self

    def err(self, err, flag="ERROR", reraise=False):
        if type(err) is not Exception:
            err = RuntimeError(str(err))
        if _global_log_level >= LogLevel.ERROR:
            self.log(
                str(err),
                prefix=f"[{colored(flag,AnsiColor.RED)}]",
                into_file=False,
                traceback=3,
            )
            self.log(str(err), prefix=flag, into_stdout=False, traceback=3)
        if reraise:
            raise err
        return self

    def catch(
        self, exception_type=Exception, *, reraise=True, handler=None
    ):  # todo add handler interface
        if callable(exception_type) and (
            not isclass(exception_type) or not issubclass(exception_type, BaseException)
        ):
            return self.catch()(exception_type)
        logger = self

        class Catcher:
            def __init__(self, from_decorator):
                self._from_decorator = from_decorator

            def __enter__(self):
                return None

            def __exit__(self, type_, value, traceback_):
                if type_ is None:
                    return
                if not issubclass(type_, exception_type):
                    return False
                from_decorator = self._from_decorator
                catch_options = [(type_, value, traceback_)]
                if handler:
                    handler(traceback_)
                # logger.log(
                #     from_decorator, catch_options, traceback=4 if from_decorator else 3
                # )
                # todo add reraise functions
                return not reraise

            def __call__(self, function):
                if isclass(function):
                    raise TypeError(
                        "Invalid object decorated with 'catch()', it must be a function, "
                        "not a class (tried to wrap '%s')" % function.__name__
                    )

                catcher = Catcher(True)

                if iscoroutinefunction(function):

                    async def catch_wrapper(*args, **kwargs):
                        with catcher:
                            return await function(*args, **kwargs)

                elif isgeneratorfunction(function):

                    def catch_wrapper(*args, **kwargs):
                        with catcher:
                            return (yield from function(*args, **kwargs))

                else:

                    def catch_wrapper(*args, **kwargs):
                        with catcher:
                            return function(*args, **kwargs)

                functools.update_wrapper(catch_wrapper, function)
                return catch_wrapper

        return Catcher(False)

    def banner(self, text, font: Optional[str] = None):        
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
                if (
                    file[0] not in FigletFont.getFonts()
                ):  # no installed file match the file name
                    try:
                        self.info(
                            f"{file[0]} is not installed. Trying to install as a fontfile."
                        )
                        FigletFont.installFonts(f"res/flfs/{font}.flf")
                    except:
                        self.err("Could not install font {font}. Fallback to default.")
                        font = None
                else:
                    font = file[0]
        f = Figlet(font)
        self.log(f.renderText(text), with_datetime=False, with_identifier=False)
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
        if not path:
            self._bind_file(None)
            return self
        if not path:
            self._bind_file(None)
            return self
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
        if not path:
            self.file_writer = None
            return self
        if not path:
            self.file_writer = None
            return self
        log_file_identity = os.path.abspath(path)
        if os.path.isdir(log_file_identity):
            raise Exception("Target path is not a file.")
        filename = utils.legal_file_name_of(os.path.basename(path))
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
        return self.file_writer != None


DEFAULT_LOGGER = Logger(None)
