---
title: hardware
sidebar_position: 3
---

## TOC

- **Attributes:**
  - 🅰 [hardware](#🅰-hardware) - watch updates in daemon
- **Functions:**
  - 🅵 [return\_default\_config](#🅵-return_default_config)
  - 🅵 [load\_monit\_hardware](#🅵-load_monit_hardware)
- **Classes:**
  - 🅲 [CpuStatus](#🅲-cpustatus)
  - 🅲 [CpuStatistics](#🅲-cpustatistics)
  - 🅲 [MemoryStatus](#🅲-memorystatus)
  - 🅲 [NvGpuStatus](#🅲-nvgpustatus)
  - 🅲 [Hardware](#🅲-hardware)

## Attributes

## 🅰 hardware

```python
hardware = Hardware() #watch updates in daemon
```


## Functions

## 🅵 return\_default\_config

```python
@export_default_config
def return_default_config() -> dict:
```
## 🅵 load\_monit\_hardware

```python
@on_workspace_loaded(name="hardware-monit")
def load_monit_hardware():
```

## Classes

## 🅲 CpuStatus

```python
class CpuStatus:
```


### 🅼 \_\_init\_\_

```python
def __init__(self, id=-1, percentage=0.0, frequency=0.0):
```
### 🅼 \_\_str\_\_

```python
def __str__(self) -> str:
```
### 🅼 json

```python
@property
def json(self):
```
## 🅲 CpuStatistics

```python
class CpuStatistics:
```


### 🅼 \_\_init\_\_

```python
def __init__(self, ctx_switches, interrupts, soft_interrupts, syscalls) -> None:
```
### 🅼 json

```python
@property
def json(self):
```
### 🅼 \_\_str\_\_

```python
def __str__(self) -> str:
```
## 🅲 MemoryStatus

```python
class MemoryStatus:
```


### 🅼 \_\_init\_\_

```python
def __init__(self, total, available, used, free) -> None:
```
### 🅼 json

```python
@property
def json(self):
```
### 🅼 \_\_str\_\_

```python
def __str__(self) -> str:
```
## 🅲 NvGpuStatus

```python
class NvGpuStatus(GPU):
```


### 🅼 parse

```python
@classmethod
def parse(cls, other: GPU):
```
### 🅼 json

```python
@property
def json(self):
```
### 🅼 \_\_str\_\_

```python
def __str__(self) -> str:
```
## 🅲 Hardware

```python
class Hardware:
    watch_thread: Thread = None
    _do_watch: bool = True
    _update_interval: float = 1.0
    _cpus: List[CpuStatus] = None
    _gpus: List[NvGpuStatus] = None
    _cpu_statistics: CpuStatistics = None
    _memory: MemoryStatus = None
    _on_update_call_backs = []
```


### 🅼 \_\_init\_\_

```python
def __init__(self) -> None:
```
### 🅼 cpus

```python
@property
def cpus(self):
```
### 🅼 cpu\_statistics

```python
@property
def cpu_statistics(self):
```
### 🅼 memory

```python
@property
def memory(self):
```
### 🅼 gpus

```python
@property
def gpus(self):
```
### 🅼 with\_gpu

```python
@property
def with_gpu(self):
```
### 🅼 json

```python
@property
def json(self):
```
### 🅼 add\_on\_update\_call\_back

```python
def add_on_update_call_back(self, func: Callable):
```
### 🅼 set\_start\_update\_intervel

```python
def set_start_update_intervel(self, intervel=1.0) -> None:
```
