---
title: _formatting
sidebar_position: 3
---

## TOC

- **Classes:**
  - 🅲 [LogStyle](#🅲-logstyle)
  - 🅲 [RawLog](#🅲-rawlog)

## Classes

## 🅲 LogStyle

```python
@dataclass
class LogStyle:
    datetime_format: Optional[str] = "%Y-%m-%dT%H:%M:%S.%f"
    caller_info_format: Optional[str] = "%m/%c/%f"
```
## 🅲 RawLog

```python
@dataclass
class RawLog:
    message: str = None
    caller_info: TracebackInfo = None
    caller_name_alias: Optional[str] = None
    timestamp: datetime = datetime.now()
    series: Optional[str] = None
    style: LogStyle = field(default_factory=LogStyle)
```


### 🅼 timestamp\_formatted

```python
@property
def timestamp_formatted(self):
```
### 🅼 caller\_info\_formatted

```python
@property
def caller_info_formatted(self):
```
### 🅼 json

```python
@property
def json(self) -> dict:
```
### 🅼 \_\_repr\_\_

```python
def __repr__(self) -> str:
```
