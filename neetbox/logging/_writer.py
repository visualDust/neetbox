import inspect
import io
import json
import os
import pathlib
from dataclasses import dataclass
from datetime import date, datetime
from typing import Any, Callable, Iterable, Optional, Union

from rich import print as rprint

from neetbox.logging.formatting import LogStyle, colored_text, styled_text
from neetbox.utils import formatting


# Log writer interface
class LogWriter:
    def write(self, raw_log):
        pass


@dataclass
class RawLog:
    rich_msg: str
    style: LogStyle
    caller_identity: Any
    whom: Any = None
    prefix: Optional[str] = None
    datetime_format: Optional[str] = None
    with_identifier: Optional[bool] = None
    with_datetime: Optional[bool] = None
    skip_writers: Optional[list[str]] = None

    def write_by(self, writer: LogWriter) -> bool:
        if self.skip_writers:  # if skipping any writers
            for swr in self.skip_writers:
                if isinstance(writer, RawLog.name2writerType[swr]):
                    return False  # skip this writer, do not write
        writer.write(self)
        return False

    def json(self) -> dict:
        _default_style = self.style
        # prefix
        _prefix = self.prefix or _default_style.prefix
        # composing datetime
        _with_datetime = self.with_datetime or _default_style.with_datetime
        _datetime = ""
        if _with_datetime:
            _datetime_fmt = self.datetime_format or _default_style.datetime_format
            _datetime = datetime.now().strftime(_datetime_fmt)

        # composing identifier
        _whom = ""
        _with_identifier = self.with_identifier or _default_style.with_identifier
        if _with_identifier:
            _caller_identity = self.caller_identity
            _whom = str(self.whom)  # check identity
            id_seq = []
            if self.whom is None:  # if using default logger, tracing back to the caller
                file_level = True
                _whom = ""
                if _caller_identity.module_name and _default_style.trace_level >= 2:
                    # trace as module level
                    id_seq.append(_caller_identity.module_name)
                    file_level = False
                if _caller_identity.class_name and _default_style.trace_level >= 1:
                    # trace as class level
                    id_seq.append(_caller_identity.class_name)
                    file_level = False
                if file_level and _default_style.trace_level >= 1:
                    id_seq.append(_caller_identity.filename)  # not module level and class level
            if _caller_identity.func_name != "<module>":
                id_seq.append(_caller_identity.func_name)  # skip for jupyters
            for i in range(len(id_seq)):
                if len(_whom) != 0:
                    _whom += _default_style.split_char_identity
                _whom += id_seq[i]
        return {"prefix": _prefix, "datetime": _datetime, "whom": _whom, "msg": self.rich_msg}

    def __repr__(self) -> str:
        return json.dumps(self.json(), default=str)


# ================== CONSOLE LOG WRITER =====================


class __ConsoleLogWriter(LogWriter):
    def write(self, raw_log: RawLog):
        _msg_dict = raw_log.json()
        _style = raw_log.style
        rich_msg = str(
            _msg_dict["prefix"]
            + _msg_dict["datetime"]
            + _style.split_char_cmd * min(len(_msg_dict["datetime"]), 1)
            + styled_text(_msg_dict["whom"], style=_style)
            + _style.split_char_cmd * min(len(_msg_dict["whom"]), 1)
            + _msg_dict["msg"]
        )
        rprint(rich_msg)


# console writer singleton
consoleLogWriter = __ConsoleLogWriter()


# ================== FILE LOG WRITER =====================


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
                return self.make_result(self.file_id + metadata.written_bytes // size_in_bytes)

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

    _writer: Union[io.IOBase, None]
    _filename_template: str
    _split_strategy: Union[SplitStrategyCallable, Callable]
    _current_logfile: Union[pathlib.Path, None]

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

        self._split_strategy = (lambda *_: None) if split_strategy is None else split_strategy

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

        raise ValueError("Filename provider must return either a string or an iterable of strings")

    def make_logfile_path(self, provider_supplied):
        return self._base_dir / self._apply_filename_template(provider_supplied)

    def _create_logfile(self):
        expected_logfile = self.make_logfile_path(self._split_strategy(self._stats))
        if expected_logfile != self._current_logfile:
            if self._writer is not None:
                self._writer.close()
            expected_logfile.parent.mkdir(parents=True, exist_ok=True)
            self._current_logfile = expected_logfile
            self._writer = open(self._current_logfile, self._open_mode)  # type: ignore

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


class FileLogWriter(LogWriter):
    # class level static pool
    PATH_2_FILE_WRITER = {}

    # instance level non-static things
    file_writer = None  # assign in __init__

    def __new__(cls, path, *args, **kwargs):
        # per file, per writer.
        file_abs_path = os.path.abspath(path)
        if os.path.isdir(file_abs_path):
            raise Exception("Target path is not a file.")
        filename = formatting.legal_file_name_of(os.path.basename(path))
        dirname = os.path.dirname(path) if len(os.path.dirname(path)) != 0 else "."
        if not os.path.exists(dirname):
            raise Exception(f"Could not find dictionary {dirname}")
        real_path = os.path.join(dirname, filename)
        if file_abs_path not in FileLogWriter.PATH_2_FILE_WRITER:
            newWriter = LogWriter.__new__(cls)
            newWriter.file_writer = open(real_path, "a", encoding="utf-8", buffering=1)
            FileLogWriter.PATH_2_FILE_WRITER[file_abs_path] = newWriter

        return FileLogWriter.PATH_2_FILE_WRITER[file_abs_path]

    def __init__(self, path) -> None:
        self.file_writer = open(path, "a", encoding="utf-8", buffering=1)

    def write(self, raw_log: RawLog):
        _msg_dict = raw_log.json()
        _style = raw_log.style
        text_msg = (
            _msg_dict["prefix"]
            + _msg_dict["datetime"]
            + _style.split_char_txt * min(len(_msg_dict["datetime"]), 1)
            + _msg_dict["whom"]
            + _style.split_char_txt * min(len(_msg_dict["whom"]), 1)
            + _msg_dict["msg"]
            + "\n"
        )
        self.file_writer.write(text_msg)


# ================== JSON LOG WRITER =====================


class JsonLogWriter(FileLogWriter):
    def write(self, raw_log: RawLog):
        # todo convert to json and write
        pass


# ================== WS LOG WRITER =====================


class __WebSocketLogWriter(LogWriter):
    def __init__(self) -> None:
        pass

    def write(self, raw_log: RawLog):
        pass


webSocketLogWriter = __WebSocketLogWriter()


# ================== POST INIT TYPE REF =====================

RawLog.name2writerType = {
    "console": __ConsoleLogWriter,
    "file": FileLogWriter,
    "json": JsonLogWriter,
}
