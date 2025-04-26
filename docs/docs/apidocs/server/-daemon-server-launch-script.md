---
title: _daemon_server_launch_script
sidebar_position: 3
---

## TOC

- **Functions:**
  - 🅵 [run](#🅵-run)
  - 🅵 [start](#🅵-start) - start a server as background daemon

## Functions

## 🅵 run

```python
def run(config):
```
## 🅵 start

```python
def start(config) -> Optional[int]:
```

start a server as background daemon

**Parameters:**

- **config** ([dict](https://docs.python.org/3/library/stdtypes.html#mapping-types-dict)): server launch config

**Returns:**

- **[DaemonableProcess](../utils/-daemonable-process#🅲-daemonableprocess)**: the daemon process
