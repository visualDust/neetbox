---
title: _image
---

## TOC

- **Functions:**
  - 🅵 [figure\_to\_image](#🅵-figure_to_image) - Render matplotlib figure to numpy format.
  - 🅵 [make\_grid](#🅵-make_grid)
  - 🅵 [convert\_to\_HWC](#🅵-convert_to_hwc)
  - 🅵 [add\_image](#🅵-add_image) - send an image to frontend display
  - 🅵 [add\_figure](#🅵-add_figure) - Render matplotlib figure into an image and add it to summary.

## Functions

## 🅵 figure\_to\_image

```python
def figure_to_image(figures, close=True):
```

Render matplotlib figure to numpy format.

Note that this requires the \`\`matplotlib\`\` package.

**Parameters:**

- **figure** (matplotlib.pyplot.figure): figure or a list of figures
- **close** ([bool](https://docs.python.org/3/library/stdtypes.html#boolean-values)): Flag to automatically close the figure

**Returns:**

- **numpy.array**: image in \[CHW\] order
## 🅵 make\_grid

```python
def make_grid(I, ncols=8):
```
## 🅵 convert\_to\_HWC

```python
def convert_to_HWC(tensor, input_format):
```
## 🅵 add\_image

```python
def add_image(name: str, image, dataformats: str = None):
```

send an image to frontend display

**Parameters:**

- **image** (Union[np.array, Image.Image, Tensor]): image from cv2 and PIL.Image as well as tensors are supported
- **name** ([str](https://docs.python.org/3/library/stdtypes.html#text-sequence-type-str)): name of the image, used in frontend display
- **dataformats** ([str](https://docs.python.org/3/library/stdtypes.html#text-sequence-type-str)): if you are passing a tensor as image, please indicate how to understand the tensor. For example, dataformats="NCWH" means the first axis of the tensor is Number of batches, the second axis is Channel, and the third axis is Width, and the fourth axis is Height.
## 🅵 add\_figure

```python
def add_figure(name: str, figure, close: Optional[bool] = True):
```

Render matplotlib figure into an image and add it to summary.

Note that this requires the \`\`matplotlib\`\` package.

**Parameters:**

- **tag**: Data identifier
- **figure** (matplotlib.pyplot.figure): Figure or a list of figures
- **global_step**: Global step value to record
- **close**: Flag to automatically close the figure
- **walltime**: Override default walltime \(time.time\(\)\) of event
