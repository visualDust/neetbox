---
title: extension
---

## TOC

- **Attributes:**
  - 🅰 [\_\_QUERY\_AFTER\_LOAD\_WORKSPACE](#🅰-__query_after_load_workspace)
  - 🅰 [on\_workspace\_loaded](#🅰-on_workspace_loaded)
- **Functions:**
  - 🅵 [\_scan\_sub\_modules](#🅵-_scan_sub_modules)
  - 🅵 [\_init\_extensions](#🅵-_init_extensions) - DO NOT call before workspace config load

## Attributes

## 🅰 \_\_QUERY\_AFTER\_LOAD\_WORKSPACE

```python
__QUERY_AFTER_LOAD_WORKSPACE = Registry("__QUERY_AFTER_LOAD_WORKSPACE")
```

## 🅰 on\_workspace\_loaded

```python
on_workspace_loaded = __QUERY_AFTER_LOAD_WORKSPACE.register
```


## Functions

## 🅵 \_scan\_sub\_modules

```python
def _scan_sub_modules():
```
## 🅵 \_init\_extensions

```python
def _init_extensions():
```

DO NOT call before workspace config load
