from enum import Enum
import importlib
from neetbox.core.framing import get_caller_identity_traceback

class Engine(Enum):
    Torch = "torch"


class _Environment:
    def __init__(self) -> None:
        self.supported_engines = None
        self.installed_engines = None
        self.installed_packages = []
        # todo migrate to python 3.9 after frameworks are supporting it
        
    def get_supported_engines(self):
        if not self.supported_engines:
            self.supported_engines = []
            for engine in Engine:
                self.supported_engines.append(engine)
        return self.supported_engines.copy()

    def get_installed_engines(self):
        if not self.installed_engines:
            logger.info("Scanning installed engines...")
            self.installed_engines = []
            for engine in self.get_supported_engines():
                try:
                    importlib.import_module(engine.value)
                    self.installed_engines.append(engine)
                except:
                    pass
        return self.installed_engines.copy()
    
    def installed(self, package, terminate: bool = False):
        if type(package) is Engine:  # asking if an engine installed
            package = package.value
            for installed in self.get_installed_engines():
                if package == installed.value:
                    return True
        elif type(package) is str:
            if package in  self.installed_packages:
                return True
            try:
                importlib.import_module(package)
                self.installed_packages.append(package)
                return True
            except:
                if terminate:
                    caller_name = get_caller_identity_traceback().filename
                    raise ImportError(f"{caller_name} requires \'{package}\' which is not installed.")
                return False
        return True

# singleton
_Environment = _Environment()
