---
title: _messaging
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
class MessageListener:
```


### 🅼 json

```python
def json(self):
```
## 🅲 Messaging

```python
class Messaging:
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
def json(self):
```
