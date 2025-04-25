# -*- coding: utf-8 -*-
#
# Author: GavinGong aka VisualDust
# Github: github.com/visualDust
# Date:   20231206

from ._client import connection
from ._signal_and_slot import listen, watch
from .apis import (
    actionManager,
    add_figure,
    add_image,
    add_hyperparams,
    add_scalar,
    set_run_name,
    progress,
)

ws_subscribe = connection.ws_subscribe
action = actionManager.register

__all__ = [
    "add_image",
    "add_scalar",
    "add_figure",
    "add_hyperparams",
    "set_run_name",
    "ws_subscribe",
    "action",
    "watch",
    "listen",
    "progress",
]
