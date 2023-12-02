import functools
import json
import sqlite3
from datetime import datetime, timedelta
from enum import Enum
from importlib.metadata import version
from typing import List, Tuple, Union

from neetbox.config import get_module_level_config
from neetbox.logging import logger
from neetbox.logging.formatting import LogStyle

logger = logger("NEETBOX HISTORY", LogStyle(skip_writers=["ws", "file"]))

NEETBOX_VERSION = version("neetbox")
HISTORY_FILE_ROOT = "history"
HISTORY_FILE_TYPE_NAME = "neethistory"
DATETIME_FORMAT = "%Y-%m-%dT%H:%M:%S.%f"  # YYYY-MM-DDTHH:MM:SS.SSS


class FetchType(Enum):
    ALL = "all"
    ONE = "one"
    MANY = "many"


class SortType(Enum):
    ASC = "asc"
    DESC = "desc"


ID_COLUMN_NAME = "id"
TIMESTAMP_COLUMN_NAME = "timestamp"
DATA_COLUMN_NAME = "data"


class QueryCondition:
    def __init__(
        self,
        id_range: Union[Tuple[int, int], int] = None,
        timestamp_range: Union[Tuple[str, str], str] = None,
        limit: int = None,
        order: Union[List[Tuple[str, SortType]], Tuple[str, SortType]] = [],
    ) -> None:
        self.id_range = id_range if isinstance(id_range, tuple) else (id_range, None)
        self.timestamp_range = (
            timestamp_range if isinstance(timestamp_range, tuple) else (timestamp_range, None)
        )
        self.limit = limit
        self.order = order if isinstance(order, list) else [order]

    @functools.lru_cache()
    def dumps(self):
        _id_cond = ""
        if self.id_range[0]:
            _id_0, _id_1 = self.id_range
            _id_cond = (
                f"{ID_COLUMN_NAME}=={_id_0}"
                if _id_1 is None
                else f"{ID_COLUMN_NAME} BETWEEN {_id_0} AND {_id_1}"
            )
        _timestamp_cond = ""
        if self.timestamp_range[0]:
            _ts_0, _ts_1 = self.timestamp_range
            _timestamp_cond = (
                f"{TIMESTAMP_COLUMN_NAME}>='{_ts_0}'"
                if _ts_1 is None
                else f"{TIMESTAMP_COLUMN_NAME} BETWEEN '{_ts_0} AND '{_ts_1}"
            )
        _limit_cond = f"LIMIT {self.limit}" if self.limit else ""
        _order_cond = f"ORDER BY " if self.order else ""
        if self.order:
            for order in self.order:
                _col_name, _sort = order
                if isinstance(_sort, SortType):
                    _sort = _sort.value
                _order_cond += f"{_col_name} {_sort},"
            _order_cond = _order_cond[:-2]  # remove last ','
        query_conditions = []
        for cond in [_id_cond, _timestamp_cond]:
            if cond:
                query_conditions.append(cond)
        query_conditions = " AND ".join(query_conditions)
        limit_and_order = []
        for cond in [_limit_cond, _order_cond]:
            if cond:
                limit_and_order.append(cond)
        limit_and_order = " ".join(limit_and_order)
        if query_conditions:
            query_conditions = f"WHERE {query_conditions}"
        querty_condition_str = f"{query_conditions} {limit_and_order}"
        return querty_condition_str


class DBConnection:
    connection = None
    _path2dbc = {}
    _id2dbc = {}

    def __new__(cls, path=None, **kwargs) -> "DBConnection":
        if path in cls._path2dbc:
            return cls._path2dbc[path]
        new_dbc = super().__new__(cls, **kwargs)
        # connect to sqlite
        new_dbc.connection = sqlite3.connect(path, check_same_thread=False)
        # check neetbox version
        PROJECT_ID = get_module_level_config("@")["workspace-id"]
        _db_file_project_id = new_dbc.fetch_db_project_id(PROJECT_ID)
        if _db_file_project_id != PROJECT_ID:
            raise RuntimeError(
                f"Wrong DB file! reading history of project id '{PROJECT_ID}' from file of project id '{_db_file_project_id}'"
            )
        _db_file_version = new_dbc.fetch_db_version(NEETBOX_VERSION)
        if NEETBOX_VERSION != _db_file_version:
            logger.warn(
                f"History file version not match: reading from version {_db_file_version} with neetbox version {NEETBOX_VERSION}"
            )
        cls._path2dbc[path] = new_dbc
        cls._id2dbc[PROJECT_ID] = new_dbc
        logger.ok(
            f"History file '{path}'(version={_db_file_version}) loaded, project id '{PROJECT_ID}'"
        )
        return new_dbc

    @classmethod
    def items(cls):
        return cls._id2dbc.items()

    @classmethod
    def of_project_id(cls, project_id):
        if project_id in cls._id2dbc:
            return cls._id2dbc[project_id]
        # not exist, create new
        path = f"{HISTORY_FILE_ROOT}/{project_id}.{HISTORY_FILE_TYPE_NAME}"
        return DBConnection(path=path)

    def _execute(self, query, *args, fetch: FetchType = None, save_immediately=True, **kwargs):
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
        return result, cur.lastrowid

    def get_table_names(self):
        sql_query = "SELECT name FROM sqlite_master;"
        table_names, _ = self._execute(sql_query, fetch=FetchType.ALL)
        return table_names

    def fetch_db_version(self, default=None):
        # create if there is no version table
        sql_query = "CREATE TABLE IF NOT EXISTS version ( version TEXT NON NULL );"
        self._execute(sql_query)
        sql_query = "SELECT version FROM version"
        _version, _ = self._execute(sql_query, fetch=FetchType.ONE)
        if _version is None:
            if default is None:
                raise RuntimeError(
                    "should provide a default version if fetching from empty version"
                )
            sql_query = f"INSERT INTO version VALUES (?);"
            self._execute(sql_query, default)
            return default
        return _version[0]

    def fetch_db_project_id(self, default=None):
        # create if there is no projectid table
        sql_query = "CREATE TABLE IF NOT EXISTS projectid ( projectid TEXT NON NULL );"
        self._execute(sql_query)
        sql_query = "SELECT projectid FROM projectid"
        _projectid, _ = self._execute(sql_query, fetch=FetchType.ONE)
        if _projectid is None:
            if default is None:
                raise RuntimeError(
                    "should provide a default project id if fetching from empty project id"
                )
            sql_query = f"INSERT INTO projectid VALUES (?);"
            self._execute(sql_query, default)
            return default
        return _projectid[0]

    def write_json(self, table_name, json_data, timestamp=None):
        # create if there is no version table
        sql_query = f"CREATE TABLE IF NOT EXISTS {table_name} ( id INTEGER PRIMARY KEY AUTOINCREMENT, timestamp TEXT NON NULL, data TEXT NON NULL );"
        self._execute(sql_query)
        _timestamp = timestamp or datetime.now().strftime(DATETIME_FORMAT)
        sql_query = f"INSERT INTO {table_name}(timestamp, data) VALUES (?, ?)"
        if not isinstance(json_data, str):
            json_data = json.dumps(json_data)
        _, lastrowid = self._execute(sql_query, _timestamp, json_data)
        return lastrowid

    def write_blob(self, table_name, json_data, blob_data, timestamp=None):
        if isinstance(blob_data, bytes):
            blob_data = bytearray(blob_data)
        if not isinstance(json_data, str):
            json_data = json.dumps(json_data)
        # create if there is no version table
        sql_query = f"CREATE TABLE IF NOT EXISTS {table_name} ( id INTEGER PRIMARY KEY AUTOINCREMENT, timestamp TEXT NON NULL, json TEXT, data BLOB NON NULL );"
        self._execute(sql_query)
        _timestamp = timestamp or datetime.now().strftime(DATETIME_FORMAT)
        sql_query = f"INSERT INTO {table_name}(timestamp, json, data) VALUES (?, ?, ?)"
        _, lastrowid = self._execute(sql_query, _timestamp, json_data, blob_data)
        return lastrowid

    def read_json(self, table_name: str, condition: QueryCondition = None):
        return self.read(table_name, ("id", "timestamp", "data"), condition)

    def read_blob(self, table_name: str, condition: QueryCondition = None, meta_only=False):
        return self.read(
            table_name,
            ("id", "timestamp", "json", *(("data",) if not meta_only else ())),
            condition,
        )

    def read(self, table_name: str, columns: Tuple[str], condition: QueryCondition = None):
        condition = condition.dumps() if condition else ""
        sql_query = f"SELECT {', '.join(columns)} FROM {table_name} {condition}"
        result, _ = self._execute(sql_query, fetch=FetchType.ALL)
        return result


if __name__ == "__main__":
    conn = DBConnection(path=".ignore/some.db")
    conn.write_json(
        table_name="test_log",
        json_data={
            "enable": True,
            "host": "localhost",
            "port": 5000,
            "allowIpython": False,
            "mute": True,
            "mode": "detached",
            "uploadInterval": 10,
        },
    )
    for item in conn.read_json(
        table_name="test_log",
        condition=QueryCondition(
            timestamp_range=(datetime.now() - timedelta(days=1)).strftime(DATETIME_FORMAT)
        ),
    ):
        print(item)
        print()
