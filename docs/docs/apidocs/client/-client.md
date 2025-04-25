---
title: _client
---

## TOC

- **Attributes:**
  - 🅰 [logger](#🅰-logger)
  - 🅰 [connection](#🅰-connection) - assign this connection to websocket log writer
  - 🅰 [LogWriters](#🅰-logwriters)
- **Functions:**
  - 🅵 [addr\_of\_api](#🅵-addr_of_api)
  - 🅵 [log\_writer\_ws](#🅵-log_writer_ws)
- **Classes:**
  - 🅲 [NeetboxClient](#🅲-neetboxclient)

## Attributes

## 🅰 logger

```python
logger = Logger(name_alias="CLIENT", skip_writers_names=["ws"])
```

## 🅰 connection

```python
connection = NeetboxClient() #assign this connection to websocket log writer
```

## 🅰 LogWriters

```python
LogWriters = Registry("LOG_WRITERS")
```


## Functions

## 🅵 addr\_of\_api

```python
def addr_of_api(api, http_root=None):
```
## 🅵 log\_writer\_ws

```python
def log_writer_ws(log: RawLog):
```

## Classes

## 🅲 NeetboxClient

```python
class NeetboxClient:
```


### 🅼 \_\_init\_\_

```python
def __init__(self) -> None:
```
### 🅼 wait\_should\_online

```python
def wait_should_online(self):
```
### 🅼 post\_check\_online

```python
def post_check_online(self, api: str, root: str = None, *args, **kwargs):
```
### 🅼 post

```python
def post(self, api: str, root: str = None, *args, **kwargs):
```
### 🅼 get\_check\_online

```python
def get_check_online(self, api: str, root: str = None, *args, **kwargs):
```
### 🅼 get

```python
def get(self, api: str, root: str = None, *args, **kwargs):
```
### 🅼 put\_check\_online

```python
def put_check_online(self, api: str, root: str = None, *args, **kwargs):
```
### 🅼 put

```python
def put(self, api: str, root: str = None, *args, **kwargs):
```
### 🅼 delete\_check\_online

```python
def delete_check_online(self, api: str, root: str = None, *args, **kwargs):
```
### 🅼 delete

```python
def delete(self, api: str, root: str = None, *args, **kwargs):
```
### 🅼 subscribe

```python
def subscribe(self, event_type_name: str, callback):
```
### 🅼 unsubscribe

```python
def unsubscribe(self, event_type_name: str, callback):
```
### 🅼 ws\_subscribe

```python
def ws_subscribe(self, event_type_name: str):
```

let a function subscribe to ws messages with event type name.

\!\!\! dfor inner APIs only, do not use this in your code\!
\!\!\! developers should contorl blocking on their own functions

**Parameters:**

- **function** ([Callable](https://docs.python.org/3/library/typing.html#typing.Callable)): who is subscribing the event type
- **event_type_name** ([str](https://docs.python.org/3/library/stdtypes.html#text-sequence-type-str)) (default to `None`): Which event to listen. Defaults to None.
### 🅼 check\_server\_connectivity

```python
def check_server_connectivity(self, config=None):
```
### 🅼 initialize\_connection

```python
def initialize_connection(self, config=None):
```
### 🅼 on\_ws\_open

```python
def on_ws_open(self, ws: WebsocketClient):
```
### 🅼 on\_ws\_err

```python
def on_ws_err(self, ws: WebsocketClient, msg):
```
### 🅼 on\_ws\_close

```python
def on_ws_close(self, ws: WebsocketClient, close_status_code, close_msg):
```
### 🅼 on\_ws\_message

```python
def on_ws_message(self, ws: WebsocketClient, message):
```
### 🅼 ws\_send

```python
def ws_send(
    self,
    event_type: str,
    payload: dict,
    series=None,
    timestamp: str = None,
    event_id=-1,
    identity_type=IdentityType.CLI,
    _history_len=-1,
):
```
