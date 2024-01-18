# -*- coding: utf-8 -*-
#
# Author: GavinGong aka VisualDust
# Github: github.com/visualDust
# Date:   20240109

from typing import Optional, Union

from fastapi import APIRouter, Body, File, Form, HTTPException, Response, UploadFile

from neetbox._protocol import *
from neetbox.logging import Logger, LogLevel

from ....db.project.condition import ProjectDbQueryCondition
from ..project._bridge import Bridge

logger = Logger("ServerStat APIs", skip_writers_names=["ws"])
logger.log_level = LogLevel.DEBUG

router = APIRouter()
