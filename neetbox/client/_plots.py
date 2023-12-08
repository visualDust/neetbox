from typing import Union
from neetbox._daemon._protocol import *
from neetbox._daemon.client._client import connection


def add_scalar(name: str, x: Union[int, float], y: Union[int, float]):
    """send an image to frontend display

    Args:
        image (Union[np.array, Image.Image]): image from cv2 and PIL.Image are supported
        name (str): name of the image, used in frontend display
    """
    # send
    connection.ws_send(event_type=EVENT_TYPE_NAME_SCALAR, payload={SERIES_KEY: name, "x": x, "y": y})
    
