import importlib
from typing import Union

import pip

from neetbox.utils.framing import get_caller_identity_traceback
from neetbox.utils.mvc import Singleton


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
                error_str = "Bad Input"
                raise ValueError(error_str)
            print(f"{caller_name} want to install {package} via pip.")
            choice = input("Make your choice: [y]/n")
            choice = choice or "y"
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
        except:  # noqa
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
pipPackageHealper = PipPackageHealper()
