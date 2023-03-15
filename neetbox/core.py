# -*- coding: utf-8 -*-
#
# Author: GavinGong aka VisualDust
# URL:    https://gong.host
# Date:   20230315

from neetbox.logging import get_logger

_static_logger = get_logger(whom="NEETBOX")
def get_static_logger():
    return _static_logger

