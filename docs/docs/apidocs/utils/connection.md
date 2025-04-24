---
title: connection
---

## TOC

- **Attributes:**
  - 🅰 [httpxClient](#🅰-httpxclient) - httpx client
- **Classes:**
  - 🅲 [WebsocketClient](#🅲-websocketclient)

## Attributes

## 🅰 httpxClient

```python
httpxClient: httpx.Client = httpx.Client(proxy=None) #httpx client
```


## Classes

## 🅲 WebsocketClient

```python
class WebsocketClient:
```


### 🅼 \_\_init\_\_

```python
def __init__(
    self,
    url,
    on_open,
    on_message,
    on_error,
    on_close,
    offline_message_buffer_size=0,
):
```
### 🅼 connect

```python
def connect(self, reconnect=1):
```
### 🅼 is\_connected

```python
def is_connected(self) -> bool:
```
### 🅼 send

```python
def send(self, message: EventMsg):
```
