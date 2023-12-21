# -*- coding: utf-8 -*-
#
# Author: GavinGong aka VisualDust
# Github: github.com/visualDust
# Date:   20231201

import collections
import json
import os
import sqlite3
from datetime import datetime
from typing import Union

from neetbox._protocol import *
from neetbox.logging import LogStyle
from neetbox.logging.logger import Logger
from neetbox.utils import ResourceLoader

from ._condition import *

logger = Logger("NEETBOX", LogStyle(skip_writers=["ws"]))


class DBConnection:
    # static things
    _path2dbc = {}
    _id2dbc = {}

    # not static. instance level vars
    project_id: str  # of which project id
    file_path: str  # where is the db file
    connection: sqlite3.Connection  # the db connection
    _inited_tables: collections.defaultdict

    def __new__(cls, project_id: str = None, path: str = None, **kwargs) -> "DBConnection":
        if path is None and project_id is None:
            raise RuntimeError(f"please provide at least project id or path when creating db")
        if path is None:  # make path from project id
            path = f"{HISTORY_FILE_ROOT}/{project_id}.{HISTORY_FILE_TYPE_NAME}"
        if path in cls._path2dbc:
            return cls._path2dbc[path]
        if project_id in cls._id2dbc:
            return cls._id2dbc[project_id]
        new_dbc = super().__new__(cls, **kwargs)
        # connect to sqlite
        new_dbc.file_path = path
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
        new_dbc.project_id = project_id
        logger.ok(f"History file(version={_db_file_version}) for project id '{project_id}' loaded.")
        return new_dbc

    def finialize(self):
        if self.project_id not in DBConnection._id2dbc:
            logger.err(
                RuntimeError(f"could not find db to delete with project id {self.project_id}")
            )
        del DBConnection._id2dbc[self.project_id]
        del DBConnection._path2dbc[self.file_path]
        logger.info(f"deleting history DB for project id {self.project_id}...")
        if self.connection:
            try:
                self.connection.close()
            except Exception as e:
                logger.err(
                    RuntimeError(
                        f"failed to close DB connection for project id {self.project_id} because {e}"
                    ),
                    reraise=True,
                )
        try:
            for suffix in ["", "-shm", "-wal"]:  # remove db files
                _path = f"{self.file_path}{suffix}"
                if os.path.exists(_path):
                    os.remove(_path)
        except Exception as e:
            logger.err(
                RuntimeError(
                    f"failed to delete DB file for project id {self.project_id} because {e}"
                ),
                reraise=True,
            )
        logger.info(f"History db for project id {self.project_id} has been deleted.")

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
        if not self._inited_tables[PROJECT_ID_TABLE_NAME]:  # create if there is no project id table
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

    def get_id_of_run_id(self, run_id: str):
        try:
            sql_query = f"SELECT {ID_COLUMN_NAME} FROM {RUN_IDS_TABLE_NAME} WHERE {RUN_ID_COLUMN_NAME} == '{run_id}'"
            _id, _ = self._query(sql_query, fetch=DbQueryFetchType.ONE)
            return _id[0]
        except:
            return None

    def fetch_id_of_run_id(self, run_id: str, timestamp: str = None):
        if not self._inited_tables[RUN_IDS_TABLE_NAME]:  # create if there is no version table
            sql_query = f"CREATE TABLE IF NOT EXISTS {RUN_IDS_TABLE_NAME} ( {ID_COLUMN_NAME} INTEGER PRIMARY KEY AUTOINCREMENT, {RUN_ID_COLUMN_NAME} TEXT NON NULL, {TIMESTAMP_COLUMN_NAME} TEXT NON NULL, {METADATA_COLUMN_NAME} TEXT, CONSTRAINT run_id_unique UNIQUE ({RUN_ID_COLUMN_NAME}));"
            self._execute(sql_query)
            self._inited_tables[RUN_IDS_TABLE_NAME] = True
        id_of_run_id = self.get_id_of_run_id(run_id)
        if id_of_run_id is None:
            timestamp = timestamp or datetime.now().strftime(DATETIME_FORMAT)
            sql_query = f"INSERT INTO {RUN_IDS_TABLE_NAME}({RUN_ID_COLUMN_NAME}, {TIMESTAMP_COLUMN_NAME}) VALUES (?, ?)"
            _, lastrowid = self._execute(sql_query, run_id, timestamp)
            return lastrowid
        return id_of_run_id

    def fetch_metadata_of_run_id(self, run_id: str, metadata: Union[dict, str] = None):
        id_of_run_id = self.get_id_of_run_id(run_id)
        if id_of_run_id is None:
            return None
        if metadata:  # if update name
            metadata = json.dumps(metadata) if isinstance(metadata, dict) else metadata
            sql_query = f"UPDATE {RUN_IDS_TABLE_NAME} SET {METADATA_COLUMN_NAME} = ? WHERE {ID_COLUMN_NAME} = ?"
            _, _ = self._execute(sql_query, metadata, id_of_run_id)
        # get name
        sql_query = f"SELECT {METADATA_COLUMN_NAME} FROM {RUN_IDS_TABLE_NAME} WHERE {ID_COLUMN_NAME} == {id_of_run_id}"
        (metadata,), _ = self._query(sql_query, fetch=DbQueryFetchType.ONE)
        metadata = (
            json.loads(metadata) if metadata else {}
        )  # if does not have metadata, return an empty one
        return metadata

    def get_run_id_of_id(self, id_of_run_id):
        try:
            sql_query = f"SELECT {RUN_ID_COLUMN_NAME} FROM {RUN_IDS_TABLE_NAME} WHERE {ID_COLUMN_NAME} == {id_of_run_id}"
            run_id, _ = self._query(sql_query, fetch=DbQueryFetchType.ONE)
            return run_id[0]
        except:
            return None

    def get_run_ids(self):
        if not self.table_exist(RUN_IDS_TABLE_NAME):
            return []
        sql_query = f"SELECT {RUN_ID_COLUMN_NAME}, {TIMESTAMP_COLUMN_NAME}, {METADATA_COLUMN_NAME} FROM {RUN_IDS_TABLE_NAME}"
        result, _ = self._query(sql_query)
        result = [
            {
                RUN_ID_KEY: run_id,
                TIMESTAMP_KEY: timestamp,
                METADATA_KEY: json.loads(metadata) if metadata else {},
            }
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
            sql_query = f"SELECT DISTINCT t.series as series FROM {RUN_IDS_TABLE_NAME} r LEFT JOIN {table_name} t ON r.{RUN_ID_COLUMN_NAME} == ? WHERE t.{RUN_ID_COLUMN_NAME} == r.{ID_COLUMN_NAME}"
            args = (run_id,)
        else:
            sql_query = f"SELECT DISTINCT series FROM {table_name}"
            args = ()
        result, _ = self._query(sql_query, *args, fetch=DbQueryFetchType.ALL)
        return [result for (result,) in result]

    def do_limit_num_row_for(
        self, table_name: str, run_id: str, num_row_limit: int, series: str = None
    ):
        if num_row_limit <= 0:  # no limit or random not triggered
            return
        sql_query = f"SELECT count(*) from {table_name} WHERE {RUN_ID_COLUMN_NAME} = {run_id}"  # count rows for run id in specific table
        if series is not None:
            sql_query += f" AND {SERIES_COLUMN_NAME} = '{series}'"
        num_rows, _ = self._query(sql_query, fetch=DbQueryFetchType.ONE)
        if num_rows[0] > num_row_limit:  # num rows exceeded limit
            sql_query = f"SELECT {ID_COLUMN_NAME} from {table_name} WHERE {RUN_ID_COLUMN_NAME} = {run_id} ORDER BY {ID_COLUMN_NAME} DESC LIMIT 1 OFFSET {num_row_limit - 1}"  # get max id to delete of row for specific run id
            max_id_to_del, _ = self._query(sql_query, fetch=DbQueryFetchType.ONE)
            sql_query = f"DELETE FROM {table_name} WHERE {ID_COLUMN_NAME} < {max_id_to_del[0]} AND {RUN_ID_COLUMN_NAME} = {run_id}"
            if series is not None:
                sql_query += f" AND {SERIES_COLUMN_NAME} = '{series}'"
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
        self.do_limit_num_row_for(
            table_name=table_name, run_id=run_id, num_row_limit=num_row_limit, series=series
        )
        return lastrowid

    def read_json(self, table_name: str, condition: QueryCondition = None):
        if not self.table_exist(table_name):
            return []
        if condition and isinstance(condition.run_id, str):
            condition.run_id = self.get_id_of_run_id(condition.run_id)  # convert run id
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
            condition.run_id = self.get_id_of_run_id(run_id)
        condition = condition.dumps()
        sql_query = f"SELECT {', '.join((RUN_ID_COLUMN_NAME, SERIES_COLUMN_NAME, JSON_COLUMN_NAME))} FROM {STATUS_TABLE_NAME} {condition}"
        query_result, _ = self._query(sql_query, fetch=DbQueryFetchType.ALL)
        result = {}
        for id_of_runid, series_name, value in query_result:
            run_id = self.get_run_id_of_id(id_of_runid)
            if run_id and run_id not in result:
                result[run_id] = {}
            result[run_id][series_name] = json.loads(value)
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
        self.do_limit_num_row_for(
            table_name=table_name, run_id=run_id, num_row_limit=num_row_limit, series=series
        )
        return lastrowid

    def read_blob(self, table_name: str, condition: QueryCondition = None, meta_only=False):
        if not self.table_exist(table_name):
            return []
        if condition and isinstance(condition.run_id, str):
            condition.run_id = self.get_id_of_run_id(condition.run_id)  # convert run id
        condition = condition.dumps() if condition else ""
        sql_query = f"SELECT {', '.join((ID_COLUMN_NAME,TIMESTAMP_COLUMN_NAME, METADATA_COLUMN_NAME, *((BLOB_COLUMN_NAME,) if not meta_only else ())))} FROM {table_name} {condition}"
        result, _ = self._query(sql_query, fetch=DbQueryFetchType.ALL)
        return result


# === DEFAULT EXPORT FUNCs ===

if not os.path.exists(HISTORY_FILE_ROOT):
    # create history root dir
    os.mkdir(HISTORY_FILE_ROOT)
# check if is dir
if not os.path.isdir(HISTORY_FILE_ROOT):
    raise RuntimeError(f"{HISTORY_FILE_ROOT} is not a directory.")


def load_db_of_path(path):
    if not os.path.isfile(path):
        raise RuntimeError(f"{path} is not a file")
    conn = DBConnection(path=path)
    return conn


def get_db_list():
    history_file_loader = ResourceLoader(
        folder=HISTORY_FILE_ROOT, file_types=[HISTORY_FILE_TYPE_NAME], force_rescan=True
    )
    history_file_list = history_file_loader.get_file_list()
    for path in history_file_list:
        load_db_of_path(path=path)
    return DBConnection._id2dbc.items()


def get_db_of_id(project_id, rescan: bool = True):
    if rescan:
        get_db_list()  # scan for possible file changes
    conn = DBConnection.of_project_id(project_id=project_id)
    return conn
