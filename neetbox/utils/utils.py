# -*- coding: utf-8 -*-
#
# Author: GavinGong aka VisualDust
# URL:    https://gong.host
# Date:   20230319

import re
import platform
import functools
import json


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

def singleton(class_):
    class class_w(class_):
        _instance = None

        def __new__(class_, *args, **kwargs):
            if class_w._instance is None:
                class_w._instance = super(class_w, class_).__new__(
                    class_, *args, **kwargs
                )


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


def patch(func):
    """Patch a function into a class type

    Args:
        func (Function): A funtion that takes at least one argument with a specific class type 'self:YourClass'

    Returns:
        funtion: patched function
    """
    cls = next(iter(func.__annotations__.values()))
    name = func.__defaults__[0]
    func.__qualname__ = f"{cls.__name__}.{func.__name__}"
    func.__module__ = cls.__module__
    if name is None:
        setattr(cls, func.__name__, func)
    else:
        func.__qualname__ = f"{cls.__name__}.{name}"
        setattr(cls, name, func)
    return func
