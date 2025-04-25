---
title: _protocol
---

## TOC

- **Attributes:**
  - 🅰 [VERSION](#🅰-version) - You can add error handling if needed
  - 🅰 [ID\_KEY](#🅰-id_key)
  - 🅰 [NAME\_KEY](#🅰-name_key)
  - 🅰 [ARGS\_KEY](#🅰-args_key)
  - 🅰 [MACHINE\_ID\_KEY](#🅰-machine_id_key)
  - 🅰 [PROJECT\_KEY](#🅰-project_key)
  - 🅰 [SERVER\_KEY](#🅰-server_key)
  - 🅰 [PROJECT\_ID\_KEY](#🅰-project_id_key)
  - 🅰 [RUN\_ID\_KEY](#🅰-run_id_key)
  - 🅰 [SERIES\_KEY](#🅰-series_key) - YYYY-MM-DDTHH:MM:SS.SSS
  - 🅰 [EVENT\_TYPE\_KEY](#🅰-event_type_key) - YYYY-MM-DDTHH:MM:SS.SSS
  - 🅰 [EVENT\_ID\_KEY](#🅰-event_id_key) - YYYY-MM-DDTHH:MM:SS.SSS
  - 🅰 [IDENTITY\_TYPE\_KEY](#🅰-identity_type_key) - YYYY-MM-DDTHH:MM:SS.SSS
  - 🅰 [CALLER\_ID\_KEY](#🅰-caller_id_key) - YYYY-MM-DDTHH:MM:SS.SSS
  - 🅰 [PAYLOAD\_KEY](#🅰-payload_key) - YYYY-MM-DDTHH:MM:SS.SSS
  - 🅰 [METADATA\_KEY](#🅰-metadata_key) - YYYY-MM-DDTHH:MM:SS.SSS
  - 🅰 [MESSAGE\_KEY](#🅰-message_key) - YYYY-MM-DDTHH:MM:SS.SSS
  - 🅰 [TIMESTAMP\_KEY](#🅰-timestamp_key) - YYYY-MM-DDTHH:MM:SS.SSS
  - 🅰 [HISTORY\_LEN\_KEY](#🅰-history_len_key) - YYYY-MM-DDTHH:MM:SS.SSS
  - 🅰 [DATETIME\_FORMAT](#🅰-datetime_format) - YYYY-MM-DDTHH:MM:SS.SSS
  - 🅰 [RESULT\_KEY](#🅰-result_key)
  - 🅰 [ERROR\_KEY](#🅰-error_key)
  - 🅰 [REASON\_KEY](#🅰-reason_key)
  - 🅰 [EVENT\_TYPE\_NAME\_HANDSHAKE](#🅰-event_type_name_handshake)
  - 🅰 [EVENT\_TYPE\_NAME\_WAVEHANDS](#🅰-event_type_name_wavehands)
  - 🅰 [EVENT\_TYPE\_NAME\_LOG](#🅰-event_type_name_log)
  - 🅰 [EVENT\_TYPE\_NAME\_ACTION](#🅰-event_type_name_action) - ===================== HTTP things =====================
  - 🅰 [EVENT\_TYPE\_NAME\_SCALAR](#🅰-event_type_name_scalar) - ===================== HTTP things =====================
  - 🅰 [EVENT\_TYPE\_NAME\_HIST](#🅰-event_type_name_hist) - ===================== HTTP things =====================
  - 🅰 [EVENT\_TYPE\_NAME\_IMAGE](#🅰-event_type_name_image) - ===================== HTTP things =====================
  - 🅰 [EVENT\_TYPE\_NAME\_VIDEO](#🅰-event_type_name_video) - ===================== HTTP things =====================
  - 🅰 [EVENT\_TYPE\_NAME\_HPARAMS](#🅰-event_type_name_hparams) - ===================== HTTP things =====================
  - 🅰 [EVENT\_TYPE\_NAME\_STATUS](#🅰-event_type_name_status) - ===================== HTTP things =====================
  - 🅰 [EVENT\_TYPE\_NAME\_HARDWARE](#🅰-event_type_name_hardware) - ===================== HTTP things =====================
  - 🅰 [EVENT\_TYPE\_NAME\_PROGRESS](#🅰-event_type_name_progress) - ===================== HTTP things =====================
  - 🅰 [API\_ROOT](#🅰-api_root) - ===================== DB things =====================
  - 🅰 [WS\_ROOT](#🅰-ws_root) - ===================== DB things =====================
  - 🅰 [ID\_COLUMN\_NAME](#🅰-id_column_name) - === TABLE NAMES ===
  - 🅰 [TIMESTAMP\_COLUMN\_NAME](#🅰-timestamp_column_name) - === TABLE NAMES ===
  - 🅰 [NAME\_COLUMN\_NAME](#🅰-name_column_name) - === TABLE NAMES ===
  - 🅰 [RUN\_ID\_COLUMN\_NAME](#🅰-run_id_column_name) - === TABLE NAMES ===
  - 🅰 [JSON\_COLUMN\_NAME](#🅰-json_column_name) - === TABLE NAMES ===
  - 🅰 [BLOB\_COLUMN\_NAME](#🅰-blob_column_name) - === TABLE NAMES ===
  - 🅰 [PROJECT\_ID\_TABLE\_NAME](#🅰-project_id_table_name)
  - 🅰 [VERSION\_TABLE\_NAME](#🅰-version_table_name)
  - 🅰 [RUN\_IDS\_TABLE\_NAME](#🅰-run_ids_table_name)
  - 🅰 [STATUS\_TABLE\_NAME](#🅰-status_table_name)
  - 🅰 [LOG\_TABLE\_NAME](#🅰-log_table_name)
  - 🅰 [IMAGE\_TABLE\_NAME](#🅰-image_table_name)
  - 🅰 [NEETBOX\_VERSION](#🅰-neetbox_version)
- **Functions:**
  - 🅵 [\_refresh\_version\_every](#🅵-_refresh_version_every)
  - 🅵 [get\_timestamp](#🅵-get_timestamp)
- **Classes:**
  - 🅲 [IdentityType](#🅲-identitytype)
  - 🅲 [EventMsg](#🅲-eventmsg)

## Attributes

## 🅰 VERSION

```python
VERSION = version("neetbox") #You can add error handling if needed
```

## 🅰 ID\_KEY

```python
ID_KEY = """id"""
```

## 🅰 NAME\_KEY

```python
NAME_KEY = """name"""
```

## 🅰 ARGS\_KEY

```python
ARGS_KEY = """args"""
```

## 🅰 MACHINE\_ID\_KEY

```python
MACHINE_ID_KEY = """machineId"""
```

## 🅰 PROJECT\_KEY

```python
PROJECT_KEY = """project"""
```

## 🅰 SERVER\_KEY

```python
SERVER_KEY = """server"""
```

## 🅰 PROJECT\_ID\_KEY

```python
PROJECT_ID_KEY = """projectId"""
```

## 🅰 RUN\_ID\_KEY

```python
RUN_ID_KEY = """runId"""
```

## 🅰 SERIES\_KEY

```python
SERIES_KEY = """series""" #YYYY-MM-DDTHH:MM:SS.SSS
```

## 🅰 EVENT\_TYPE\_KEY

```python
EVENT_TYPE_KEY = """eventType""" #YYYY-MM-DDTHH:MM:SS.SSS
```

## 🅰 EVENT\_ID\_KEY

```python
EVENT_ID_KEY = """eventId""" #YYYY-MM-DDTHH:MM:SS.SSS
```

## 🅰 IDENTITY\_TYPE\_KEY

```python
IDENTITY_TYPE_KEY = """identityType""" #YYYY-MM-DDTHH:MM:SS.SSS
```

## 🅰 CALLER\_ID\_KEY

```python
CALLER_ID_KEY = """whom""" #YYYY-MM-DDTHH:MM:SS.SSS
```

## 🅰 PAYLOAD\_KEY

```python
PAYLOAD_KEY = """payload""" #YYYY-MM-DDTHH:MM:SS.SSS
```

## 🅰 METADATA\_KEY

```python
METADATA_KEY = """metadata""" #YYYY-MM-DDTHH:MM:SS.SSS
```

## 🅰 MESSAGE\_KEY

```python
MESSAGE_KEY = """message""" #YYYY-MM-DDTHH:MM:SS.SSS
```

## 🅰 TIMESTAMP\_KEY

```python
TIMESTAMP_KEY = """timestamp""" #YYYY-MM-DDTHH:MM:SS.SSS
```

## 🅰 HISTORY\_LEN\_KEY

```python
HISTORY_LEN_KEY = """historyLen""" #YYYY-MM-DDTHH:MM:SS.SSS
```

## 🅰 DATETIME\_FORMAT

```python
DATETIME_FORMAT = """%Y-%m-%dT%H:%M:%S.%f""" #YYYY-MM-DDTHH:MM:SS.SSS
```

## 🅰 RESULT\_KEY

```python
RESULT_KEY = """result"""
```

## 🅰 ERROR\_KEY

```python
ERROR_KEY = """error"""
```

## 🅰 REASON\_KEY

```python
REASON_KEY = """reason"""
```

## 🅰 EVENT\_TYPE\_NAME\_HANDSHAKE

```python
EVENT_TYPE_NAME_HANDSHAKE = """handshake"""
```

## 🅰 EVENT\_TYPE\_NAME\_WAVEHANDS

```python
EVENT_TYPE_NAME_WAVEHANDS = """wavehands"""
```

## 🅰 EVENT\_TYPE\_NAME\_LOG

```python
EVENT_TYPE_NAME_LOG = """log"""
```

## 🅰 EVENT\_TYPE\_NAME\_ACTION

```python
EVENT_TYPE_NAME_ACTION = """action""" #===================== HTTP things =====================
```

## 🅰 EVENT\_TYPE\_NAME\_SCALAR

```python
EVENT_TYPE_NAME_SCALAR = """scalar""" #===================== HTTP things =====================
```

## 🅰 EVENT\_TYPE\_NAME\_HIST

```python
EVENT_TYPE_NAME_HIST = """histogram""" #===================== HTTP things =====================
```

## 🅰 EVENT\_TYPE\_NAME\_IMAGE

```python
EVENT_TYPE_NAME_IMAGE = """image""" #===================== HTTP things =====================
```

## 🅰 EVENT\_TYPE\_NAME\_VIDEO

```python
EVENT_TYPE_NAME_VIDEO = """video""" #===================== HTTP things =====================
```

## 🅰 EVENT\_TYPE\_NAME\_HPARAMS

```python
EVENT_TYPE_NAME_HPARAMS = """hyperparameters""" #===================== HTTP things =====================
```

## 🅰 EVENT\_TYPE\_NAME\_STATUS

```python
EVENT_TYPE_NAME_STATUS = """status""" #===================== HTTP things =====================
```

## 🅰 EVENT\_TYPE\_NAME\_HARDWARE

```python
EVENT_TYPE_NAME_HARDWARE = """hardware""" #===================== HTTP things =====================
```

## 🅰 EVENT\_TYPE\_NAME\_PROGRESS

```python
EVENT_TYPE_NAME_PROGRESS = """progress""" #===================== HTTP things =====================
```

## 🅰 API\_ROOT

```python
API_ROOT = """/api""" #===================== DB things =====================
```

## 🅰 WS\_ROOT

```python
WS_ROOT = """/ws""" #===================== DB things =====================
```

## 🅰 ID\_COLUMN\_NAME

```python
ID_COLUMN_NAME = ID_KEY #=== TABLE NAMES ===
```

## 🅰 TIMESTAMP\_COLUMN\_NAME

```python
TIMESTAMP_COLUMN_NAME = TIMESTAMP_KEY #=== TABLE NAMES ===
```

## 🅰 NAME\_COLUMN\_NAME

```python
NAME_COLUMN_NAME = SERIES_KEY #=== TABLE NAMES ===
```

## 🅰 RUN\_ID\_COLUMN\_NAME

```python
RUN_ID_COLUMN_NAME = RUN_ID_KEY #=== TABLE NAMES ===
```

## 🅰 JSON\_COLUMN\_NAME

```python
JSON_COLUMN_NAME = METADATA_KEY #=== TABLE NAMES ===
```

## 🅰 BLOB\_COLUMN\_NAME

```python
BLOB_COLUMN_NAME = """data""" #=== TABLE NAMES ===
```

## 🅰 PROJECT\_ID\_TABLE\_NAME

```python
PROJECT_ID_TABLE_NAME = PROJECT_ID_KEY
```

## 🅰 VERSION\_TABLE\_NAME

```python
VERSION_TABLE_NAME = """version"""
```

## 🅰 RUN\_IDS\_TABLE\_NAME

```python
RUN_IDS_TABLE_NAME = RUN_ID_KEY
```

## 🅰 STATUS\_TABLE\_NAME

```python
STATUS_TABLE_NAME = EVENT_TYPE_NAME_STATUS
```

## 🅰 LOG\_TABLE\_NAME

```python
LOG_TABLE_NAME = """log"""
```

## 🅰 IMAGE\_TABLE\_NAME

```python
IMAGE_TABLE_NAME = """image"""
```

## 🅰 NEETBOX\_VERSION

```python
NEETBOX_VERSION = version("neetbox")
```


## Functions

## 🅵 \_refresh\_version\_every

```python
def _refresh_version_every(sec: int = 60):
```
## 🅵 get\_timestamp

```python
def get_timestamp(datetime=None):
```

## Classes

## 🅲 IdentityType

```python
class IdentityType(str, Enum):
```


### 🅼 \_\_repr\_\_

```python
def __repr__(self) -> str:
```
## 🅲 EventMsg

```python
class EventMsg:
```


### 🅼 json

```python
def json(self):
```
### 🅼 dumps

```python
def dumps(self):
```
### 🅼 loads

```python
def loads(cls, src):
```
### 🅼 merge

```python
def merge(cls, x: Union["EventMsg", dict], y: Union["EventMsg", dict]):
```
