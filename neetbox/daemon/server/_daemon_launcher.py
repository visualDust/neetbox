import argparse
import json
import sys

from neetbox.daemon.server._flask_server import daemon_process

# sys.stdout=open(r'D:\Projects\ML\neetbox\logdir\daemon.log', 'a+')


# from neetbox.daemon._local_http_client import _local_http_client
print("========= Daemon  =========")


def run():
    if len(sys.argv) <= 1:
        print("_daemon_: Warning: empty daemon_config")
        daemon_config = {}
    else:
        ap = argparse.ArgumentParser()
        ap.add_argument("--config")
        args = ap.parse_args()
        daemon_config = json.loads(args.config)
        print("Daemon  started with config:", daemon_config)
    daemon_process(daemon_config)


print("_daemon_ is starting with __name__ =", __name__, " and args =", sys.argv)
run()
print("_daemon_: exiting")
