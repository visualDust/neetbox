---
title: project
---

## TOC

- **Attributes:**
  - 🅰 [CONFIG\_FILE\_NAME](#🅰-config_file_name) - later will be overwrite by workspace config file
  - 🅰 [NEETBOX\_VERSION](#🅰-neetbox_version) - later will be overwrite by workspace config file
  - 🅰 [\_DEFAULT\_WORKSPACE\_CONFIG](#🅰-_default_workspace_config) - later will be overwrite by workspace config file
  - 🅰 [\_QUERY\_ADD\_EXTENSION\_DEFAULT\_CONFIG](#🅰-_query_add_extension_default_config) - if workspace already loaded
  - 🅰 [\_IS\_WORKSPACE\_LOADED](#🅰-_is_workspace_loaded) - if workspace already loaded
  - 🅰 [\_QUERY\_AFTER\_CONFIG\_LOAD](#🅰-_query_after_config_load) - if workspace already loaded
- **Functions:**
  - 🅵 [\_obtain\_new\_run\_id](#🅵-_obtain_new_run_id) - put a new run id into config. do not run before workspace loaded as a project.
  - 🅵 [on\_config\_loaded](#🅵-on_config_loaded)
  - 🅵 [export\_default\_config](#🅵-export_default_config)
  - 🅵 [\_build\_global\_config\_dict\_for\_module](#🅵-_build_global_config_dict_for_module) - build a global config from a local config of a module. for example:
  - 🅵 [\_update\_default\_config\_from\_config\_register](#🅵-_update_default_config_from_config_register) - iterate through config register to read their default config and write the result into global config. DO NOT run after workspace loaded.
  - 🅵 [\_update\_default\_workspace\_config\_with](#🅵-_update_default_workspace_config_with)
  - 🅵 [\_init\_workspace](#🅵-_init_workspace)
  - 🅵 [\_load\_workspace\_config](#🅵-_load_workspace_config)
  - 🅵 [\_create\_load\_workspace](#🅵-_create_load_workspace)
  - 🅵 [\_get\_module\_level\_config](#🅵-_get_module_level_config) - get a module level config from global config

## Attributes

## 🅰 CONFIG\_FILE\_NAME

```python
CONFIG_FILE_NAME = f"""neetbox.toml""" #later will be overwrite by workspace config file
```

## 🅰 NEETBOX\_VERSION

```python
NEETBOX_VERSION = version("neetbox") #later will be overwrite by workspace config file
```

## 🅰 \_DEFAULT\_WORKSPACE\_CONFIG

```python
_DEFAULT_WORKSPACE_CONFIG = {
    NAME_KEY: os.path.basename(os.path.normpath(os.getcwd())),
    "version": NEETBOX_VERSION,
    PROJECT_ID_KEY: str(uuid4()),
    "extension": {"autoload": True},
    "client": {
        "enable": True,
        "host": "127.0.0.1",
        "port": 20202,
        "allowIpython": False,
        "mute": True,
        "mode": "detached",
        "uploadInterval": 1,
        "shell": {"enable": True, "daemon": True},
    },
} #later will be overwrite by workspace config file
```

## 🅰 \_QUERY\_ADD\_EXTENSION\_DEFAULT\_CONFIG

```python
_QUERY_ADD_EXTENSION_DEFAULT_CONFIG = [] #if workspace already loaded
```

## 🅰 \_IS\_WORKSPACE\_LOADED

```python
_IS_WORKSPACE_LOADED = False #if workspace already loaded
```

## 🅰 \_QUERY\_AFTER\_CONFIG\_LOAD

```python
_QUERY_AFTER_CONFIG_LOAD = [] #if workspace already loaded
```


## Functions

## 🅵 \_obtain\_new\_run\_id

```python
def _obtain_new_run_id():
```

put a new run id into config. do not run before workspace loaded as a project.

**Returns:**

- **[str](https://docs.python.org/3/library/stdtypes.html#text-sequence-type-str)**: new run id
## 🅵 on\_config\_loaded

```python
def on_config_loaded(func):
```
## 🅵 export\_default\_config

```python
def export_default_config(func):
```
## 🅵 \_build\_global\_config\_dict\_for\_module

```python
def _build_global_config_dict_for_module(module, local_config):
```

build a global config from a local config of a module. for example:

- local config in neetbox/moduleA/some.py: \{ \{ "a" : 1 \} \}
- the returned global config: \{
    moduleA: \{
        some: \{
            "a" : 1
        \}
    \}
\}

**Parameters:**

- **module** (_type_): \_description\_
- **local_config** (_type_): \_description\_
## 🅵 \_update\_default\_config\_from\_config\_register

```python
def _update_default_config_from_config_register():
```

iterate through config register to read their default config and write the result into global config. DO NOT run after workspace loaded.

**Raises:**

- **e**: any possible exception
## 🅵 \_update\_default\_workspace\_config\_with

```python
def _update_default_workspace_config_with(cfg: dict):
```
## 🅵 \_init\_workspace

```python
def _init_workspace(path=None, **kwargs) -> bool:
```
## 🅵 \_load\_workspace\_config

```python
def _load_workspace_config(folder=".", load_only=False):
```
## 🅵 \_create\_load\_workspace

```python
def _create_load_workspace(folder="."):
```
## 🅵 \_get\_module\_level\_config

```python
def _get_module_level_config(
    module: Union[str, types.ModuleType] = None, **kwargs
):
```

get a module level config from global config

**Parameters:**

- **module** (str or module) (default to `None(which means neetbox will automatically find the module in which this function is called). if you want to get all the global config, pass "@" for module`): which module's config to get. Defaults to None\(which means neetbox will automatically find the module in which this function is called\). if you want to get all the global config, pass "@" for module.

**Returns:**

- **[dict](https://docs.python.org/3/library/stdtypes.html#mapping-types-dict)**: the config you want.
