import warnings
import os
from colorama import Fore, Back
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


def colored(text, color_foreground: AnsiColor, color_background: AnsiColor = None):
    """_summary_

    Args:
        text (str): original raw string
        color (AnsiColor): which color

    Raises: Nothing

    Returns:
        str: colored string
    """
    if "ANSI_COLORS_DISABLED" in os.environ or "NO_COLOR" in os.environ:
        warnings.warn(
            "Notice that current running environment does not supported colored text. NEETBOX logging facilities will still work but may not output colored text in console."
        )

    # Resolving foreground color
    if type(color_foreground) is AnsiColor:
        color_foreground = color_foreground.value
    if hasattr(Fore, color_foreground.upper()):
        text = getattr(Fore, color_foreground.upper()) + text + Fore.RESET
    else:
        raise ValueError("Wrong color was inputed in colored func.")
    
    # Resolving background color
    if color_background:
        if type(color_foreground) is AnsiColor:
            color_background = color_background.value
        color_background = color_background.value
        if hasattr(Fore, color_foreground.upper()):
            text = getattr(Back, color_foreground.upper()) + text + Fore.RESET
        else:
            raise ValueError("Wrong color was inputed in colored func.")
    return text
