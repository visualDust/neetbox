---
title: condition
sidebar_position: 3
---

## TOC

- **Classes:**
  - 🅲 [ProjectDbQueryCondition](#🅲-projectdbquerycondition)

## Classes

## 🅲 ProjectDbQueryCondition

```python
class ProjectDbQueryCondition:
```


### 🅼 \_\_init\_\_

```python
def __init__(
    self,
    id: Union[Tuple[int, int], int] = None,
    timestamp: Union[Tuple[str, str], str] = None,
    series: str = None,
    run_id: Union[str, int] = None,
    limit: int = None,
    order: Dict[str, SortType] = {},
) -> None:
```
### 🅼 loads

```python
@classmethod
def loads(cls, json_data):
```
### 🅼 dumpt

```python
def dumpt(self):
```
