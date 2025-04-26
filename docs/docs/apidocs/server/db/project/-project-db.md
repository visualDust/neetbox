---
title: _project_db
sidebar_position: 3
---

## TOC

- **Attributes:**
  - 🅰 [logger](#🅰-logger) - check if the db path is valid. if not, create it
  - 🅰 [DB\_PROJECT\_FILE\_FOLDER](#🅰-db_project_file_folder) - check if the db path is valid. if not, create it
  - 🅰 [DB\_PROJECT\_FILE\_TYPE\_NAME](#🅰-db_project_file_type_name) - check if the db path is valid. if not, create it
- **Functions:**
  - 🅵 [\_CHECK\_GET\_PROJECT\_FILE\_FOLDER](#🅵-_check_get_project_file_folder) - check if the db path is valid. if not, create it
- **Classes:**
  - 🅲 [ProjectDB](#🅲-projectdb)

## Attributes

## 🅰 logger

```python
logger = Logger("PROJECT DB", skip_writers_names=["ws"]) #check if the db path is valid. if not, create it
```

## 🅰 DB\_PROJECT\_FILE\_FOLDER

```python
DB_PROJECT_FILE_FOLDER = f"""{get_global_config('vault')}/server/db/project""" #check if the db path is valid. if not, create it
```

## 🅰 DB\_PROJECT\_FILE\_TYPE\_NAME

```python
DB_PROJECT_FILE_TYPE_NAME = """projectdb""" #check if the db path is valid. if not, create it
```


## Functions

## 🅵 \_CHECK\_GET\_PROJECT\_FILE\_FOLDER

```python
def _CHECK_GET_PROJECT_FILE_FOLDER():
```

check if the db path is valid. if not, create it

## Classes

## 🅲 ProjectDB

```python
class ProjectDB(ManageableDB):
    _path2dbc = {}
    project_id: str = None
    file_path: str = None
    connection: sqlite3.Connection = None
    _inited_tables: collections.defaultdict = None
    _run_id_fetch_lock = Lock()
```


### 🅼 \_\_new\_\_

```python
def __new__(
    cls, project_id: str = None, path: str = None, **kwargs
) -> "ProjectDB":
```
### 🅼 \_\_repr\_\_

```python
def __repr__(self):
```
### 🅼 size

```python
@property
def size(self):
```

return local storage usage by this project db in bytes

**Returns:**

- **[int](https://docs.python.org/3/library/stdtypes.html#numeric-types-int-float-complex)**: size in bytes
### 🅼 close

```python
def close(self):
```
### 🅼 delete

```python
def delete(self):
```

delete related files of db
### 🅼 items

```python
@classmethod
def items(cls):
```
### 🅼 of\_project\_id

```python
@classmethod
def of_project_id(cls, project_id):
```
### 🅼 \_execute

```python
def _execute(self, query, *args, fetch: FetchType = FetchType.ALL, **kwargs):
```
### 🅼 \_query

```python
def _query(self, query, *args, fetch: FetchType = FetchType.ALL, **kwargs):
```
### 🅼 table\_exist

```python
def table_exist(self, table_name):
```
### 🅼 get\_table\_names

```python
def get_table_names(self):
```
### 🅼 fetch\_db\_version

```python
def fetch_db_version(self, default=None):
```
### 🅼 fetch\_db\_project\_id

```python
def fetch_db_project_id(self, default=None):
```
### 🅼 get\_id\_of\_run\_id

```python
def get_id_of_run_id(self, run_id: str):
```
### 🅼 fetch\_id\_of\_run\_id

```python
def fetch_id_of_run_id(self, run_id: str, timestamp: str = None):
```
### 🅼 fetch\_metadata\_of\_run\_id

```python
def fetch_metadata_of_run_id(
    self, run_id: str, metadata: Union[dict, str] = None
):
```
### 🅼 get\_run\_id\_of\_id

```python
def get_run_id_of_id(self, id_of_run_id):
```
### 🅼 get\_run\_ids

```python
def get_run_ids(self):
```
### 🅼 delete\_run\_id

```python
def delete_run_id(self, run_id: str):
```
### 🅼 get\_series\_of\_table

```python
def get_series_of_table(self, table_name, run_id=None):
```
### 🅼 do\_limit\_num\_row\_for

```python
def do_limit_num_row_for(
    self, table_name: str, run_id: str, num_row_limit: int, series: str = None
):
```
### 🅼 write\_json

```python
def write_json(
    self,
    table_name: str,
    json_data: str,
    series: str = None,
    run_id: str = None,
    timestamp: str = None,
    num_row_limit=-1,
):
```
### 🅼 read\_json

```python
def read_json(self, table_name: str, condition: ProjectDbQueryCondition = None):
```
### 🅼 set\_status

```python
def set_status(self, run_id: str, series: str, json_data):
```
### 🅼 get\_status

```python
def get_status(self, run_id: str = None, series: str = None):
```
### 🅼 write\_blob

```python
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
```
### 🅼 read\_blob

```python
def read_blob(
    self,
    table_name: str,
    condition: ProjectDbQueryCondition = None,
    meta_only=False,
):
```
### 🅼 load\_db\_of\_path

```python
@classmethod
def load_db_of_path(cls, path):
```
### 🅼 get\_db\_list

```python
@classmethod
def get_db_list(cls):
```
### 🅼 get\_db\_of\_id

```python
@classmethod
def get_db_of_id(cls, project_id, rescan: bool = True):
```
