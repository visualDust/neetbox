---
title: user
---

## TOC

- **Attributes:**
  - 🅰 [\_GLOBAL\_CONFIG](#🅰-_global_config)
  - 🅰 [\_GLOBAL\_CONFIG\_FILE\_NAME](#🅰-_global_config_file_name)
- **Functions:**
  - 🅵 [update\_dict\_recursively\_on\_missing\_keys](#🅵-update_dict_recursively_on_missing_keys) - Update dictionary B with keys from dictionary A. Add missing keys from A to B,
  - 🅵 [overwrite\_create\_local](#🅵-overwrite_create_local)
  - 🅵 [read\_create\_local](#🅵-read_create_local)
  - 🅵 [set](#🅵-set)
  - 🅵 [get](#🅵-get)

## Attributes

## 🅰 \_GLOBAL\_CONFIG

```python
_GLOBAL_CONFIG = {
    MACHINE_ID_KEY: str(uuid4()),
    "vault": get_create_initial_neetbox_data_directory(),
    "bypass-db-version-check": True,
}
```

## 🅰 \_GLOBAL\_CONFIG\_FILE\_NAME

```python
_GLOBAL_CONFIG_FILE_NAME = f"""neetbox.global.toml"""
```


## Functions

## 🅵 update\_dict\_recursively\_on\_missing\_keys

```python
def update_dict_recursively_on_missing_keys(A, B):
```

Update dictionary B with keys from dictionary A. Add missing keys from A to B,

but do not overwrite existing keys in B. Handles nested dictionaries recursively.
## 🅵 overwrite\_create\_local

```python
def overwrite_create_local(config: dict):
```
## 🅵 read\_create\_local

```python
def read_create_local():
```
## 🅵 set

```python
def set(key, value):
```
## 🅵 get

```python
def get(key=None):
```
