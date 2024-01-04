# -*- coding: utf-8 -*-
#
# Author: GavinGong aka VisualDust
# Github: github.com/visualDust
# Date:   20230413

import json
import os
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Optional
from rich.console import Console
from rich.table import Table
from rich.text import Text
from neetbox.logging.formatting import LogStyle
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
            identity_seq = self.caller_identity.as_str_sequence(lineno=False)
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


def prefix2RichText(prefix: str):
    return {
        "ok": Text("[ok]", style="green"),
        "debug": Text("[debug]", style="cyan"),
        "info": Text("[info]", style="white"),
        "warning": Text("[warning]", style="yellow"),
        "mention": Text("[mention]", style="yellow"),
        "error": Text("[error]", style="red"),
    }.get(prefix, Text(prefix))


class __ConsoleLogWriter(LogWriter):
    _console = Console()

    def write(self, raw_log: RawLog):
        msg_dict = raw_log.json
        log_style = raw_log.style
        style = " ".join(
            [x for x in [log_style.console_color, log_style.text_style] if x is not None]
        )
        prefix = msg_dict["series"]
        prefix = prefix2RichText(prefix) if prefix else None
        table = Table(show_header=False, box=None, expand=True)
        table.add_column(justify="left")
        table.add_column(justify="right")
        whom_text = Text(msg_dict["whom"], style)
        split_text = (
            Text(log_style.split_char_cmd, style="dim " + style) if len(msg_dict["whom"]) else ""
        )
        message_text = Text(msg_dict["message"], style="default")
        time_text = Text(msg_dict["timestamp"], style="default dim")
        prefix_and_time = prefix + " " + time_text if prefix else time_text
        table.add_row(whom_text + split_text + message_text, prefix_and_time)
        self.__class__._console.print(table)


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
