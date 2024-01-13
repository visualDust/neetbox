import argparse
import json
import sys


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
    from ._server import server_process

    server_process(daemon_config)


if __name__ == "__main__":
    print("daemon server starting.\n name:\t", __name__, "\nargs:\t", sys.argv)
    run(sys.argv)
    print("daemon server exiting.")
