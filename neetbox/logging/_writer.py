# -*- coding: utf-8 -*-
#
# Author: GavinGong aka VisualDust
# Github: github.com/visualDust
# Date:   20230413

import inspect
import io
import json
import os
import pathlib
from abc import ABC, abstractmethod
from collections import defaultdict
from dataclasses import dataclass
from datetime import date, datetime
from typing import Any, Callable, Iterable, Optional, Union

from rich.console import Console

from neetbox.config import get_project_id, get_run_id
from neetbox.logging.formatting import LogStyle, colored_text, styled_text
from neetbox.utils import formatting
from neetbox.utils.framing import TracebackIdentity


class LogWriter(ABC):
    @abstractmethod
    def write(self, raw_log):
        pass


# ================== DEFINE LOG TYPE =====================


@dataclass
class RawLog:
    rich_msg: str
    style: LogStyle
    caller_identity: TracebackIdentity
    whom: Any = None
    prefix: Optional[str] = None
    datetime_format: Optional[str] = None
    with_identifier: Optional[bool] = None
    with_datetime: Optional[bool] = None
    skip_writers: Optional[list[str]] = None

    def write_by(self, writer: LogWriter) -> bool:
        skip_writers = (self.style.skip_writers or []) + (self.skip_writers or [])
        for swr in skip_writers:
            if isinstance(writer, RawLog.name2writerType[swr]):
                return False  # skip this writer, do not write
        writer.write(self)
        return False

    @property
    def json(self) -> dict:
        default_style = self.style
        # prefix
        prefix = self.prefix or default_style.prefix
        # composing datetime
        with_datetime = (
            default_style.with_datetime if self.with_datetime is None else self.with_datetime
        )
        timestamp = ""
        if with_datetime:
            datetime_fmt = self.datetime_format or default_style.datetime_format
            timestamp = datetime.now().strftime(datetime_fmt)

        # composing identifier
        whom = ""
        with_identifier = (
            default_style.with_identifier if self.with_identifier is None else self.with_identifier
        )
        if with_identifier:
            identity_seq = self.caller_identity.sequence
            if len(identity_seq) > 1:
                identity_seq = identity_seq[1:]
            if len(identity_seq) > self.style.trace_level:
                identity_seq = identity_seq[: self.style.trace_level - 1]
            whom = (
                str(self.whom)
                if self.whom is not None
                else default_style.split_char_identity.join(identity_seq)
            )  # check identity
        return {"series": prefix, "timestamp": timestamp, "whom": whom, "message": self.rich_msg}

    def __repr__(self) -> str:
        return json.dumps(self.json, default=str)


# ================== CONSOLE LOG WRITER =====================


class DefaultDictThatReturnsKeyOnMissing(defaultdict):
    def __missing__(self, key):
        return key


_console_prefix_2_colored_text = DefaultDictThatReturnsKeyOnMissing(
    str,
    {
        "ok": colored_text("[ok]", "green"),
        "debug": colored_text("[debug]", "cyan"),
        "info": colored_text("[info]", "white"),
        "warning": colored_text("[warning]", "yellow"),
        "mention": colored_text("[mention]", "yellow"),
        "error": colored_text("[error]", "red"),
    },
)


class __ConsoleLogWriter(LogWriter):
    _console = Console()

    def write(self, raw_log: RawLog):
        _msg_dict = raw_log.json
        _style = raw_log.style
        _prefix = _msg_dict["series"]
        _prefix = _console_prefix_2_colored_text[_prefix] + " " if _prefix else _prefix
        rich_msg = str(
            _prefix
            + _msg_dict["timestamp"]
            + _style.split_char_cmd * min(len(_msg_dict["timestamp"]), 1)
            + styled_text(_msg_dict["whom"], style=_style)
            + _style.split_char_cmd * min(len(_msg_dict["whom"]), 1)
            + _msg_dict["message"]
        )
        self.__class__._console.print(rich_msg)


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
        _msg_dict = raw_log.json
        _style = raw_log.style
        _series_text = f"[{_msg_dict['series']}]" if _msg_dict["series"] else ""
        text_msg = _style.split_char_txt.join(
            [_msg_dict["timestamp"], _series_text, _msg_dict["whom"], _msg_dict["message"]]
        )
        self.file_writer.write(text_msg + "\n")


# ================== WS LOG WRITER =====================


class _WebSocketLogWriter(LogWriter):
    # class level statics
    connection = None  # connection should be assigned by neetbox._daemon.client._client to avoid recursive import

    def write(self, raw_log: RawLog):
        json_data = raw_log.json
        payload = {"whom": json_data["whom"], "message": json_data["message"]}
        if _WebSocketLogWriter.connection:
            _WebSocketLogWriter.connection.ws_send(
                event_type="log",
                series=json_data["series"],
                payload=payload,
                timestamp=json_data["timestamp"],
            )


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
