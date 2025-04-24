---
title: project
---

## TOC

- **Attributes:**
  - 🅰 [CONFIG\_FILE\_NAME](#🅰-config_file_name) - later will be overwrite by workspace config file
  - 🅰 [NEETBOX\_VERSION](#🅰-neetbox_version) - later will be overwrite by workspace config file
- **Functions:**
  - 🅵 [on\_config\_loaded](#🅵-on_config_loaded)
  - 🅵 [export\_default\_config](#🅵-export_default_config)

## Attributes

## 🅰 CONFIG\_FILE\_NAME

```python
CONFIG_FILE_NAME = f"""neetbox.toml""" #later will be overwrite by workspace config file
```

## 🅰 NEETBOX\_VERSION

```python
NEETBOX_VERSION = version("neetbox") #later will be overwrite by workspace config file
```


## Functions

## 🅵 on\_config\_loaded

```python
def on_config_loaded(func):
```
## 🅵 export\_default\_config

```python
def export_default_config(func):
```
