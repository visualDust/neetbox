# -*- coding: utf-8 -*-
#
# Author: GavinGong aka VisualDust
# Github: github.com/visualDust
# Date:   20230318

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

from vdtoys.framing import TracebackInfo

from neetbox._protocol import *


@dataclass
class LogStyle:
    datetime_format: Optional[str] = r"%Y-%m-%dT%H:%M:%S.%f"
    caller_info_format: Optional[str] = r"%m/%c/%f"


@dataclass
class RawLog:
    message: str
    caller_info: TracebackInfo
    caller_name_alias: Optional[str] = None
    timestamp: datetime = datetime.now()
    series: Optional[str] = None
    style: LogStyle = field(default_factory=LogStyle)  # fix python 3.11 dataclass issue

    @property
    def timestamp_formatted(self):
        return (
            self.timestamp.strftime(self.style.datetime_format)
            if self.style.datetime_format
            else ""
        )

    @property
    def caller_info_formatted(self):
        if self.caller_name_alias:
            return str(self.caller_name_alias)
        return (
            self.caller_info.format(self.style.caller_info_format)
            if self.style.caller_info_format
            else ""
        )

    @property
    def json(self) -> dict:
        return {
            SERIES_KEY: self.series,
            MESSAGE_KEY: self.message,
            TIMESTAMP_KEY: self.timestamp_formatted,
            CALLER_ID_KEY: self.caller_info_formatted,
        }

    def __repr__(self) -> str:
        result = ""
        for k, v in self.json.items():
            result += f"{k}: {v}\n"
        return result
