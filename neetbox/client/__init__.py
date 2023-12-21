# -*- coding: utf-8 -*-
#
# Author: GavinGong aka VisualDust
# Github: github.com/visualDust
# Date:   20231206

from .api._action_agent import _NeetActionManager as NeetActionManager
from .api._client import connection
from .api._image import add_figure, add_image
from .api._plot import add_hyperparams, add_scalar
from .api._progress import Progress as progress
from .api._signal_and_slot import listen, watch

action = NeetActionManager.register
ws_subscribe = connection.ws_subscribe

__all__ = [
    "add_image",
    "add_scalar",
    "add_figure",
    "add_hyperparams",
    "ws_subscribe",
    "action",
    "NeetActionManager",
    "watch",
    "listen",
    "progress",
]
