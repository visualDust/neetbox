# -*- coding: utf-8 -*-
#
# Author: GavinGong aka VisualDust
# URL:    https://gong.host
# Date:   20231211

import io
from typing import Optional

import cv2
import numpy as np
from PIL import Image

from neetbox._daemon._protocol import *
from neetbox._daemon.client._client import connection
from neetbox.config import get_project_id, get_run_id
from neetbox.logging import logger
from neetbox.utils.x2numpy import *

# ===================== IMAGE things ===================== #


def figure_to_image(figures, close=True):
    """Render matplotlib figure to numpy format.

    Note that this requires the ``matplotlib`` package.

    Args:
        figure (matplotlib.pyplot.figure) or list of figures: figure or a list of figures
        close (bool): Flag to automatically close the figure

    Returns:
        numpy.array: image in [CHW] order
    """
    import numpy as np

    try:
        import matplotlib.backends.backend_agg as plt_backend_agg
        import matplotlib.pyplot as plt
    except ModuleNotFoundError:
        print("please install matplotlib")

    def render_to_rgb(figure):
        canvas = plt_backend_agg.FigureCanvasAgg(figure)
        canvas.draw()
        data = np.frombuffer(canvas.buffer_rgba(), dtype=np.uint8)
        w, h = figure.canvas.get_width_height()
        image_hwc = data.reshape([h, w, 4])[:, :, 0:3]
        image_chw = np.moveaxis(image_hwc, source=2, destination=0)
        if close:
            plt.close(figure)
        return image_chw

    if isinstance(figures, list):
        images = [render_to_rgb(figure) for figure in figures]
        return np.stack(images)
    else:
        image = render_to_rgb(figures)
        return image


def make_grid(I, ncols=8):
    # I: N1HW or N3HW
    import numpy as np

    assert isinstance(I, np.ndarray), "plugin error, should pass numpy array here"
    if I.shape[1] == 1:
        I = np.concatenate([I, I, I], 1)
    assert I.ndim == 4 and I.shape[1] == 3 or I.shape[1] == 4
    nimg = I.shape[0]
    H = I.shape[2]
    W = I.shape[3]
    ncols = min(nimg, ncols)
    nrows = int(np.ceil(float(nimg) / ncols))
    canvas = np.zeros((I.shape[1], H * nrows, W * ncols), dtype=I.dtype)
    i = 0
    for y in range(nrows):
        for x in range(ncols):
            if i >= nimg:
                break
            canvas[:, y * H : (y + 1) * H, x * W : (x + 1) * W] = I[i]
            i = i + 1
    return canvas


def convert_to_HWC(tensor, input_format):  # tensor: numpy array
    assert len(set(input_format)) == len(
        input_format
    ), "You an not use the same dimension shorthand twice. input_format: {}".format(input_format)
    assert len(tensor.shape) == len(
        input_format
    ), "size of input tensor and input format are different. tensor shape: {}, input_format: {}".format(
        tensor.shape, input_format
    )
    input_format = input_format.upper()

    if len(input_format) == 4:
        index = [input_format.find(c) for c in "NCHW"]
        tensor_NCHW = tensor.transpose(index)
        tensor_CHW = make_grid(tensor_NCHW)
        return tensor_CHW.transpose(1, 2, 0)

    if len(input_format) == 3:
        index = [input_format.find(c) for c in "HWC"]
        tensor_HWC = tensor.transpose(index)
        if tensor_HWC.shape[2] == 1:
            tensor_HWC = np.concatenate([tensor_HWC, tensor_HWC, tensor_HWC], 2)
        return tensor_HWC

    if len(input_format) == 2:
        index = [input_format.find(c) for c in "HW"]
        tensor = tensor.transpose(index)
        tensor = np.stack([tensor, tensor, tensor], 2)
        return tensor


def add_image(name: str, image, dataformats: str = None):
    """send an image to frontend display

    Args:
        image (Union[np.array, Image.Image]): image from cv2 and PIL.Image are supported
        name (str): name of the image, used in frontend display
    """
    if isinstance(image, Image.Image):  # is PIL Image
        with io.BytesIO() as image_bytes_stream:
            # convert PIL Image to bytes
            image.save(image_bytes_stream, format="PNG")
            image_bytes = image_bytes_stream.getvalue()
    else:  # try convert numpy
        dataformats = dataformats or "CHW"
        image = make_np(image)
        image = convert_to_HWC(image, dataformats)
        if image.dtype != np.uint8:
            image = (image * 255.0).astype(np.uint8)

        if isinstance(image, np.ndarray):  # convert ndarray to bytes
            _, im_buf_arr = cv2.imencode(".png", image)
            image_bytes = im_buf_arr.tobytes()

    # send bytes
    project_id = get_project_id()
    run_id = get_run_id()
    try:
        message = EventMsg(
            project_id=project_id,
            run_id=run_id,
            who=IdentityType.CLI,
            series=name,
            event_type=EVENT_TYPE_NAME_IMAGE,
        )
        connection.post(
            api=f"/image/{project_id}",
            data={"json": message.dumps()},
            files={"image": image_bytes},
        )
    except Exception as e:
        logger.warn(f"unable to upload image: {e}")


# ===================== MATPLOTLIB things ===================== #


def add_figure(
    figure,
    close: Optional[bool] = True,
):
    """Render matplotlib figure into an image and add it to summary.
    Note that this requires the ``matplotlib`` package.

    Args:
        tag: Data identifier
        figure (matplotlib.pyplot.figure) or list of figures: Figure or a list of figures
        global_step: Global step value to record
        close: Flag to automatically close the figure
        walltime: Override default walltime (time.time()) of event
    """
    if isinstance(figure, list):
        add_image(image=figure_to_image(figure, close), dataformats="NCHW")
    else:
        add_image(image=figure_to_image(figure, close), dataformats="CHW")
