import collections
import json
import sqlite3
from datetime import datetime
from random import random
from typing import Dict, Tuple, Union

from neetbox._daemon._protocol import *
from neetbox.logging import logger
from neetbox.logging.formatting import LogStyle

logger = logger("NEETBOX", LogStyle(skip_writers=["ws", "file"]))


class QueryCondition:
    def __init__(
        self,
        id: Union[Tuple[int, int], int] = None,
        timestamp: Union[Tuple[str, str], str] = None,
        series: str = None,
        run_id: Union[str, int] = None,
        limit: int = None,
        order: Dict[str, DbQuerySortType] = {},
    ) -> None:
        self.id_range = id if isinstance(id, tuple) else (id, None)
        self.timestamp_range = timestamp if isinstance(timestamp, tuple) else (timestamp, None)
        self.series = series
        self.run_id = run_id
        self.limit = limit
        self.order = {order[0], order[1]} if isinstance(order, tuple) else order

    @classmethod
    def from_json(cls, json_data):
        if isinstance(json_data, str):
            json_data = json.loads(json_data)
        """
        {
            "id" : [int,int], # from,to
            "timestamp" : [str,str], # from,to
            "series" : str, # series name
            "limit" : int,
            "order" : [
                {"column name" : "ASC/DESC"},
                ...
            ]
        }
        """
        # try load id range
        id_range = None
        if ID_COLUMN_NAME in json_data:
            id_range_str = json_data[ID_COLUMN_NAME]
            id_range = eval(id_range_str)
            assert (
                isinstance(id_range, list)
                and len(id_range) == 2
                and type(id_range[0]) is int
                and type(id_range[1]) is int
                or type(id_range) is int
            )
            id_range = tuple(id_range)  # to tuple
        # try load timestamp range
        timestamp_range = None
        if TIMESTAMP_COLUMN_NAME in json_data:
            timestamp_range_str = json_data[TIMESTAMP_COLUMN_NAME]
            timestamp_range = eval(timestamp_range_str)
            assert (
                isinstance(timestamp_range, list)
                and len(timestamp_range) == 2
                and type(timestamp_range[0]) is str
                and type(timestamp_range[1]) is str
                or type(timestamp_range) is str
            )
            # datetime.strptime(timestamp_range[0], DATETIME_FORMAT) # try parse to datetime, makesure its valid
            # datetime.strptime(timestamp_range[1], DATETIME_FORMAT)
            timestamp_range = tuple(timestamp_range)
        # try to load series
        series = json_data[SERIES_COLUMN_NAME] if SERIES_COLUMN_NAME in json_data else None
        # run-id cond
        run_id = json_data[RUN_ID_COLUMN_NAME] if RUN_ID_COLUMN_NAME in json_data else None
        # try load limit
        limit = None
        if "limit" in json_data:
            limit = json_data["limit"]
            assert type(limit) is int
        # try load order
        order = None
        if "order" in json_data:
            order = json_data["order"]
            assert isinstance(order, dict)
        return QueryCondition(
            id=id_range,
            timestamp=timestamp_range,
            series=series,
            run_id=run_id,
            limit=limit,
            order=order,
        )

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
            _series_cond = f"{SERIES_COLUMN_NAME} == '{self.series}'"
        # === run-id condition ===
        _run_id_cond = ""
        if self.run_id:
            _run_id_cond = f"{RUN_ID_COLUMN_NAME} == {self.run_id}"
        # === ORDER BY ===
        _order_cond = f"ORDER BY " if self.order else ""
        if self.order:
            for _col_name, _sort in self.order.items():
                _order_cond += (
                    f"{_col_name} {_sort.value if isinstance(_sort,DbQuerySortType) else _sort}, "
                )
            _order_cond = _order_cond[:-2]  # remove last ','
        # === LIMIT ===
        _limit_cond = f"LIMIT {self.limit}" if self.limit else ""
        # === concat conditions ===
        query_conditions = []
        for cond in [_id_cond, _timestamp_cond, _series_cond, _run_id_cond]:
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
        query_condition_str = f"{query_conditions} {order_and_limit}"
        return query_condition_str


class DBConnection:
    # static things
    _path2dbc = {}
    _id2dbc = {}

    # not static. instance level vars
    connection: sqlite3.Connection
    _inited_tables: collections.defaultdict

    def __new__(cls, project_id: str = None, path: str = None, **kwargs) -> "DBConnection":
        if path is None:  # make path from project id
            path = f"{HISTORY_FILE_ROOT}/{project_id}.{HISTORY_FILE_TYPE_NAME}"
        if path in cls._path2dbc:
            return cls._path2dbc[path]
        if project_id in cls._id2dbc:
            return cls._id2dbc[project_id]
        new_dbc = super().__new__(cls, **kwargs)
        # connect to sqlite
        new_dbc.connection = sqlite3.connect(path, check_same_thread=False, isolation_level=None)
        new_dbc.connection.execute("pragma journal_mode=wal")  # set journal mode WAL
        new_dbc.connection.execute("PRAGMA foreign_keys = ON")  # enable foreign keys features
        new_dbc._inited_tables = collections.defaultdict(lambda: False)
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

    def _execute(self, query, *args, fetch: DbQueryFetchType = DbQueryFetchType.ALL, **kwargs):
        cur = self.connection.cursor()
        # logger.info(f"executing sql='{query}', params={args}")
        result = cur.execute(query, args)
        if fetch:
            if fetch == DbQueryFetchType.ALL:
                result = result.fetchall()
            elif fetch == DbQueryFetchType.ONE:
                result = result.fetchone()
            elif fetch == DbQueryFetchType.MANY:
                result = result.fetchmany(kwargs["many"])
        return result, cur.lastrowid

    def _query(self, query, *args, fetch: DbQueryFetchType = DbQueryFetchType.ALL, **kwargs):
        return self._execute(query, *args, fetch=fetch, **kwargs)

    def table_exist(self, table_name):
        sql_query = f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}';"
        result, _ = self._query(sql_query, fetch=DbQueryFetchType.ALL)
        return result != []

    def get_table_names(self):
        sql_query = "SELECT name FROM sqlite_master;"
        table_names, _ = self._query(sql_query, fetch=DbQueryFetchType.ALL)
        return table_names

    def fetch_db_version(self, default=None):
        if not self._inited_tables[VERSION_TABLE_NAME]:  # create if there is no version table
            sql_query = f"CREATE TABLE IF NOT EXISTS {VERSION_TABLE_NAME} ( {VERSION_TABLE_NAME} TEXT NON NULL );"
            self._execute(sql_query)
            self._inited_tables[VERSION_TABLE_NAME] = True
        sql_query = f"SELECT {VERSION_TABLE_NAME} FROM {VERSION_TABLE_NAME}"
        _version, _ = self._query(sql_query, fetch=DbQueryFetchType.ONE)
        if _version is None:
            if default is None:
                raise RuntimeError(
                    "should provide a default version if fetching from empty version"
                )
            sql_query = f"INSERT INTO {VERSION_TABLE_NAME} VALUES (?);"
            self._execute(sql_query, default)
            return default
        return _version[0]

    def fetch_db_project_id(self, default=None):
        if not self._inited_tables[PROJECT_ID_TABLE_NAME]:  # create if there is no projectid table
            sql_query = f"CREATE TABLE IF NOT EXISTS {PROJECT_ID_TABLE_NAME} ( {PROJECT_ID_TABLE_NAME} TEXT NON NULL );"
            self._execute(sql_query)
            self._inited_tables[PROJECT_ID_TABLE_NAME] = True
        sql_query = f"SELECT {PROJECT_ID_TABLE_NAME} FROM {PROJECT_ID_TABLE_NAME}"
        _projectid, _ = self._query(sql_query, fetch=DbQueryFetchType.ONE)
        if _projectid is None:
            if default is None:
                raise RuntimeError(
                    "should provide a default project id if fetching from empty project id"
                )
            sql_query = f"INSERT INTO {PROJECT_ID_TABLE_NAME} VALUES (?);"
            self._execute(sql_query, default)
            return default
        return _projectid[0]

    def fetch_id_of_run_id(self, run_id: str, timestamp: str = None):
        if not self._inited_tables[RUN_IDS_TABLE_NAME]:  # create if there is no version table
            sql_query = f"CREATE TABLE IF NOT EXISTS {RUN_IDS_TABLE_NAME} ( {ID_COLUMN_NAME} INTEGER PRIMARY KEY AUTOINCREMENT, {RUN_ID_COLUMN_NAME} TEXT NON NULL, {TIMESTAMP_COLUMN_NAME} TEXT NON NULL, {METADATA_COLUMN_NAME} TEXT, CONSTRAINT run_id_unique UNIQUE ({RUN_ID_COLUMN_NAME}));"
            self._execute(sql_query)
            self._inited_tables[RUN_IDS_TABLE_NAME] = True
        sql_query = f"SELECT {ID_COLUMN_NAME} FROM {RUN_IDS_TABLE_NAME} WHERE {RUN_ID_COLUMN_NAME} == '{run_id}'"
        _id, _ = self._query(sql_query, fetch=DbQueryFetchType.ONE)
        if _id is None:
            timestamp = timestamp or datetime.now().strftime(DATETIME_FORMAT)
            sql_query = f"INSERT INTO {RUN_IDS_TABLE_NAME}({RUN_ID_COLUMN_NAME}, {TIMESTAMP_COLUMN_NAME}) VALUES (?, ?)"
            _, lastrowid = self._execute(sql_query, run_id, timestamp)
            return lastrowid
        return _id[0]

    def fetch_metadata_of_run_id(self, run_id: str, metadata: Union[dict, str] = None):
        id = self.fetch_id_of_run_id(run_id=run_id)
        if metadata:  # if update name
            metadata = json.dumps(metadata) if isinstance(metadata, dict) else metadata
            sql_query = f"UPDATE {RUN_IDS_TABLE_NAME} SET {METADATA_COLUMN_NAME} = ? WHERE {ID_COLUMN_NAME} = ?"
            _, _ = self._execute(sql_query, metadata, id)
        # get name
        sql_query = f"SELECT {METADATA_COLUMN_NAME} FROM {RUN_IDS_TABLE_NAME} WHERE {ID_COLUMN_NAME} == {id}"
        (metadata,), _ = self._query(sql_query, fetch=DbQueryFetchType.ONE)
        metadata = (
            json.loads(metadata) if metadata else {}
        )  # if does not have metadata, return an empty one
        return metadata

    def run_id_of_id(self, id_of_run_id):
        sql_query = f"SELECT {RUN_ID_COLUMN_NAME} FROM {RUN_IDS_TABLE_NAME} WHERE {ID_COLUMN_NAME} == {id_of_run_id}"
        run_id, _ = self._query(sql_query, fetch=DbQueryFetchType.ONE)
        return run_id[0]

    def get_run_ids(self):
        if not self.table_exist(RUN_IDS_TABLE_NAME):
            raise RuntimeError("should not get run id of id before run id table creation")
        sql_query = f"SELECT {RUN_ID_COLUMN_NAME}, {TIMESTAMP_COLUMN_NAME}, {METADATA_COLUMN_NAME} FROM {RUN_IDS_TABLE_NAME}"
        result, _ = self._query(sql_query)
        result = [
            (run_id, timestamp, json.loads(metadata) if metadata else {})
            for run_id, timestamp, metadata in result
        ]
        return result

    def delete_run_id(self, run_id: str):
        sql_query = f"DELETE FROM {RUN_IDS_TABLE_NAME} where {RUN_ID_COLUMN_NAME} = ?"
        _, _ = self._execute(sql_query, run_id)

    def get_series_of_table(self, table_name, run_id=None):
        if not self.table_exist(table_name):
            return []
        if run_id is not None:
            sql_query = f"SELECT DISTINCT t.series as series FROM {table_name} t RIGHT JOIN {RUN_IDS_TABLE_NAME} r ON r.runid == ? WHERE t.runid == r.id"
            args = (run_id,)
        else:
            sql_query = f"SELECT DISTINCT series FROM {table_name}"
            args = ()
        result, _ = self._query(sql_query, *args, fetch=DbQueryFetchType.ALL)
        return [result for (result,) in result]

    def do_limit_num_row_for(self, table_name: str, run_id: str, num_row_limit: int):
        if num_row_limit <= 0:  # no limit or random not triggered
            return
        sql_query = f"SELECT count(*) from {table_name} WHERE {RUN_ID_COLUMN_NAME} = {run_id}"  # count rows for runid in specific table
        num_rows, _ = self._query(sql_query, fetch=DbQueryFetchType.ONE)
        if num_rows[0] > num_row_limit:  # num rows exceeded limit
            sql_query = f"SELECT {ID_COLUMN_NAME} from {table_name} WHERE {RUN_ID_COLUMN_NAME} = {run_id} ORDER BY {ID_COLUMN_NAME} DESC LIMIT 1 OFFSET {num_row_limit - 1}"  # get max id to delete of row for specific run id
            max_id_to_del, _ = self._query(sql_query, fetch=DbQueryFetchType.ONE)
            sql_query = f"DELETE FROM {table_name} WHERE {ID_COLUMN_NAME} < {max_id_to_del[0]} AND {RUN_ID_COLUMN_NAME} = {run_id}"
            self._query(sql_query)  # delete rows with smaller id and specific run id

    def write_json(
        self,
        table_name: str,
        json_data: str,
        series: str = None,
        run_id: str = None,
        timestamp: str = None,
        num_row_limit=-1,
    ):
        if not isinstance(json_data, dict):
            json_data = json.loads(json_data)
        if run_id:
            run_id = self.fetch_id_of_run_id(run_id, timestamp=timestamp)
        if not self._inited_tables[table_name]:  # create if there is no version table
            sql_query = f"CREATE TABLE IF NOT EXISTS {table_name} ( {ID_COLUMN_NAME} INTEGER PRIMARY KEY AUTOINCREMENT, {TIMESTAMP_COLUMN_NAME} TEXT NON NULL, {SERIES_COLUMN_NAME} TEXT, {RUN_ID_COLUMN_NAME} INTEGER, {JSON_COLUMN_NAME} TEXT NON NULL, FOREIGN KEY({RUN_ID_COLUMN_NAME}) REFERENCES {RUN_IDS_TABLE_NAME}({ID_COLUMN_NAME}) ON DELETE CASCADE);"
            self._execute(sql_query)
            sql_query = f"CREATE INDEX IF NOT EXISTS series_and_runid_index ON {table_name} ({SERIES_COLUMN_NAME}, {RUN_ID_COLUMN_NAME})"
            self._execute(sql_query)
            self._inited_tables[table_name] = True

        sql_query = f"INSERT INTO {table_name}({TIMESTAMP_COLUMN_NAME}, {SERIES_COLUMN_NAME}, {RUN_ID_COLUMN_NAME}, {JSON_COLUMN_NAME}) VALUES (?, ?, ?, ?)"
        if isinstance(json_data, dict):
            json_data = json.dumps(json_data)
        _, lastrowid = self._execute(sql_query, timestamp, series, run_id, json_data)
        self.do_limit_num_row_for(table_name, run_id, num_row_limit)
        return lastrowid

    def read_json(self, table_name: str, condition: QueryCondition = None):
        if not self.table_exist(table_name):
            return []
        if isinstance(condition.run_id, str):
            condition.run_id = self.fetch_id_of_run_id(condition.run_id)  # convert run id
        condition = condition.dumps() if condition else ""
        sql_query = f"SELECT {', '.join((ID_COLUMN_NAME, TIMESTAMP_COLUMN_NAME,SERIES_COLUMN_NAME, JSON_COLUMN_NAME))} FROM {table_name} {condition}"
        result, _ = self._query(sql_query, fetch=DbQueryFetchType.ALL)
        try:
            result = [
                {
                    ID_COLUMN_NAME: w,
                    TIMESTAMP_COLUMN_NAME: x,
                    SERIES_COLUMN_NAME: y,
                    JSON_COLUMN_NAME: json.loads(z),
                }
                for w, x, y, z in result
            ]
        except:
            print(result)
            raise
        return result

    def set_status(self, run_id: str, series: str, json_data):
        if not (isinstance(json_data, str) or isinstance(json_data, dict)):
            raise
        if isinstance(json_data, str):
            json_data = json.loads(json_data)
        if run_id:
            run_id = self.fetch_id_of_run_id(run_id)
        if not self._inited_tables[STATUS_TABLE_NAME]:  # create if there is no version table
            sql_query = f"CREATE TABLE IF NOT EXISTS {STATUS_TABLE_NAME} ({ID_COLUMN_NAME} INTEGER PRIMARY KEY,{RUN_ID_COLUMN_NAME} INTEGER NON NULL, {SERIES_COLUMN_NAME} TEXT NON NULL, {JSON_COLUMN_NAME} TEXT NON NULL, UNIQUE({RUN_ID_COLUMN_NAME}, {SERIES_COLUMN_NAME}) ON CONFLICT REPLACE, FOREIGN KEY({RUN_ID_COLUMN_NAME}) REFERENCES {RUN_IDS_TABLE_NAME}({ID_COLUMN_NAME}) ON DELETE CASCADE);"
            self._execute(sql_query)
            self._inited_tables[STATUS_TABLE_NAME] = True
        sql_query = f"INSERT OR REPLACE INTO {STATUS_TABLE_NAME}({RUN_ID_COLUMN_NAME},{SERIES_COLUMN_NAME}, {JSON_COLUMN_NAME}) VALUES (?, ?, ?)"
        if isinstance(json_data, dict):
            json_data = json.dumps(json_data)
        _, lastrowid = self._execute(sql_query, run_id, series, json_data)
        return lastrowid

    def get_status(self, run_id: str = None, series: str = None):
        if not self.table_exist(STATUS_TABLE_NAME):
            return {}
        condition = QueryCondition(run_id=run_id, series=series)
        if isinstance(condition.run_id, str):
            condition.run_id = self.fetch_id_of_run_id(condition.run_id)  # convert run id
        condition = condition.dumps() if condition else ""
        sql_query = f"SELECT {', '.join((RUN_ID_COLUMN_NAME, SERIES_COLUMN_NAME, JSON_COLUMN_NAME))} FROM {STATUS_TABLE_NAME} {condition}"
        query_result, _ = self._query(sql_query, fetch=DbQueryFetchType.ALL)
        result = {}
        for id_of_runid, series_name, value in query_result:
            _run_id = self.run_id_of_id(id_of_runid)
            if _run_id not in result:
                result[_run_id] = {}
            result[_run_id][series_name] = json.loads(value)
        return result

    def write_blob(
        self,
        table_name: str,
        meta_data: Union[str, dict],
        blob_data: bytes,
        series: str = None,
        run_id: str = None,
        timestamp: str = None,
        num_row_limit=-1,
    ):
        meta_data = meta_data or {}
        meta_data = meta_data if isinstance(meta_data, dict) else json.loads(meta_data)
        if run_id:
            run_id = self.fetch_id_of_run_id(run_id, timestamp=timestamp)
        if isinstance(blob_data, bytes):
            blob_data = bytearray(blob_data)
        if isinstance(meta_data, dict):
            meta_data = json.dumps(meta_data)

        if not self._inited_tables[table_name]:  # create if not exist
            sql_query = f"CREATE TABLE IF NOT EXISTS {table_name} ( {ID_COLUMN_NAME} INTEGER PRIMARY KEY AUTOINCREMENT, {TIMESTAMP_COLUMN_NAME} TEXT NON NULL, {SERIES_COLUMN_NAME} TEXT, {RUN_ID_COLUMN_NAME} INTEGER, {METADATA_COLUMN_NAME} TEXT, {BLOB_COLUMN_NAME} BLOB NON NULL, FOREIGN KEY({RUN_ID_COLUMN_NAME}) REFERENCES {RUN_IDS_TABLE_NAME}({ID_COLUMN_NAME}) ON DELETE CASCADE);"
            self._execute(sql_query)
            sql_query = f"CREATE INDEX IF NOT EXISTS series_and_runid_index ON {table_name} ({SERIES_COLUMN_NAME}, {RUN_ID_COLUMN_NAME})"
            self._execute(sql_query)
            self._inited_tables[table_name] = True

        sql_query = f"INSERT INTO {table_name}({TIMESTAMP_COLUMN_NAME}, {SERIES_COLUMN_NAME}, {RUN_ID_COLUMN_NAME}, {METADATA_COLUMN_NAME}, {BLOB_COLUMN_NAME}) VALUES (?, ?, ?, ?, ?)"
        _, lastrowid = self._execute(sql_query, timestamp, series, run_id, meta_data, blob_data)
        self.do_limit_num_row_for(table_name, run_id, num_row_limit)
        return lastrowid

    def read_blob(self, table_name: str, condition: QueryCondition = None, meta_only=False):
        if not self.table_exist(table_name):
            return []
        if isinstance(condition.run_id, str):
            condition.run_id = self.fetch_id_of_run_id(condition.run_id)  # convert run id
        condition = condition.dumps() if condition else ""
        sql_query = f"SELECT {', '.join((ID_COLUMN_NAME,TIMESTAMP_COLUMN_NAME, METADATA_COLUMN_NAME, *((BLOB_COLUMN_NAME,) if not meta_only else ())))} FROM {table_name} {condition}"
        result, _ = self._query(sql_query, fetch=DbQueryFetchType.ALL)
        return result
