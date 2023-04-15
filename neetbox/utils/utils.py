# -*- coding: utf-8 -*-
#
# Author: GavinGong aka VisualDust
# URL:    https://gong.host
# Date:   20230319

import re
import platform
import json
import pip
import importlib
from typing import Union
from neetbox.utils.framing import get_caller_identity_traceback


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


class PipPackageHealper(metaclass=Singleton):
    def __init__(self) -> None:
        self.installed_packages = None

    def install(self, package, terminate=False):
        caller = get_caller_identity_traceback(3)
        caller_name = caller.module_name if caller.module else caller.filename
        retry = 4
        _installed = False
        while retry:
            if not retry:
                error_str = f"Bad Input"
                raise ValueError(error_str)
            choice = input(
                f"{caller_name} want to install {package} via pip. Allow? y/[n]:"
            )
            if choice in ["y", "yes"]:  # user choose to install
                print(f"installing {package} via pip...")
                pip.main(["install", package])
                _installed = True
                break
            if choice in ["n", "no"]:  # user choose not to install
                if terminate:  # the package must be installed
                    error_str = f"{caller_name} requires '{package}' but it is not going to be installed."
                    raise RuntimeError(error_str)
                else:
                    print(f"{package} is not going to be installed")
                    break
            else:  # illegal input
                retry -= 1
                if retry:
                    print(
                        f"illegal input: required 'y'/'n' but recieved '{choice}'. {retry} retries remaining."
                    )
        return _installed

    def is_installed(self, package: str, try_install_if_not: Union[str, bool] = True):
        caller = get_caller_identity_traceback(3)
        caller_name = caller.module_name if caller.module else caller.filename
        if not self.installed_packages:
            self.installed_packages = []
            package = str(package)
        if package in self.installed_packages:
            return True
        try:
            importlib.import_module(package)
            self.installed_packages.append(package)
            return True
        except:
            package_name_install = (
                package if type(try_install_if_not) is bool else try_install_if_not
            )
            print(
                f"{caller_name} requires '{package_name_install}' which is not installed."
            )
            if try_install_if_not:
                return self.install(package=package_name_install, terminate=True)
            return False


# singleton
PipPackageHealper = PipPackageHealper()
