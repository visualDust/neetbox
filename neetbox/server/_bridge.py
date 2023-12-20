# -*- coding: utf-8 -*-
#
# Author: GavinGong aka VisualDust
# Github: github.com/visualDust
# Date:   20231204

from typing import Dict

from websocket_server import WebsocketServer

from neetbox._protocol import *
from neetbox.logging import LogStyle, logger

from .db import history

logger = logger("NEETBOX", LogStyle(skip_writers=["ws"]))


class Bridge:
    """Server works as a bridge between clients and frontends. Bridge connects one client and multiple frontend. Since client means a running project, a bridge represents a running(connected) or not running(not connected, loaded from history database) project.
    You can:
    - send websocket message to clients or frontends connected to specific bridge
    - read and write history db(sqlite3) via bridge
    HTTP server should serves information via bridges.

            Client  ┌──--> Frontend
                |   |
                ↓   ↓
    Client<--> Server--> Frontend
                ↑   ↑
                │   │
            Client  └──--> Frontend
    """

    # static
    _id2bridge: Dict[str, "Bridge"] = {}  # manage connections using project id
    _ws_server: WebsocketServer = None

    # instance vars
    project_id: str
    status: dict
    cli_ws_dict: dict  # { run_id : client}
    web_ws_list: list  # since web do not have run id, use list instead of dict
    historyDB: history.DBConnection

    def __new__(cls, project_id: str, **kwargs) -> None:
        """Create Bridge of project id, return the old one if already exist
        Args:
            project_id (str): project id
        Returns:
            Bridge: Bridge of given project id
        """
        if project_id not in cls._id2bridge:
            new_bridge = super().__new__(cls)
            new_bridge.project_id = project_id
            new_bridge.cli_ws_dict: dict = {}  # cli ws sid
            new_bridge.web_ws_list: list = (
                []
            )  # frontend ws sids. client data should be able to be shown on multiple frontend
            flag_auto_load_db = kwargs["auto_load_db"] if "auto_load_db" in kwargs else True
            new_bridge.historyDB = history.get_db_of_id(project_id) if flag_auto_load_db else None
            cls._id2bridge[project_id] = new_bridge
            logger.info(f"created new Bridge for project id '{project_id}'")
        return cls._id2bridge[project_id]

    def __del__(self):  # on delete
        logger.info(f"bridge project id {self.project_id} handling on delete...")
        if 0 == len(self.get_run_ids()):  # if there is no active run id
            self.historyDB.finialize()
            del self.historyDB  # delete history db
        logger.info(f"bridge of project id {self.project_id} deleted.")

    @classmethod
    def items(cls):
        return cls._id2bridge.items()

    @classmethod
    def has(cls, project_id: str):
        return project_id in cls._id2bridge

    @classmethod
    def of_id(cls, project_id: str) -> "Bridge":
        """get Bridge of project id if exist. note that this class method is different fromBridge.__new__, which do not create new Bridge if given id not exist, it returns Noneinstead.
        Args:
            project_id (str): project id
        Returns:
            Bridge: Bridge if id exist, otherwise None
        """
        bridge = cls._id2bridge[project_id] if cls.has(project_id) else None
        return bridge

    @classmethod
    def from_db(cls, db: history.DBConnection) -> "Bridge":
        project_id = db.fetch_db_project_id()
        target_bridge = Bridge(project_id, auto_load_db=False)
        if target_bridge.historyDB is not None:
            logger.warn(f"overwriting db of '{project_id}'")
        target_bridge.historyDB = db
        return target_bridge

    @classmethod
    def load_histories(cls):
        db_list = history.get_db_list()
        logger.log(f"found {len(db_list)} history db.")
        for _, history_db in db_list:
            cls.from_db(history_db)

    def ws_send_to_frontends(self, message: EventMsg):
        for web_ws in self.web_ws_list:
            try:
                Bridge._ws_server.send_message(
                    client=web_ws, msg=message.dumps()
                )  # forward original message to frontend
            except Exception as e:
                logger.err(e)
        return

    def ws_send_to_client(self, message: EventMsg, run_id: str = None):
        target_run_id = run_id or message.run_id
        _client = self.cli_ws_dict[target_run_id]
        try:
            Bridge._ws_server.send_message(
                client=_client, msg=message.dumps()
            )  # forward original message to client
        except Exception as e:
            logger.err(e)
        return

    def set_status(self, run_id: str, series: str, value: dict):
        self.historyDB.set_status(run_id=run_id, series=series, json_data=value)

    def get_status(self, run_id: str = None, series: str = None):
        status = self.historyDB.get_status(run_id=run_id, series=series)
        if run_id:
            status = status.get(run_id, {})
        if series:
            status = status.get(series, {})
        return status

    def is_online(self, run_id: str = None):
        if run_id:  # if checking client run with specific run id
            return run_id in self.cli_ws_dict
        return len(self.cli_ws_dict.keys()) != 0

    def get_series_of(self, table_name, run_id=None):
        return self.historyDB.get_series_of_table(table_name=table_name, run_id=run_id)

    def get_run_ids(self):
        info_run_ids = self.historyDB.get_run_ids()
        for info_run_id in info_run_ids:
            info_run_id["online"] = info_run_id[RUN_ID_KEY] in self.cli_ws_dict
        return info_run_ids

    def save_json_to_history(
        self, table_name, json_data, series=None, run_id=None, timestamp=None, num_row_limit=-1
    ):
        lastrowid = Bridge.of_id(self.project_id).historyDB.write_json(
            table_name=table_name,
            json_data=json_data,
            series=series,
            run_id=run_id,
            timestamp=timestamp,
            num_row_limit=num_row_limit,
        )
        return lastrowid

    def read_json_from_history(self, table_name, condition):
        return self.historyDB.read_json(table_name=table_name, condition=condition)

    def save_blob_to_history(
        self,
        table_name,
        meta_data,
        blob_data,
        series=None,
        run_id=None,
        timestamp=None,
        num_row_limit=-1,
    ):
        lastrowid = Bridge.of_id(self.project_id).historyDB.write_blob(
            table_name=table_name,
            meta_data=meta_data,
            blob_data=blob_data,
            series=series,
            run_id=run_id,
            timestamp=timestamp,
            num_row_limit=num_row_limit,
        )
        return lastrowid

    def read_blob_from_history(self, table_name, condition, meta_only: bool):
        return self.historyDB.read_blob(table_name, condition=condition, meta_only=meta_only)
