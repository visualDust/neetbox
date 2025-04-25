---
title: _stdout
---

## TOC

- **Attributes:**
  - 🅰 [LogWriters](#🅰-logwriters)
  - 🅰 [console](#🅰-console)
  - 🅰 [whom2color](#🅰-whom2color)
  - 🅰 [supported\_colors](#🅰-supported_colors)
  - 🅰 [supported\_text\_styles](#🅰-supported_text_styles)
- **Functions:**
  - 🅵 [log\_write\_stdout](#🅵-log_write_stdout)

## Attributes

## 🅰 LogWriters

```python
LogWriters = Registry("LOG_WRITERS")
```

## 🅰 console

```python
console = Console()
```

## 🅰 whom2color

```python
whom2color = {}
```

## 🅰 supported\_colors

```python
supported_colors = ["red", "green", "blue", "cyan", "yellow", "magenta"]
```

## 🅰 supported\_text\_styles

```python
supported_text_styles = ["bold", "italic", "blink", "dim"]
```


## Functions

## 🅵 log\_write\_stdout

```python
def log_write_stdout(log: RawLog):
```
