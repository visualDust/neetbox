---
title: _action
sidebar_position: 3
---

## TOC

- **Attributes:**
  - 🅰 [actionManager](#🅰-actionmanager)
- **Classes:**
  - 🅲 [Action](#🅲-action)
  - 🅲 [ActionManager](#🅲-actionmanager)

## Attributes

## 🅰 actionManager

```python
actionManager = ActionManager()
```


## Classes

## 🅲 Action

```python
class Action(Callable):
```


### 🅼 \_\_init\_\_

```python
def __init__(
    self,
    function: Callable,
    name: str = None,
    description: str = None,
    blocking: bool = False,
    **kwargs
):
```
### 🅼 get\_props\_dict

```python
def get_props_dict(self):
```
### 🅼 \_\_call\_\_

```python
def __call__(self, **argv):
```
### 🅼 eval\_call

```python
def eval_call(self, params: dict):
```
## 🅲 ActionManager

```python
class ActionManager:
    ACTION_POOL: Registry = Registry("__NEET_ACTIONS")
    _is_initialized = False
```


### 🅼 get\_action\_dict

```python
def get_action_dict(self):
```
### 🅼 eval\_call

```python
def eval_call(
    self, name: str, params: dict, callback: Optional[Callable] = None
):
```
### 🅼 \_initialize

```python
def _initialize(self):
```
### 🅼 register

```python
def register(
    self,
    name: Optional[str] = None,
    description: str = None,
    blocking: bool = False,
):
```

register function as action visiable on frontend page

**Parameters:**

- **name** ([Optional](https://docs.python.org/3/library/typing.html#typing.Optional)[[str](https://docs.python.org/3/library/stdtypes.html#text-sequence-type-str)]) (default to `None(neetbox will use the function name when set to None)`): name of the action. Defaults to None\(neetbox will use the function name when set to None\).
- **description** ([str](https://docs.python.org/3/library/stdtypes.html#text-sequence-type-str)) (default to `None(neetbox will use function docs as default when set to None)`): description of the action. Defaults to None\(neetbox will use function docs as default when set to None\).
- **blocking** ([bool](https://docs.python.org/3/library/stdtypes.html#boolean-values)) (default to `False`): whether to run the action in a blocked query. Defaults to False.

**Returns:**

- **[Callable](https://docs.python.org/3/library/typing.html#typing.Callable)**: the function itself.
### 🅼 \_register

```python
def _register(
    self,
    function: Callable,
    name: str = None,
    description: str = None,
    blocking: bool = False,
):
```
