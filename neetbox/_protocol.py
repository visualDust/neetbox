import json
from dataclasses import dataclass
from datetime import datetime as dt
from enum import Enum
from importlib.metadata import version
from typing import Any, Union

# ===================== common things =====================

ID_KEY = "id"
NAME_KEY = "name"
ARGS_KEY = "args"
PROJECT_ID_KEY = WORKSPACE_ID_KEY = "projectid"
RUN_ID_KEY = "runid"
SERIES_KEY = "series"
EVENT_TYPE_KEY = "event-type"
EVENT_ID_KEY = "event-id"
WHO_KEY = "who"
PAYLOAD_KEY = "payload"
METADATA_KEY = "metadata"
TIMESTAMP_KEY = "timestamp"
HISTORY_LEN_KEY = "history-len"
DATETIME_FORMAT = "%Y-%m-%dT%H:%M:%S.%f"  # YYYY-MM-DDTHH:MM:SS.SSS


def get_timestamp(datetime=None):
    datetime = datetime or dt.now()
    return datetime.strftime(DATETIME_FORMAT)


class IdentityType(str, Enum):
    WEB = "web"
    CLI = "cli"
    SERVER = "server"
    SELF = "self"
    OTHERS = "another"
    BOTH = "both"


RESULT_KEY = "result"
ERROR_KEY = "error"
REASON_KEY = "reason"


@dataclass
class EventMsg:
    project_id: str
    run_id: str
    event_type: str
    series: str = None
    payload: Any = None
    event_id: int = -1
    who: str = None
    timestamp: str = get_timestamp()
    history_len: int = -1
    id: int = None  # id in database

    def json(self):
        return {
            PROJECT_ID_KEY: self.project_id,
            RUN_ID_KEY: self.run_id,
            EVENT_TYPE_KEY: self.event_type,
            EVENT_ID_KEY: self.event_id,
            WHO_KEY: self.who,
            SERIES_KEY: self.series,
            PAYLOAD_KEY: self.payload,
            TIMESTAMP_KEY: self.timestamp,
            HISTORY_LEN_KEY: self.history_len,
            ID_KEY: self.id,
        }

    def dumps(self):
        return json.dumps(self.json(), default=str)

    @classmethod
    def loads(cls, src):
        if isinstance(src, str):
            src = json.loads(src)
        return EventMsg(
            project_id=src.get(PROJECT_ID_KEY),
            run_id=src.get(RUN_ID_KEY),
            event_type=src.get(EVENT_TYPE_KEY),
            who=src.get(WHO_KEY),
            series=src.get(SERIES_KEY),
            payload=src.get(PAYLOAD_KEY),
            event_id=src.get(EVENT_ID_KEY, -1),
            timestamp=src.get(TIMESTAMP_KEY, get_timestamp()),
            history_len=src.get(HISTORY_LEN_KEY, -1),
            id=src.get(ID_KEY, None),
        )

    @classmethod
    def merge(cls, x: Union["EventMsg", dict], y: Union["EventMsg", dict]):
        _x = x if isinstance(x, dict) else x.json()
        _y = y if isinstance(y, dict) else y.json()
        for _k, _v in _y.items():
            _x[_k] = _v
        return cls.loads(_x)


# ===================== WS things =====================

# known event names
EVENT_TYPE_NAME_HANDSHAKE = "handshake"
EVENT_TYPE_NAME_LOG = "log"
EVENT_TYPE_NAME_ACTION = "action"
EVENT_TYPE_NAME_SCALAR = "scalar"
EVENT_TYPE_NAME_HIST = "histogram"
EVENT_TYPE_NAME_IMAGE = "image"
EVENT_TYPE_NAME_VIDEO = "video"
EVENT_TYPE_NAME_HPARAMS = "hyperparameters"
EVENT_TYPE_NAME_STATUS = "status"
EVENT_TYPE_NAME_HARDWARE = "hardware"

# ===================== HTTP things =====================

FRONTEND_API_ROOT = "/api"
CLIENT_API_ROOT = "/cli"

# ===================== DB things =====================

# === COLUMN NAMES ===
ID_COLUMN_NAME = ID_KEY
TIMESTAMP_COLUMN_NAME = TIMESTAMP_KEY
NAME_COLUMN_NAME = SERIES_COLUMN_NAME = SERIES_KEY
RUN_ID_COLUMN_NAME = RUN_ID_KEY
JSON_COLUMN_NAME = METADATA_COLUMN_NAME = METADATA_KEY
BLOB_COLUMN_NAME = "data"

# === TABLE NAMES ===
PROJECT_ID_TABLE_NAME = PROJECT_ID_KEY
VERSION_TABLE_NAME = "version"
RUN_IDS_TABLE_NAME = RUN_ID_KEY
STATUS_TABLE_NAME = EVENT_TYPE_NAME_STATUS
LOG_TABLE_NAME = "log"
IMAGE_TABLE_NAME = "image"

NEETBOX_VERSION = version("neetbox")
HISTORY_FILE_ROOT = ".neethistory"
HISTORY_FILE_TYPE_NAME = "neetory"


class DbQueryFetchType(str, Enum):
    ALL = "all"
    ONE = "one"
    MANY = "many"


class DbQuerySortType(str, Enum):
    ASC = "ASC"
    DESC = "DESC"
