import io
from typing import Union

import cv2
import numpy as np
from PIL import Image

from neetbox.config import get_project_id, get_run_id
from neetbox.daemon._protocol import *
from neetbox.daemon.client._client import connection


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
