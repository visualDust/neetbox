from neetbox.utils.framing import get_caller_identity_traceback
import importlib
import getpass
import time
from threading import Thread
import asyncio
import platform
import GPUtil
import psutil
from neetbox.utils.utils import Singleton
from GPUtil import GPU as GPU


class Package(metaclass=Singleton):
    def __init__(self) -> None:
        self.installed_packages = None

    def is_installed(self, package: str, terminate: bool = False):
        caller = get_caller_identity_traceback(2)
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
            if terminate:
                error_str = (
                    f"{caller_name} requires '{package}' which is not installed."
                )
                raise ImportError(error_str)
            return False


# singleton
Package = Package()


class _CPU_STAT:
    def __init__(self, id=-1, percent=0.0, freq=0.0) -> None:
        self.id = id
        self.percent = percent
        self.freq = freq

    def __str__(self) -> str:
        return f"CPU{self.id}, {self.percent}%, {self.freq}Mhz"


class Environment(metaclass=Singleton):
    _update_interval = 1.0
    """
    The watcher may interacts with external libraries or devices
    a thread may be more suitable because it can provide a separate execution
    context with its own stack and memory space, which can simplify the design
    and debugging of the code.
    """
    _watcher: Thread = None
    _do_watch: bool = True
    _update_interval: float = 1.0
    gpus: list = []
    cpus: list = []
    platform_info: dict = {}

    def __init__(self) -> None:
        self.platform_info["username"] = getpass.getuser()
        self.platform_info["machine"] = platform.machine()
        self.platform_info["processor"] = (
            "unknown" if len(platform.processor()) == 0 else platform.processor()
        )
        self.platform_info["os name"] = platform.system()
        self.platform_info["os release"] = platform.version()
        self.platform_info["architecture"] = platform.architecture()
        self.platform_info["python version"] = platform.python_version()
        self.platform_info["python build"] = platform.python_build()

        self.cpus = [_CPU_STAT() for _ in range(psutil.cpu_count(logical=True))]
        self.gpus = GPUtil.getGPUs()
        self._with_gpu = False if len(self.gpus) == 0 else True

        # the environment shoube be imported in the __init__.py of the outer module. And the watcher thread should be auto started
        self.set_update_intervel()

    def set_update_intervel(self, intervel=1.0) -> None:
        if intervel < 1.0:
            self._do_watch = False
            return
        self._do_watch = True
        self._update_interval = intervel
        if not self._watcher or not self._watcher.is_alive():

            def watcher_fun(env_instance: Environment, do_update_gpus: bool):
                while env_instance._do_watch:
                    cpu_percent = psutil.cpu_percent(percpu=True)
                    cpu_freq = psutil.cpu_freq(percpu=True)
                    if len(cpu_freq) == 1:
                        cpu_freq = cpu_freq * len(cpu_percent)
                    for index in range(len(cpu_percent)):
                        env_instance.cpus[index] = _CPU_STAT(
                            id=index,
                            percent=cpu_percent[index],
                            freq=cpu_freq[index],
                        )
                    if do_update_gpus:
                        env_instance.gpus = GPUtil.getGPUs()
                    env_instance.cpu_stats = psutil.cpu_stats()
                    time.sleep(env_instance._update_interval)

            self._watcher = Thread(
                target=watcher_fun, args=(self, self._with_gpu), daemon=True
            )
            self._watcher.start()


# singleton
Environment = Environment()
