from neetbox.utils.framing import get_caller_identity_traceback
from neetbox.integrations import engine
from neetbox.logging import get_logger
import importlib

logger = get_logger("NEETBOX")

class Environment:
    def __init__(self) -> None:
        self.installed_packages = None

    def is_installed(self, package: str, terminate: bool = False):
        caller = get_caller_identity_traceback(2)
        caller_name = caller.module_name if caller.module else caller.filename
        if not self.installed_packages:
            self.installed_packages = []
        logger.log(f"{caller_name} searching for '{package}'...")
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
                logger.err(error_str)
                raise ImportError(error_str)
            return False

# singleton
Environment = Environment()
