# -*- coding: utf-8 -*-
#
# Author: GavinGong aka VisualDust
# Github: github.com/visualDust
# Date:   20231211

from neetbox._protocol import *
from neetbox.utils.x2numpy import *
from neetbox.config import get_module_level_config, get_project_id, get_run_id


from .._client import connection

# ===================== HYPERPARAM things ===================== #


def add_hyperparams(hparam: dict, name: str = None):
    """add/set hyperparams to current run, the added hyperparams will show in frontend

    Args:
        hparam (dict): hyperparams
        name (str, optional): name of hyperparams. Defaults to None.
    """
    assert isinstance(hparam, dict)
    hparam = {name: hparam} if name else hparam
    connection.ws_send(event_type=EVENT_TYPE_NAME_HPARAMS, series=name, payload=hparam)


# ===================== metadata things ===================== #

def set_run_name(name: str):
    """set the name of current run

    Args:
        name (str): name of current run
    """
    projectId = get_project_id()
    runId = get_run_id()
    connection.put_check_online(api=f"{API_ROOT}/{PROJECT_KEY}/{projectId}/run/{runId}", json={"name": name})