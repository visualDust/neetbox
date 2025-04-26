---
title: _progress
sidebar_position: 3
---

## TOC

- **Classes:**
  - 🅲 [Progress](#🅲-progress)

## Classes

## 🅲 Progress

```python
class Progress:
    total: int = None
    done: int = None
    iterator: enumerate = None
    timestamp: str = None
```


### 🅼 \_\_init\_\_

```python
def __init__(self, input: Union[int, enumerate, any], name=None):
```

Decorate an iterable object, returning an iterator. Neetbox will send progress to frontend while you are iterating through it.

**Parameters:**

- **input** ([Union](https://docs.python.org/3/library/typing.html#typing.Union)[[int](https://docs.python.org/3/library/stdtypes.html#numeric-types-int-float-complex), enumerate, any]): Something to iterate or something to create enumeratable object.
### 🅼 \_\_enter\_\_

```python
def __enter__(self):
```
### 🅼 \_\_exit\_\_

```python
def __exit__(self, type, value, traceback):
```
### 🅼 \_\_iter\_\_

```python
def __iter__(self):
```
### 🅼 \_update

```python
@classmethod
def _update(
    cls,
    name: str,
    what_is_current: any,
    done: int,
    total: int,
    rate: float,
    timestamp=None,
):
```
### 🅼 \_\_next\_\_

```python
def __next__(self):
```
### 🅼 \_\_len\_\_

```python
def __len__(self):
```
