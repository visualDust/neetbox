---
title: _messaging
sidebar_position: 3
---

## TOC

- **Attributes:**
  - 🅰 [console](#🅰-console)
  - 🅰 [MessageType](#🅰-messagetype)
  - 🅰 [NameType](#🅰-nametype)
  - 🅰 [messaging](#🅰-messaging) - singleton
- **Classes:**
  - 🅲 [MessageListener](#🅲-messagelistener)
  - 🅲 [Messaging](#🅲-messaging)

## Attributes

## 🅰 console

```python
console = Console()
```

## 🅰 MessageType

```python
MessageType = str
```

## 🅰 NameType

```python
NameType = str
```

## 🅰 messaging

```python
messaging = Messaging() #singleton
```


## Classes

## 🅲 MessageListener

```python
@dataclass
class MessageListener:
    creator: TracebackInfo = None
    message_type: str = None
    name: str = None
    func: Callable = None
```


### 🅼 json

```python
@property
def json(self):
```
## 🅲 Messaging

```python
class Messaging:
    _listener_dicts: Dict[MessageType, Dict[NameType, MessageListener]] = (
        defaultdict(dict)
    )
```


### 🅼 listener

```python
def listener(self, message_type: str, name: str = None):
```
### 🅼 send

```python
def send(self, message_type: str, message: any = None):
```
### 🅼 json

```python
@property
def json(self):
```
