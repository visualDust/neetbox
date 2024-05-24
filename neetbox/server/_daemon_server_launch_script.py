import argparse
import json
import sys
import subprocess
import time
from typing import Optional


def run(config):
    from .server_process import server_process

    server_process(config)


def start(config) -> Optional[int]:
    """start a server as background daemon

    Args:
        config (dict): server launch config

    Returns:
        DaemonableProcess: the daemon process
    """
    from neetbox.utils import DaemonableProcess
    import neetbox.server._daemon_server_launch_script as myself

    popen = DaemonableProcess(  # server daemon
        target=myself,
        args=["--config", json.dumps(config)],
        mode=config["mode"],
        redirect_stdout=subprocess.DEVNULL if config["mute"] else None,
        env_append={"NEETBOX_DAEMON_PROCESS": "1"},
    ).start()
    time.sleep(1)
    return popen


if __name__ == "__main__":
    print("server starting.\n name:\t", __name__, "\nargs:\t", sys.argv)
    if len(sys.argv) <= 1:
        print("Warning: empty server config")
        config = None
    else:
        ap = argparse.ArgumentParser()
        ap.add_argument("--config")
        args = ap.parse_args()
        print(type(args.config))
        print(args.config)
        config = json.loads(args.config)
        print("Daemon started with config:", config)
    run(config)
    print("server closed.")
