---
title: abc
sidebar_position: 3
---

## TOC

- **Classes:**
  - 🅲 [ConfigInterface](#🅲-configinterface)

## Classes

## 🅲 ConfigInterface

```python
class ConfigInterface(ABC):
```


### 🅼 \_\_setattr\_\_

```python
@abstractmethod
def __setattr__(self, key, value):
```
### 🅼 \_\_getattr\_\_

```python
@abstractmethod
def __getattr__(self, key):
```
### 🅼 update

```python
@abstractmethod
def update(self, another):
```
### 🅼 here

```python
@property
@abstractmethod
def here(self):
```
