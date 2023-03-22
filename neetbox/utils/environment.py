from neetbox.utils.framing import get_caller_identity_traceback
from neetbox.integrations import engine
import importlib
import getpass
import platform
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



class Environment(dict):
    gpus:list
    def __new__(cls) -> "Environment":
        # todo return the old one
        pass
    def __init__(self) -> None:
        self.gpus = GPUtil.getGPUs()
        # todo add inits
        pass

Environment = Environment()

# def os_info(self):
#     """Log some maybe-useful os info
#     Returns:
#         _Logger : the logger instance itself
#     """
#     message = (
#         f"whom\t\t|\t" + getpass.getuser() + " using " + str(platform.node()) + "\n"
#     )
#     message += (
#         "machine\t\t|\t"
#         + str(platform.machine())
#         + " on "
#         + str(platform.processor())
#         + "\n"
#     )
#     message += (
#         "system\t\t|\t" + str(platform.system()) +
#         str(platform.version()) + "\n"
#     )
#     message += (
#         "python\t\t|\t"
#         + str(platform.python_build())
#         + ", ver "
#         + platform.python_version()
#         + "\n"
#     )
#     self.log(message, with_datetime=False, with_identifier=False)
#     return self