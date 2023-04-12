from neetbox.config._default import DEFAULT_CONFIG as default
from neetbox.config._config import _update as update

update(default)
from neetbox.config._config import _get
from neetbox.utils.framing import *


def get_module_config():
    module_name = get_frame_module_traceback(traceback=2).__name__
    the_config = _get()
    for sub_module_name in module_name.split(".")[1:]:  # skip 'neetbox'
        if sub_module_name not in the_config:
            return the_config
        the_config = the_config[sub_module_name]
    return the_config


__all__ = ["config", "get_module_config", "default"]
