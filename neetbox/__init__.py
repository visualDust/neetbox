import os
import sys


def _load_workspace(connect_daemon=True):
    from neetbox.config import get_module_level_config

    get_module_level_config()  # run things after init workspace
    if connect_daemon:
        import neetbox._daemon as _daemon

        _daemon.connect()


is_in_daemon_process = (
    "NEETBOX_DAEMON_PROCESS" in os.environ and os.environ["NEETBOX_DAEMON_PROCESS"] == "1"
)

if len(sys.argv) > 0 and sys.argv[0].endswith("neet") or is_in_daemon_process:
    # running in cli or daemon process, do not load workspace
    pass
else:
    _load_workspace(connect_daemon=True)

from neetbox.client import action, add_image, add_scalar, listen, watch
from neetbox.logging import logger

__all__ = ["add_image", "add_scalar", "action", "logger", "watch", "listen"]
