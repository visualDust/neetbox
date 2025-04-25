# -*- coding: utf-8 -*-
#
# Author: GavinGong aka VisualDust
# Github: github.com/visualDust
# Date:   20231201

import atexit
from collections import defaultdict
from multiprocessing import managers
from typing import Dict

from vdtoys.framing import get_caller_info_traceback
from vdtoys.mvc import Singleton

from neetbox.logging import Logger

from .abc import ManageableDB

ModuleNameType = str
DbIdType = str


class DBConnectionManager(metaclass=Singleton):
    _POOL: Dict[ModuleNameType, Dict[DbIdType, ManageableDB]] = defaultdict(
        dict
    )

    @property
    def current(self):
        identity = get_caller_info_traceback(stack_offset=2)
        return self._POOL[identity.module_name]

    def __init__(self):
        self.logger = Logger("DB Conn Manager", skip_writers_names=["ws"])

        def clear_dbc_on_exit():
            for module_name, conn_dict in self._POOL.items():
                self.logger.info(
                    f"Closing db connection for module {module_name}:"
                )
                dbc: ManageableDB
                for _, dbc in conn_dict.items():
                    self.logger.info(f"=> Closing {dbc}")
                    try:
                        dbc.close()
                    except Exception as e:
                        self.logger.err(
                            RuntimeError(
                                f"Failed to close db connection {dbc}, {e}"
                            )
                        )

        atexit.register(clear_dbc_on_exit)
        
manager = DBConnectionManager()