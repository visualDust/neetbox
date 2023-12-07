import io
from typing import Union

import cv2
import numpy as np
from PIL import Image
from neetbox._daemon._protocol import *
from neetbox._daemon.client._client import connection
from neetbox.config import get_project_id, get_run_id
from neetbox.logging import logger


def make_np(x):
    def check_nan(array):
        tmp = np.sum(array)
        if np.isnan(tmp) or np.isinf(tmp):
            logger.warning("NaN or Inf found in input tensor.")
        return array

    if isinstance(x, list):
        return check_nan(np.array(x))
    if isinstance(x, np.ndarray):
        return check_nan(x)
    if np.isscalar(x):
        return check_nan(np.array([x]))
    if "torch" in str(type(x)):

        def prepare_pytorch(x):
            import torch

            if isinstance(x, torch.autograd.Variable):
                x = x.data
            x = x.cpu().numpy()
            return x

        return check_nan(prepare_pytorch(x))


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


def add_image(name: str, image: Union[np.array, Image.Image]):
    """send an image to frontend display

    Args:
        image (Union[np.array, Image.Image]): image from cv2 and PIL.Image are supported
        name (str): name of the image, used in frontend display
    """

    if isinstance(image, np.ndarray):  # convert ndarray to bytes
        _, im_buf_arr = cv2.imencode(".png", image)
        image_bytes = im_buf_arr.tobytes()
    elif isinstance(image, Image.Image):
        with io.BytesIO() as image_bytes_stream:
            # convert PIL Image to bytes
            image.save(image_bytes_stream, format="PNG")
            image_bytes = image_bytes_stream.getvalue()
    # send bytes
    project_id = get_project_id()
    connection.post(
        api=f"/image/{project_id}",
        data={PROJECT_ID_KEY: project_id, "series": name, "run-id": get_run_id()},
        files={"image": image_bytes},
    )


def add_tensor(name: str, tensor, dataformats="CHW"):
    tensor = make_np(tensor)
    tensor = convert_to_HWC(tensor, dataformats)
    if tensor.dtype != np.uint8:
        tensor = (tensor * 255.0).astype(np.uint8)
    add_image(name=name, image=tensor)
