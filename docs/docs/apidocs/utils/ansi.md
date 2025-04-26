---
title: ansi
sidebar_position: 3
---

## TOC

- **Functions:**
  - 🅵 [is\_pure\_ansi](#🅵-is_pure_ansi)
  - 🅵 [is\_fs\_case\_sensitive](#🅵-is_fs_case_sensitive) - Check if the file system is case sensitive
  - 🅵 [legal\_file\_name\_of](#🅵-legal_file_name_of) - Remove invalid characters for windows file systems
  - 🅵 [is\_jsonable](#🅵-is_jsonable)

## Functions

## 🅵 is\_pure\_ansi

```python
def is_pure_ansi(text: str) -> bool:
```
## 🅵 is\_fs\_case\_sensitive

```python
def is_fs_case_sensitive():
```

Check if the file system is case sensitive

**Returns:**

- **[bool](https://docs.python.org/3/library/stdtypes.html#boolean-values)**: True if case sensitive
## 🅵 legal\_file\_name\_of

```python
def legal_file_name_of(text: str) -> str:
```

Remove invalid characters for windows file systems

**Parameters:**

- **title** ([str](https://docs.python.org/3/library/stdtypes.html#text-sequence-type-str)): the given title

**Returns:**

- **[str](https://docs.python.org/3/library/stdtypes.html#text-sequence-type-str)**: valid text
## 🅵 is\_jsonable

```python
def is_jsonable(x):
```
