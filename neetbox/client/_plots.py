import io
from typing import Union

from neetbox._daemon._protocol import *
from neetbox._daemon.client._client import connection
from neetbox.config import get_project_id, get_run_id


def add_scatter(name: str, x: Union[int, float], y: Union[int, float]):
    """send an image to frontend display

    Args:
        image (Union[np.array, Image.Image]): image from cv2 and PIL.Image are supported
        name (str): name of the image, used in frontend display
    """
    # send bytes
    connection.ws_send(event_type="scatter", payload={"series": name, "x": x, "y": y})
