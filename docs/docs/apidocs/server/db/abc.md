---
title: abc
sidebar_position: 3
---

## TOC

- **Classes:**
  - 🅲 [FetchType](#🅲-fetchtype)
  - 🅲 [SortType](#🅲-sorttype)
  - 🅲 [ManageableDB](#🅲-manageabledb)

## Classes

## 🅲 FetchType

```python
class FetchType(str, Enum):
    ALL = """all"""
    ONE = """one"""
    MANY = """many"""
```
## 🅲 SortType

```python
class SortType(str, Enum):
    ASC = """ASC"""
    DESC = """DESC"""
```
## 🅲 ManageableDB

```python
class ManageableDB(ABC):
```


### 🅼 size

```python
@abstractmethod
def size(self):
```

get local storage usage in bytes
### 🅼 close

```python
@abstractmethod
def close(self):
```
### 🅼 delete

```python
@abstractmethod
def delete(self):
```

handle delete, a typical behavior is to close connection and remove files
