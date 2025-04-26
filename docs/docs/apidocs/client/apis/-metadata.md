---
title: _metadata
sidebar_position: 3
---

## TOC

- **Functions:**
  - 🅵 [add\_hyperparams](#🅵-add_hyperparams) - add/set hyperparams to current run, the added hyperparams will show in frontend
  - 🅵 [set\_run\_name](#🅵-set_run_name) - set the name of current run

## Functions

## 🅵 add\_hyperparams

```python
def add_hyperparams(hparam: dict, name: str = None):
```

add/set hyperparams to current run, the added hyperparams will show in frontend

**Parameters:**

- **hparam** ([dict](https://docs.python.org/3/library/stdtypes.html#mapping-types-dict)): hyperparams
- **name** ([str](https://docs.python.org/3/library/stdtypes.html#text-sequence-type-str)) (default to `None`): name of hyperparams. Defaults to None.
## 🅵 set\_run\_name

```python
def set_run_name(name: str):
```

set the name of current run

**Parameters:**

- **name** ([str](https://docs.python.org/3/library/stdtypes.html#text-sequence-type-str)): name of current run
