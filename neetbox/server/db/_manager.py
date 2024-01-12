# -*- coding: utf-8 -*-
#
# Author: GavinGong aka VisualDust
# Github: github.com/visualDust
# Date:   20231201

import atexit
from collections import defaultdict

from neetbox.logging import Logger
from neetbox.utils.framing import get_caller_identity_traceback
from neetbox.utils.mvc import Singleton

logger = Logger("DB Manager", skip_writers_names=["ws"])


class DBCPool(metaclass=Singleton):
    _POOL = defaultdict(dict)

    @property
    def current(self):
        identity = get_caller_identity_traceback()
        return self._POOL[identity.module_name]


manager = DBCPool()


def clear_dbc_on_exit():
    logger.info("process exiting, cleaning up...")
    for module_name, conn_dict in manager._POOL.items():
        logger.info(f"closing db connection for module {module_name}:")
        for _, dbc in conn_dict.items():
            logger.info(f"=> closing {dbc}")
            try:
                dbc.connection.close()
            except Exception as e:
                logger.err(RuntimeError(f"failed to close db connection {dbc}, {e}"))


atexit.register(clear_dbc_on_exit)
