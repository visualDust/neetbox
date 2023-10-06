# -*- coding: utf-8 -*-
#
# Author: GavinGong aka VisualDust
# URL:    https://gong.host
# Date:   20230319

import json
import platform
import re


def is_pure_ansi(text: str) -> bool:
    if not re.compile(r"^[A-Za-z0-9_-]+$").match(text):
        return False
    return True


def is_fs_case_sensitive():
    """Check if the file system is case sensitive

    Returns:
        bool: True if case sensitive
    """
    return "windows" not in platform.system().lower()


def legal_file_name_of(text: str) -> str:
    """Remove invalid characters for windows file systems

    Args:
        title (str): the given title

    Returns:
        str: valid text
    """
    if platform.system().lower() == "windows":
        rstr = r"[\/\\\:\*\?\"\<\>\|]"  # '/ \ : * ? " < > |'
        new_title = re.sub(rstr, "_", text)  # replace with '_'
        return new_title
    return text


def is_jsonable(x):
    try:
        x = json.dumps(x)
        return True
    except (TypeError, OverflowError):
        return False
