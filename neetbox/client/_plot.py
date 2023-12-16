# -*- coding: utf-8 -*-
#
# Author: GavinGong aka VisualDust
# Github: github.com/visualDust
# Date:   20231211

from neetbox._protocol import *
from neetbox.utils.x2numpy import *

from ._client import connection

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


def add_hyperparams(hparam: dict, name: str = None):
    assert isinstance(hparam, dict)
    hparam = {name: hparam} if name else hparam
    connection.ws_send(event_type=EVENT_TYPE_NAME_HPARAMS, series=name, payload=hparam)
