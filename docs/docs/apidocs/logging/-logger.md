---
title: _logger
---

## TOC

- **Attributes:**
  - 🅰 [LogWriters](#🅰-logwriters)
  - 🅰 [DEFAULT\_LOGGER](#🅰-default_logger)
- **Classes:**
  - 🅲 [LogLevel](#🅲-loglevel)
  - 🅲 [Logger](#🅲-logger)

## Attributes

## 🅰 LogWriters

```python
LogWriters = Registry("LOG_WRITERS")
```

## 🅰 DEFAULT\_LOGGER

```python
DEFAULT_LOGGER = Logger(None)
```


## Classes

## 🅲 LogLevel

```python
class LogLevel(Enum):
```


### 🅼 \_\_lt\_\_

```python
def __lt__(self, other):
```
### 🅼 \_\_le\_\_

```python
def __le__(self, other):
```
### 🅼 \_\_eq\_\_

```python
def __eq__(self, other):
```
### 🅼 \_\_ne\_\_

```python
def __ne__(self, other):
```
### 🅼 \_\_gt\_\_

```python
def __gt__(self, other):
```
### 🅼 \_\_ge\_\_

```python
def __ge__(self, other):
```
## 🅲 Logger

```python
class Logger:
```


### 🅼 \_\_init\_\_

```python
def __init__(
    self,
    name_alias: str = None,
    style: Optional[LogStyle] = LogStyle(),
    log_level: LogLevel = LogLevel.INFO,
    skip_writers_names=[],
):
```

create a new logger

**Parameters:**

- **name_alias** ([str](https://docs.python.org/3/library/stdtypes.html#text-sequence-type-str)) (default to `None`): the name alias of the logger. Defaults to None.
- **style** (Optional[LogStyle]) (default to `LogStyle()`): logger's default log style. Defaults to LogStyle\(\).
- **log_level** ([LogLevel](-logger#🅲-loglevel)) (default to `LogLevel.INFO`): log level. Defaults to LogLevel.INFO.
- **skip_writers_names** ([list](https://docs.python.org/3/library/stdtypes.html#lists)) (default to `[]`): names of writers to be skipped. Defaults to \[\].
### 🅼 \_\_new\_\_

```python
def __new__(cls, name_alias: str = None, *args, **kwargs) -> "Logger":
```
### 🅼 style

```python
def style(self):
```
### 🅼 style

```python
def style(self, style: LogStyle):
```
### 🅼 log\_level

```python
def log_level(self):
```
### 🅼 log\_level

```python
def log_level(self, level: Union[LogLevel, str]):
```
### 🅼 set\_global\_log\_level

```python
def set_global_log_level(cls, level: Union[LogLevel, str]):
```
### 🅼 writer

```python
def writer(self, name: str):
```
### 🅼 skip\_writer\_name

```python
def skip_writer_name(self, name: str):
```
### 🅼 log

```python
def log(
    self,
    *content,
    series: Optional[str] = None,
    skip_writers_names: list[str] = [],
    stack_offset=2
):
```
### 🅼 ok

```python
def ok(self, *content, skip_writers_names: list[str] = [], stack_offset=2):
```
### 🅼 debug

```python
def debug(self, *content, skip_writers_names: list[str] = [], stack_offset=2):
```
### 🅼 info

```python
def info(self, *content, skip_writers_names: list[str] = [], stack_offset=2):
```
### 🅼 warn

```python
def warn(self, *content, skip_writers_names: list[str] = [], stack_offset=2):
```
### 🅼 err

```python
def err(
    self, err, skip_writers_names: list[str] = [], stack_offset=2, reraise=False
):
```
### 🅼 mention

```python
def mention(
    self, mention_args=True, mention_result=True, skip_writers_names=[]
):
```
### 🅼 send\_mention

```python
def send_mention(
    self, message: str, skip_writers_names: list[str] = [], stack_offset=2
):
```
### 🅼 set\_log\_dir

```python
def set_log_dir(self, path, dedicated_file=False):
```
