import inspect
import io
import json
import os
import pathlib
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import date, datetime
from typing import Any, Callable, Iterable, Optional, Union

from rich import print as rprint

from neetbox.logging.formatting import LogStyle, colored_text, styled_text
from neetbox.utils import formatting


class LogWriter(ABC):
    @abstractmethod
    def write(self, raw_log):
        pass


# ================== DEFINE LOG TYPE =====================


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
        _skip_writers = (self.style.skip_writers or []) + (self.skip_writers or [])
        for swr in _skip_writers:
            if isinstance(writer, RawLog.name2writerType[swr]):
                return False  # skip this writer, do not write
        writer.write(self)
        return False

    def json(self) -> dict:
        _default_style = self.style
        # prefix
        _prefix = self.prefix or _default_style.prefix
        # composing datetime
        _with_datetime = (
            _default_style.with_datetime if self.with_datetime is None else self.with_datetime
        )
        _datetime = ""
        if _with_datetime:
            _datetime_fmt = self.datetime_format or _default_style.datetime_format
            _datetime = datetime.now().strftime(_datetime_fmt)

        # composing identifier
        _whom = ""
        _with_identifier = (
            _default_style.with_identifier if self.with_identifier is None else self.with_identifier
        )
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
        text_msg = str(
            _msg_dict["prefix"]
            + _msg_dict["datetime"]
            + _style.split_char_txt * min(len(_msg_dict["datetime"]), 1)
            + _msg_dict["whom"]
            + _style.split_char_txt * min(len(_msg_dict["whom"]), 1)
            + _msg_dict["msg"]
            + "\n"
        )
        self.file_writer.write(text_msg)


# ================== WS LOG WRITER =====================


class _WebSocketLogWriter(LogWriter):
    # class level statics
    connection = None  # connection should be assigned by neetbox.daemon.client._client to avoid recursive import

    def write(self, raw_log: RawLog):
        json_data = raw_log.json()

        if _WebSocketLogWriter.connection:
            _WebSocketLogWriter.connection.ws_send(event_type="log", payload=json_data)


def _assign_connection_to_WebSocketLogWriter(conn):
    _WebSocketLogWriter.connection = conn


webSocketLogWriter = _WebSocketLogWriter()


# ================== JSON LOG WRITER =====================


class JsonLogWriter(FileLogWriter):
    def write(self, raw_log: RawLog):
        # todo convert to json and write to file
        pass


# ================== POST INIT TYPE REF =====================

RawLog.name2writerType = {
    "stdout": __ConsoleLogWriter,
    "file": FileLogWriter,
    "ws": _WebSocketLogWriter,
    "json": JsonLogWriter,
}
