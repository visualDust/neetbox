import argparse
import json
import sys

from neetbox.server._server import server_process

print("========= Server Daemon  =========")


def run(argv):
    if len(argv) <= 1:
        print("_daemon_: Warning: empty daemon_config")
        daemon_config = None
    else:
        ap = argparse.ArgumentParser()
        ap.add_argument("--config")
        args = ap.parse_args()
        print(type(args.config))
        print(args.config)
        daemon_config = json.loads(args.config)
        print("Daemon started with config:", daemon_config)
    server_process(daemon_config)


if __name__ == "__main__":
    print("_daemon_ is starting with __name__ =", __name__, " and args =", sys.argv)
    run(sys.argv)
    print("_daemon_: exiting")
