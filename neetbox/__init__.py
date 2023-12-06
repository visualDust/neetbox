import os
import sys

from neetbox.client import action, add_image
from neetbox.config._workspace import _is_in_workspace, _load_workspace_as_a_project

is_in_daemon_process = (
    "NEETBOX_DAEMON_PROCESS" in os.environ and os.environ["NEETBOX_DAEMON_PROCESS"] == "1"
)

if len(sys.argv) > 0 and sys.argv[0].endswith("neet") or is_in_daemon_process:
    # running in cli or daemon process, do not load workspace
    pass
elif _is_in_workspace():  # if a config file exist and not running in cli
    _load_workspace_as_a_project(connect_daemon=True)

__all__ = ["add_image", "action", "logger"]
