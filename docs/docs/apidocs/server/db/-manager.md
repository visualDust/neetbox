---
title: _manager
sidebar_position: 3
---

## TOC

- **Attributes:**
  - 🅰 [ModuleNameType](#🅰-modulenametype)
  - 🅰 [DbIdType](#🅰-dbidtype)
  - 🅰 [manager](#🅰-manager)
- **Classes:**
  - 🅲 [DBConnectionManager](#🅲-dbconnectionmanager)

## Attributes

## 🅰 ModuleNameType

```python
ModuleNameType = str
```

## 🅰 DbIdType

```python
DbIdType = str
```

## 🅰 manager

```python
manager = DBConnectionManager()
```


## Classes

## 🅲 DBConnectionManager

```python
class DBConnectionManager:
    _POOL: Dict[ModuleNameType, Dict[DbIdType, ManageableDB]] = defaultdict(
        dict
    )
```


### 🅼 current

```python
@property
def current(self):
```
### 🅼 \_\_init\_\_

```python
def __init__(self):
```
