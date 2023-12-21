# -*- coding: utf-8 -*-
#
# Author: GavinGong aka VisualDust
# Github: github.com/visualDust
# Date:   20231206

from ._client import connection
from ._signal_and_slot import listen, watch
from .apis._action import actionManager
from .apis._image import add_figure, add_image
from .apis._progress import Progress as progress
from .apis._scalar import add_hyperparams, add_scalar

ws_subscribe = connection.ws_subscribe
action = actionManager.register

__all__ = [
    "add_image",
    "add_scalar",
    "add_figure",
    "add_hyperparams",
    "ws_subscribe",
    "action",
    "watch",
    "listen",
    "progress",
]
