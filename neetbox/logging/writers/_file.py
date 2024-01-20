# -*- coding: utf-8 -*-
#
# Author: GavinGong aka VisualDust
# Github: github.com/visualDust
# Date:   20240111

import os

from .._formatting import RawLog


class FileLogWriter:
    # class level static
    PATH2WRITER = {}

    # instance level
    file_writer = None

    def __new__(cls, path):
        path = os.path.abspath(path)
        if os.path.isdir(path):
            raise Exception("Target path is not a file.")
        dirname = os.path.dirname(path) if len(os.path.dirname(path)) != 0 else "."
        if not os.path.exists(dirname):
            os.makedirs(dirname)
        if path in FileLogWriter.PATH2WRITER:
            return FileLogWriter.PATH2WRITER[path]
        new_instance = super().__new__(cls)
        new_instance.file_writer = open(path, "a", encoding="utf-8", buffering=1)
        FileLogWriter.PATH2WRITER[path] = new_instance
        return new_instance

    def write(self, log: RawLog):
        line = " ".join(
            [
                log.timestamp.strftime(r"%Y-%m-%dT%H:%M:%S.%f"),
                f"[{log.series}]" if log.series else "[log]",
                log.caller_info.format(r"%m.%c.%f:%l"),
                str(log.message),
            ]
        )
        self.file_writer.write(line + "\n")
