import os
import sys
from enum import Enum

class AnsiColor(Enum):
    BLACK = "BLACK"
    RED = "RED"
    GREEN = "GREEN"
    YELLOW = "YELLOW"
    BLUE = "BLUE"
    MAGENTA = "MAGENTA"
    CYAN = "CYAN"
    WHITE = "WHITE"
    RESET = "RESET"
    # These are fairly well supported, but not part of the standard.
    LIGHT_BLACK = "LIGHTBLACK_EX"
    LIGHT_RED = "LIGHTRED_EX"
    LIGHT_GREEN = "LIGHTGREEN_EX"
    LIGHT_YELLOW = "LIGHTYELLOW_EX"
    LIGHT_BLUE = "LIGHTBLUE_EX"
    LIGHT_MAGENTA = "LIGHTMAGENTA_EX"
    LIGHT_CYAN = "LIGHTCYAN_EX"
    LIGHT_WHITE = "LIGHTWHITE_EX"


class AnsiStyle(Enum):
    BRIGHT = "BRIGHT"
    DIM = "DIM"
    NORMAL = "NORMAL"
    RESET_ALL = "RESET_ALL"

def should_colorize(stream):
    if stream is None:
        return False

    if stream is sys.stdout or stream is sys.stderr:
        try:
            import ipykernel
            import IPython

            ipython = IPython.get_ipython()
            is_jupyter_stream = isinstance(stream, ipykernel.iostream.OutStream)
            is_jupyter_shell = isinstance(ipython, ipykernel.zmqshell.ZMQInteractiveShell)
        except Exception:
            pass
        else:
            if is_jupyter_stream and is_jupyter_shell:
                return True

    if stream is sys.__stdout__ or stream is sys.__stderr__:
        if "CI" in os.environ and any(
            ci in os.environ
            for ci in ["TRAVIS", "CIRCLECI", "APPVEYOR", "GITLAB_CI", "GITHUB_ACTIONS"]
        ):
            return True
        if "PYCHARM_HOSTED" in os.environ:
            return True
        if os.name == "nt" and "TERM" in os.environ:
            return True

    try:
        return stream.isatty()
    except Exception:
        return False


def should_wrap(stream):
    if os.name != "nt":
        return False

    if stream is not sys.__stdout__ and stream is not sys.__stderr__:
        return False

    from colorama.win32 import winapi_test

    return winapi_test()


def wrap(stream):
    from colorama import AnsiToWin32

    return AnsiToWin32(stream, convert=True, strip=False, autoreset=False).stream
