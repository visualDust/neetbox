import functools
import json
import os
import sqlite3
from datetime import datetime, timedelta
from enum import Enum
from importlib.metadata import version
from typing import List, Tuple, Union

from neetbox.logging import logger
from neetbox.logging.formatting import LogStyle

logger = logger("NEETBOX HISTORY", LogStyle(skip_writers=["ws", "file"]))

NEETBOX_VERSION = version("neetbox")
HISTORY_FILE_ROOT = "history"
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
                f"{ID_COLUMN_NAME}>={_id_0}"
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
        self.connection = sqlite3.connect(db_file, check_same_thread=False)
        # check neetbox version
        _db_file_version = self.get_db_version()
        if NEETBOX_VERSION != _db_file_version:
            logger.warn(
                f"History file version not match: reading from version {_db_file_version} with neetbox version {NEETBOX_VERSION}"
            )
        logger.info(
            f"History file '{db_file}'(version={_db_file_version}) attached for id {workspace_id}"
        )

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
            self._execute(sql_query, NEETBOX_VERSION)
            return NEETBOX_VERSION
        return _version[0]

    def write_json(self, table_name, data, timestamp=None):
        # create if there is no version table
        sql_query = f"CREATE TABLE IF NOT EXISTS {table_name} ( id INTEGER PRIMARY KEY, timestamp text non null, data text non null );"
        self._execute(sql_query)
        _timestamp = timestamp or datetime.now().strftime(DATETIME_FORMAT)
        sql_query = f"INSERT INTO {table_name}(timestamp, data) VALUES (?, ?)"
        if not isinstance(data, str):
            data = json.dumps(data)
        self._execute(sql_query, _timestamp, data)

    def read_json(self, table_name: str, condition: QueryCondition = None):
        condition = condition.dumps() if condition else ""
        print(condition)
        sql_query = f"SELECT id, timestamp, data FROM {table_name} {condition}"
        return self._execute(sql_query, fetch=FetchType.ALL)

    def write_image(self, table_name, data):
        pass  # todo (VisualDust)


def get_history_db(project_id):
    # todo handle thread safe things(?)
    conn = DBConnection(workspace_id=project_id)
    return conn


if __name__ == "__main__":
    conn = DBConnection(path=".ignore/some.db")
    conn.write_json(
        table_name="test_log",
        data={
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
