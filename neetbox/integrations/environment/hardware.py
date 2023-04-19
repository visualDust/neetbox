# -*- coding: utf-8 -*-
#
# Author: GavinGong aka VisualDust
# URL:    https://gong.host
# Date:   20230413


from neetbox.utils import pkg
from neetbox.utils.framing import get_frame_module_traceback
module_name = get_frame_module_traceback().__name__
assert pkg.is_installed('psutil', try_install_if_not=True), f"{module_name} requires psutil which is not installed"
assert pkg.is_installed('GPUtil', try_install_if_not=True), f"{module_name} requires GPUtil which is not installed"
import GPUtil
import psutil
from GPUtil import GPU

import time
from threading import Thread
from neetbox.utils.mvc import Singleton
from neetbox.pipeline import watch


class _CPU_STAT(dict):
    def __init__(self, id=-1, percent=0.0, freq=0.0) -> None:
        self["id"] = id
        self["percent"] = percent
        self["freq"] = freq

    def __str__(self) -> str:
        return f"CPU{self['id']}, {(self['percent'])}%, {(self['freq'])}Mhz"


class _GPU_STAT(dict):
    def __init__(self, id=-1, name="GPU"):
        self["id"] = id
        self["name"] = name

    @classmethod
    def parse(cls, gpu: GPU):
        _instance = _GPU_STAT()
        _instance["id"] = gpu.id
        _instance["name"] = gpu.name
        _instance["memoryUtil"] = gpu.memoryUtil
        _instance["memoryTotal"] = gpu.memoryTotal
        _instance["memoryFree"] = gpu.memoryFree
        _instance["memoryUsed"] = gpu.memoryUsed
        _instance["temperature"] = gpu.temperature
        _instance["driver"] = gpu.driver
        return _instance

class _Hardware(dict, metaclass=Singleton):
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

    def __init__(self) -> None:
        # device
        self["cpus"] = [_CPU_STAT() for _ in range(psutil.cpu_count(logical=True))]
        self["gpus"] = [_GPU_STAT.parse(_gpu) for _gpu in GPUtil.getGPUs()]
        self._with_gpu = False if len(self["gpus"]) == 0 else True

        # the environment shoube be imported in the __init__.py of the outer module. And the watcher thread should be auto started
        self.set_update_intervel()

    def set_update_intervel(self, intervel=1.0) -> None:
        if intervel < 1.0:
            self._do_watch = False
            return
        self._do_watch = True
        self._update_interval = intervel
        if not self._watcher or not self._watcher.is_alive():

            def watcher_fun(env_instance: _Hardware, do_update_gpus: bool):
                while env_instance._do_watch:
                    cpu_percent = psutil.cpu_percent(percpu=True)
                    cpu_freq = psutil.cpu_freq(percpu=True)
                    if len(cpu_freq) == 1:
                        cpu_freq = cpu_freq * len(cpu_percent)
                    for index in range(len(cpu_percent)):
                        env_instance["cpus"][index] = _CPU_STAT(
                            id=index,
                            percent=cpu_percent[index],
                            freq=cpu_freq[index],
                        )
                    if do_update_gpus:
                        env_instance["gpus"] = [
                            _GPU_STAT.parse(_gpu) for _gpu in GPUtil.getGPUs()
                        ]
                    env_instance[""] = psutil.cpu_stats()
                    time.sleep(env_instance._update_interval)

            self._watcher = Thread(
                target=watcher_fun, args=(self, self._with_gpu), daemon=True
            )
            self._watcher.start()

# singleton
hardware = _Hardware()

# watch updates in daemon
@watch(name="hardware")
def update_env_stat():
    return dict(hardware)
