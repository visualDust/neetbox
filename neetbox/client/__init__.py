# -*- coding: utf-8 -*-
#
# Author: GavinGong aka VisualDust
# URL:    https://gong.host
# Date:   20231206

from ._client_action_agent import _NeetActionManager as NeetActionManager
from ._signal_and_slot import listen, watch
from ._writers._image import add_figure, add_image
from ._writers._plot import add_hyperparams, add_scalar

action = NeetActionManager.register

__all__ = [
    "add_image",
    "add_scalar",
    "add_figure",
    "add_hyperparams",
    "action",
    "NeetActionManager",
    "watch",
    "listen",
]
