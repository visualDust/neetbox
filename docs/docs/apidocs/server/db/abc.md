---
title: abc
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
```
## 🅲 SortType

```python
class SortType(str, Enum):
```
## 🅲 ManageableDB

```python
class ManageableDB(ABC):
```


### 🅼 size

```python
def size(self):
```

get local storage usage in bytes
### 🅼 close

```python
def close(self):
```
### 🅼 delete

```python
def delete(self):
```

handle delete, a typical behavior is to close connection and remove files
