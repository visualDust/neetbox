import functools
import json
import sqlite3
from datetime import datetime, timedelta
from enum import Enum
from importlib.metadata import version
from typing import Dict, List, Tuple, Union

from neetbox.config import get_module_level_config
from neetbox.logging import logger
from neetbox.logging.formatting import LogStyle

logger = logger("NEETBOX HISTORY", LogStyle(skip_writers=["ws", "file"]))

NEETBOX_VERSION = version("neetbox")
HISTORY_FILE_ROOT = ".neethistory"
HISTORY_FILE_TYPE_NAME = "neetory"
DATETIME_FORMAT = "%Y-%m-%dT%H:%M:%S.%f"  # YYYY-MM-DDTHH:MM:SS.SSS


class FetchType(Enum):
    ALL = "all"
    ONE = "one"
    MANY = "many"


class SortType(Enum):
    ASC = "ASC"
    DESC = "DESC"


# === COLUMN NAMES ===
ID_COLUMN_NAME = "id"
TIMESTAMP_COLUMN_NAME = "timestamp"
SERIES_CLOUMN_NAME = "series"
JSON_COLUMN_NAME = METADATA_COLUMN_NAME = "metadata"
BLOB_COLUMN_NAME = "data"

# === TABLE NAMES ===


class QueryCondition:
    def __init__(
        self,
        id_range: Union[Tuple[int, int], int] = None,
        timestamp_range: Union[Tuple[str, str], str] = None,
        series: str = None,
        limit: int = None,
        order: Dict[str, SortType] = {},
    ) -> None:
        self.id_range = id_range if isinstance(id_range, tuple) else (id_range, None)
        self.timestamp_range = (
            timestamp_range if isinstance(timestamp_range, tuple) else (timestamp_range, None)
        )
        self.series = series
        self.limit = limit
        self.order = {order[0], order[1]} if isinstance(order, tuple) else order

    @classmethod
    def from_json(cls, json_data):
        if isinstance(json_data, str):
            json_data = json.loads(json_data)
        for prop in ["id_range", "timestamp_range", "limit", "order"]:
            assert prop in json_data
        """
        {
            "id_range" : [int,int], # from,to
            "timestamp_range" : [str,str], # from,to
            "series" : str, # series name
            "limit" : int,
            "order" : [
                {"column name" : "ASC/DESC"},
                ...
            ]
        }
        """
        # try load id range
        id_range_str = json_data["id_range"]
        id_range = eval(id_range_str)
        assert isinstance(id_range, list) and len(id_range) == 2
        assert type(id_range[0]) is int
        assert type(id_range[1]) is int
        id_range = tuple(id_range)  # to tuple
        # try load timestamp range
        timestamp_range_str = json_data["timestamp_range"]
        timestamp_range = eval(timestamp_range_str)
        assert isinstance(timestamp_range, list) and len(timestamp_range) == 2
        # datetime.strptime(timestamp_range[0], DATETIME_FORMAT) # try parse to datetime, makesure its valid
        # datetime.strptime(timestamp_range[1], DATETIME_FORMAT)
        timestamp_range = tuple(timestamp_range)
        # try to load series
        series = json["series"]
        # try load limit
        limit = json_data["limit"]
        assert type(limit) is int
        order = json_data["order"]
        assert isinstance(order, dict)
        return QueryCondition(
            id_range=id_range,
            timestamp_range=timestamp_range,
            series=series,
            limit=limit,
            order=order,
        )

    @functools.lru_cache()
    def dumps(self):
        # === id condition ===
        _id_cond = ""
        if self.id_range[0]:
            _id_0, _id_1 = self.id_range
            _id_cond = (
                f"{ID_COLUMN_NAME}=={_id_0}"
                if _id_1 is None
                else f"{ID_COLUMN_NAME} BETWEEN {_id_0} AND {_id_1}"
            )
        # === timestamp condition ===
        _timestamp_cond = ""
        if self.timestamp_range[0]:
            _ts_0, _ts_1 = self.timestamp_range
            _timestamp_cond = (
                f"{TIMESTAMP_COLUMN_NAME}>='{_ts_0}'"
                if _ts_1 is None
                else f"{TIMESTAMP_COLUMN_NAME} BETWEEN '{_ts_0} AND '{_ts_1}"
            )
        # === series condition ===
        _series_cond = ""
        if self.series:
            _series_cond = f"{SERIES_CLOUMN_NAME} == {self.series}"
        # === ORDER BY ===
        _order_cond = f"ORDER BY " if self.order else ""
        if self.order:
            for _col_name, _sort in self.order.items():
                _order_cond += (
                    f"{_col_name} {_sort.value if isinstance(_sort,SortType) else _sort}, "
                )
            _order_cond = _order_cond[:-2]  # remove last ','
        # === LIMIT ===
        _limit_cond = f"LIMIT {self.limit}" if self.limit else ""
        # === concat conditions ===
        query_conditions = []
        for cond in [_id_cond, _timestamp_cond, _series_cond]:
            if cond:
                query_conditions.append(cond)
        query_conditions = " AND ".join(query_conditions)
        # === concat order by and limit ===
        order_and_limit = []
        for cond in [_order_cond, _limit_cond]:
            if cond:
                order_and_limit.append(cond)
        order_and_limit = " ".join(order_and_limit)
        # result
        if query_conditions:
            query_conditions = f"WHERE {query_conditions}"
        querty_condition_str = f"{query_conditions} {order_and_limit}"
        return querty_condition_str


class DBConnection:
    connection = None
    _path2dbc = {}
    _id2dbc = {}

    def __new__(cls, project_id: str = None, path: str = None, **kwargs) -> "DBConnection":
        if path is None:  # make path from project id
            path = f"{HISTORY_FILE_ROOT}/{project_id}.{HISTORY_FILE_TYPE_NAME}"
        if path in cls._path2dbc:
            return cls._path2dbc[path]
        if project_id in cls._id2dbc:
            return cls._id2dbc[project_id]
        new_dbc = super().__new__(cls, **kwargs)
        # connect to sqlite
        new_dbc.connection = sqlite3.connect(path, check_same_thread=False)
        # check neetbox version
        _db_file_project_id = new_dbc.fetch_db_project_id(project_id)
        project_id = project_id or _db_file_project_id
        if _db_file_project_id != project_id:
            raise RuntimeError(
                f"Wrong DB file! reading history of project id '{project_id}' from file of project id '{_db_file_project_id}'"
            )
        _db_file_version = new_dbc.fetch_db_version(NEETBOX_VERSION)
        if NEETBOX_VERSION != _db_file_version:
            logger.warn(
                f"History file version not match: reading from version {_db_file_version} with neetbox version {NEETBOX_VERSION}"
            )
        cls._path2dbc[path] = new_dbc
        cls._id2dbc[project_id] = new_dbc
        logger.ok(f"History file(version={_db_file_version}) for project id '{project_id}' loaded.")
        return new_dbc

    @classmethod
    def items(cls):
        return cls._id2dbc.items()

    @classmethod
    def of_project_id(cls, project_id):
        if project_id in cls._id2dbc:
            return cls._id2dbc[project_id]
        return DBConnection(project_id)

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
        sql_query = f"CREATE TABLE IF NOT EXISTS {table_name} ( id INTEGER PRIMARY KEY AUTOINCREMENT, timestamp TEXT NON NULL, json TEXT NON NULL );"
        self._execute(sql_query)
        _timestamp = timestamp or datetime.now().strftime(DATETIME_FORMAT)
        sql_query = f"INSERT INTO {table_name}(timestamp, json) VALUES (?, ?)"
        if not isinstance(json_data, str):
            json_data = json.dumps(json_data)
        _, lastrowid = self._execute(sql_query, _timestamp, json_data)
        return lastrowid

    def write_blob(self, table_name, meta_data, blob_data, series=None, timestamp=None):
        if isinstance(blob_data, bytes):
            blob_data = bytearray(blob_data)
        if not isinstance(meta_data, str):
            meta_data = json.dumps(meta_data)
        # create if there is no version table
        sql_query = f"CREATE TABLE IF NOT EXISTS {table_name} ( id INTEGER PRIMARY KEY AUTOINCREMENT, timestamp TEXT NON NULL, series TEXT, meta TEXT, data BLOB NON NULL );"
        self._execute(sql_query)
        _timestamp = timestamp or datetime.now().strftime(DATETIME_FORMAT)
        series = meta_data["series"] if "series" in meta_data else series
        sql_query = f"INSERT INTO {table_name}(timestamp, series, meta, data) VALUES (?, ?, ?, ?)"
        _, lastrowid = self._execute(sql_query, _timestamp, series, meta_data, blob_data)
        return lastrowid

    def read_json(self, table_name: str, condition: QueryCondition = None):
        condition = condition.dumps() if condition else ""
        sql_query = f"SELECT {', '.join(('id', 'timestamp', 'json'))} FROM {table_name} {condition}"
        result, _ = self._execute(sql_query, fetch=FetchType.ALL)
        return result

    def read_blob(
        self, table_name: str, series: str = None, condition: QueryCondition = None, meta_only=False
    ):
        condition = condition.dumps() if condition else ""
        sql_query = f"SELECT {', '.join(('id', 'timestamp', 'meta', *(('data',) if not meta_only else ())))} FROM {table_name} {condition}"

        return


if __name__ == "__main__":
    conn = DBConnection(project_id="test_project_id", path=".ignore/some.db")
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
