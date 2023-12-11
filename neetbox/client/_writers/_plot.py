# -*- coding: utf-8 -*-
#
# Author: GavinGong aka VisualDust
# URL:    https://gong.host
# Date:   20231211

from typing import Optional

import numpy as np

from neetbox._daemon._protocol import *
from neetbox._daemon.client._client import connection
from neetbox.utils.x2numpy import *

# ===================== PLOTTING things ===================== #


# @dataclass
# class PlotType(str, Enum):
#     LineChart = "linechart"
#     AreaChart = "areachart"
#     Histogram = 'histogram'

# @dataclass
# class PlottingPayload:
#     pass


def add_scalar(name: str, x: Union[int, float], y: Union[int, float]):
    """send a scalar to frontend display

    Args:
        name (str): name of the image, used in frontend display
        x (Union[int, float]): x
        y (Union[int, float]): y
    """
    # send
    connection.ws_send(event_type=EVENT_TYPE_NAME_SCALAR, series=name, payload={"x": x, "y": y})


# ===================== HYPERPARAM things ===================== #


def add_hyperparams(name: str, value: dict):
    connection.ws_send(event_type=EVENT_TYPE_NAME_HPARAMS, payload={name: value})
