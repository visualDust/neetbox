import io
from typing import Union

import cv2
import numpy as np
from PIL import Image

from neetbox import PROJECT_ID
from neetbox.config._config import get_run_id
from neetbox.daemon._protocol import *
from neetbox.daemon.client._client import connection


def impost(image: Union[np.array, Image.Image], name: str):
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
    connection.post(
        api=f"/image/{PROJECT_ID}",
        data={PROJECT_ID_KEY: PROJECT_ID, "series": name, "run-id": get_run_id()},
        files={"image": image_bytes},
    )
