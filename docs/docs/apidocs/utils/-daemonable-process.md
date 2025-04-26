---
title: _daemonable_process
sidebar_position: 3
---

## TOC

- **Functions:**
  - 🅵 [main](#🅵-main)
- **Classes:**
  - 🅲 [DaemonableProcess](#🅲-daemonableprocess)

## Functions

## 🅵 main

```python
def main():
```

## Classes

## 🅲 DaemonableProcess

```python
class DaemonableProcess:
```


### 🅼 \_\_init\_\_

```python
def __init__(
    self,
    target: Union[str, ModuleType],
    args: List = [],
    mode: Literal["attached", "detached"],
    redirect_stdout=None,
    redirect_stderr=subprocess.STDOUT,
    use_os_spawn_for_daemon=False,
    redirect_stdin=subprocess.DEVNULL,
    env_append=None,
):
```
### 🅼 is\_daemon

```python
@property
def is_daemon(self):
```
### 🅼 mode

```python
@property
def mode(self):
```
### 🅼 start

```python
def start(self, shell=False, path=None):
```
### 🅼 terminate

```python
def terminate(self):
```
