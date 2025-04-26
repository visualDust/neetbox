---
title: fastapi
sidebar_position: 2
---

## TOC

- **Attributes:**
  - 🅰 [logger](#🅰-logger)
  - 🅰 [serverapp](#🅰-serverapp)
  - 🅰 [front\_end\_dist\_path](#🅰-front_end_dist_path)
- **Functions:**
  - 🅵 [redirect\_to\_web](#🅵-redirect_to_web)
  - 🅵 [serve\_static\_root](#🅵-serve_static_root)

## Attributes

## 🅰 logger

```python
logger = Logger("FASTAPI", skip_writers_names=["ws"])
```

## 🅰 serverapp

```python
serverapp = FastAPI()
```

## 🅰 front\_end\_dist\_path

```python
front_end_dist_path = os.path.join(
    os.path.dirname(neetbox.__file__), "frontend_dist"
)
```


## Functions

## 🅵 redirect\_to\_web

```python
@serverapp.get("/")
def redirect_to_web():
```
## 🅵 serve\_static\_root

```python
@serverapp.get("/web/{path:path}")
def serve_static_root(path: str):
```
