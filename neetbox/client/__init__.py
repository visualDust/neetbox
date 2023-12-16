# -*- coding: utf-8 -*-
#
# Author: GavinGong aka VisualDust
# Github: github.com/visualDust
# Date:   20231206

from ._action_agent import _NeetActionManager as NeetActionManager
from ._client import connection
from ._image import add_figure, add_image
from ._plot import add_hyperparams, add_scalar
from ._progress import Progress as progress
from ._signal_and_slot import listen, watch

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
