import os
import sqlite3
from dataclasses import dataclass
from enum import Enum
from importlib.metadata import version

from neetbox.logging import logger
from neetbox.logging.formatting import LogStyle

logger = logger("NEETBOX HISTORY", LogStyle(skip_writers=["ws", "file"]))

# NEETBOX_VERSION = "1111"
NEETBOX_VERSION = version("neetbox")
HISTORY_FILE_ROOT = "history"


# @dataclass
# class DBCommandBuilder:
#     cmd_type = None

#     def NewTable(self):
#         self.cmd_type = ""

#     def build():
#         pass


class FetchType(Enum):
    ALL = "all"
    ONE = "one"
    MANY = "many"


class DBConnection:
    connection = None

    def __init__(self, workspace_id=None, **kwargs):
        if not os.path.exists(HISTORY_FILE_ROOT):
            # create history root dir
            os.mkdir(HISTORY_FILE_ROOT)
        # check if is dir
        if not os.path.isdir(HISTORY_FILE_ROOT):
            raise RuntimeError(f"{HISTORY_FILE_ROOT} is not a directory.")

        if "path" not in kwargs and workspace_id is None:
            raise RuntimeError("please specify workspace id or db file path")
        db_file = (
            kwargs["path"]
            if "path" in kwargs
            else f"{HISTORY_FILE_ROOT}/{workspace_id}.neethistory"
        )
        # connect to sqlite
        self.connection = sqlite3.connect(db_file)
        # check neetbox version
        _db_file_version = self.get_db_version()
        print(_db_file_version, NEETBOX_VERSION)
        if NEETBOX_VERSION != _db_file_version:
            logger.warn(
                f"History file version not match: reading {_db_file_version} with neetbox version {NEETBOX_VERSION}"
            )

    def _execute(self, query, *args, fetch: FetchType = None, save_immediately=False, **kwargs):
        cur = self.connection.cursor()
        # logger.info(f"executing sql='{query}', params={args}")
        result = cur.execute(query, args)
        if fetch:
            if fetch == FetchType.ALL:
                result = result.fetchall()
            elif fetch == FetchType.ONE:
                result = result.fetchone()
            elif fetch == FetchType.MANY:
                result = result.fetchmany(kwargs["many"])
        if save_immediately:
            self.connection.commit()
        return result

    def get_table_names(self):
        sql_query = "SELECT name FROM sqlite_master;"
        table_names = self._execute(sql_query, fetch=FetchType.ALL)
        return table_names

    def get_db_version(self):
        # create if there is no version table
        sql_query = "CREATE TABLE IF NOT EXISTS version ( version );"
        self._execute(sql_query)
        sql_query = "SELECT version FROM version"
        _version = self._execute(sql_query, fetch=FetchType.ONE)
        if _version is None:
            sql_query = f"INSERT INTO version VALUES (?);"
            self._execute(sql_query, (NEETBOX_VERSION), save_immediately=True)
            return NEETBOX_VERSION
        return _version[0]

    def _write(self, table_name, data):
        sql_query = "CREATE TABLE IF NOT EXISTS version ( version );"
        self._execute(sql_query)
        pass

    def write_json(self, table_name, data):
        pass

    def write_image(self, table_name, data):
        pass


if __name__ == "__main__":
    conn = DBConnection(path=".ignore/some.db")
