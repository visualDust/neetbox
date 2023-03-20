from neetbox.utils.framing import get_caller_identity_traceback
from neetbox.integrations import engine
import importlib
import GPUtil
from GPUtil import GPU as GPU


class Package:
    def __init__(self) -> None:
        self.installed_packages = None

    def is_installed(self, package: str, terminate: bool = False):
        caller = get_caller_identity_traceback(2)
        caller_name = caller.module_name if caller.module else caller.filename
        if not self.installed_packages:
            self.installed_packages = []
        if type(package) is engine:
            package = package.value
        if package in self.installed_packages:
            return True
        try:
            importlib.import_module(package)
            self.installed_packages.append(package)
            return True
        except:
            if terminate:
                error_str = f"{caller_name} requires '{package}' which is not installed."
                raise ImportError(error_str)
            return False

# singleton
Package = Package()

class HostDevice:
    gpus:list
    def __new__(cls) -> "HostDevice":
        # todo return the old one
        pass
    def __init__(self) -> None:
        self.gpus = GPUtil.getGPUs()
        # todo add inits
        pass

HostDevice = HostDevice()