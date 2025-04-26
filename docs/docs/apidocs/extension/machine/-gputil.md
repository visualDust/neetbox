---
title: _gputil
sidebar_position: 3
---

## TOC

- **Functions:**
  - 🅵 [safeFloatCast](#🅵-safefloatcast)
  - 🅵 [getGPUs](#🅵-getgpus)
  - 🅵 [getAvailable](#🅵-getavailable)
  - 🅵 [getAvailability](#🅵-getavailability)
  - 🅵 [getFirstAvailable](#🅵-getfirstavailable)
  - 🅵 [showUtilization](#🅵-showutilization)
- **Classes:**
  - 🅲 [GPU](#🅲-gpu)

## Functions

## 🅵 safeFloatCast

```python
def safeFloatCast(strNumber):
```
## 🅵 getGPUs

```python
def getGPUs():
```
## 🅵 getAvailable

```python
def getAvailable(
    order="first",
    limit=1,
    maxLoad=0.5,
    maxMemory=0.5,
    memoryFree=0,
    includeNan=False,
    excludeID=[],
    excludeUUID=[],
):
```
## 🅵 getAvailability

```python
def getAvailability(
    GPUs,
    maxLoad=0.5,
    maxMemory=0.5,
    memoryFree=0,
    includeNan=False,
    excludeID=[],
    excludeUUID=[],
):
```
## 🅵 getFirstAvailable

```python
def getFirstAvailable(
    order="first",
    maxLoad=0.5,
    maxMemory=0.5,
    attempts=1,
    interval=900,
    verbose=False,
    includeNan=False,
    excludeID=[],
    excludeUUID=[],
):
```
## 🅵 showUtilization

```python
def showUtilization(all=False, attrList=None, useOldCode=False):
```

## Classes

## 🅲 GPU

```python
class GPU:
```


### 🅼 \_\_init\_\_

```python
def __init__(
    self,
    ID,
    uuid,
    load,
    memoryTotal,
    memoryUsed,
    memoryFree,
    driver,
    gpu_name,
    serial,
    display_mode,
    display_active,
    temp_gpu,
):
```
