---
title: _signal_and_slot
---

## TOC

- **Attributes:**
  - 🅰 [\_\_TIME\_CTR\_MAX\_CYCLE](#🅰-__time_ctr_max_cycle) - YYYY-MM-DDTHH:MM:SS.SSS
  - 🅰 [\_\_TIME\_UNIT\_SEC](#🅰-__time_unit_sec) - YYYY-MM-DDTHH:MM:SS.SSS
  - 🅰 [\_WATCH\_QUERY\_DICT](#🅰-_watch_query_dict) - YYYY-MM-DDTHH:MM:SS.SSS
  - 🅰 [\_LISTEN\_QUERY\_DICT](#🅰-_listen_query_dict) - YYYY-MM-DDTHH:MM:SS.SSS
  - 🅰 [\_UPDATE\_VALUE\_DICT](#🅰-_update_value_dict) - YYYY-MM-DDTHH:MM:SS.SSS
  - 🅰 [DATETIME\_FORMAT](#🅰-datetime_format) - YYYY-MM-DDTHH:MM:SS.SSS
  - 🅰 [\_DEFAULT\_CHANNEL](#🅰-_default_channel) - default watch and listen channel. users use this channel by default. default channel name varies on each start
  - 🅰 [SYSTEM\_CHANNEL](#🅰-system_channel) - values on this channel will upload via http client
  - 🅰 [update\_thread](#🅰-update_thread)
- **Functions:**
  - 🅵 [\_\_get](#🅵-__get)
  - 🅵 [\_\_update\_and\_get](#🅵-__update_and_get)
  - 🅵 [\_watch](#🅵-_watch)
  - 🅵 [watch](#🅵-watch)
  - 🅵 [\_listen](#🅵-_listen)
  - 🅵 [listen](#🅵-listen)
  - 🅵 [\_update\_thread](#🅵-_update_thread)
- **Classes:**
  - 🅲 [\_WatchConfig](#🅲-_watchconfig)
  - 🅲 [\_WatchedFun](#🅲-_watchedfun)

## Attributes

## 🅰 \_\_TIME\_CTR\_MAX\_CYCLE

```python
__TIME_CTR_MAX_CYCLE = Decimal("99999.0") #YYYY-MM-DDTHH:MM:SS.SSS
```

## 🅰 \_\_TIME\_UNIT\_SEC

```python
__TIME_UNIT_SEC = Decimal("0.1") #YYYY-MM-DDTHH:MM:SS.SSS
```

## 🅰 \_WATCH\_QUERY\_DICT

```python
_WATCH_QUERY_DICT = Registry("__pipeline_watch") #YYYY-MM-DDTHH:MM:SS.SSS
```

## 🅰 \_LISTEN\_QUERY\_DICT

```python
_LISTEN_QUERY_DICT = collections.defaultdict(lambda: {}) #YYYY-MM-DDTHH:MM:SS.SSS
```

## 🅰 \_UPDATE\_VALUE\_DICT

```python
_UPDATE_VALUE_DICT = collections.defaultdict(lambda: {}) #YYYY-MM-DDTHH:MM:SS.SSS
```

## 🅰 DATETIME\_FORMAT

```python
DATETIME_FORMAT = """%Y-%m-%dT%H:%M:%S.%f""" #YYYY-MM-DDTHH:MM:SS.SSS
```

## 🅰 \_DEFAULT\_CHANNEL

```python
_DEFAULT_CHANNEL = str(uuid4()) #default watch and listen channel. users use this channel by default. default channel name varies on each start
```

## 🅰 SYSTEM\_CHANNEL

```python
SYSTEM_CHANNEL = """__system""" #values on this channel will upload via http client
```

## 🅰 update\_thread

```python
update_thread = Thread(target=_update_thread, daemon=True)
```


## Functions

## 🅵 \_\_get

```python
def __get(name: str, channel):
```
## 🅵 \_\_update\_and\_get

```python
def __update_and_get(name: str, *args, **kwargs):
```
## 🅵 \_watch

```python
def _watch(
    func: Callable,
    name: Optional[str],
    interval: float,
    initiative: bool = False,
    overwrite: bool = False,
    _channel: str = None,
):
```
## 🅵 watch

```python
def watch(
    name: str = None,
    interval: float = None,
    initiative: bool = True,
    overwrite: bool = False,
    _channel: str = None,
):
```
## 🅵 \_listen

```python
def _listen(
    func: Callable,
    target: Union[str, Callable],
    listener_name: Optional[str] = None,
    overwrite: bool = False,
):
```
## 🅵 listen

```python
def listen(
    target: Union[str, Any],
    listener_name: Optional[str] = None,
    overwrite: bool = False,
):
```
## 🅵 \_update\_thread

```python
def _update_thread():
```

## Classes

## 🅲 \_WatchConfig

```python
class _WatchConfig(dict):
```
## 🅲 \_WatchedFun

```python
class _WatchedFun:
```


### 🅼 \_\_init\_\_

```python
def __init__(self, func: Callable, cfg: _WatchConfig) -> None:
```
### 🅼 \_\_call\_\_

```python
def __call__(self, *args, **kwargs) -> Any:
```
### 🅼 \_\_repr\_\_

```python
def __repr__(self) -> str:
```
