---
title: platform
sidebar_position: 3
---

## TOC

- **Attributes:**
  - 🅰 [platform](#🅰-platform) - watch updates in daemon
- **Functions:**
  - 🅵 [load\_send\_platform\_info](#🅵-load_send_platform_info)
- **Classes:**
  - 🅲 [PlatformInfo](#🅲-platforminfo)

## Attributes

## 🅰 platform

```python
platform = PlatformInfo() #watch updates in daemon
```


## Functions

## 🅵 load\_send\_platform\_info

```python
@on_workspace_loaded(name="show-platform-information")
def load_send_platform_info():
```

## Classes

## 🅲 PlatformInfo

```python
class PlatformInfo:
```


### 🅼 \_\_init\_\_

```python
def __init__(self):
```
### 🅼 username

```python
@property
def username(self):
```
### 🅼 machine

```python
@property
def machine(self):
```
### 🅼 processor

```python
@property
def processor(self):
```
### 🅼 os\_name

```python
@property
def os_name(self):
```
### 🅼 os\_release

```python
@property
def os_release(self):
```
### 🅼 python\_version

```python
@property
def python_version(self):
```
### 🅼 python\_build

```python
@property
def python_build(self):
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
