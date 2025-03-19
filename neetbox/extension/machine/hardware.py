# -*- coding: utf-8 -*-
#
# Author: GavinGong aka VisualDust
# Github: github.com/visualDust
# Date:   20230413

import functools
import time
from threading import Thread
from typing import Callable, List

import GPUtil
import psutil
from GPUtil import GPU
from GPUtil import getAvailable as _getAvailableNvGPU
from vdtoys.mvc import Singleton

from neetbox.config import export_default_config, get_module_level_config
from neetbox.extension import on_workspace_loaded


class CpuStatus:
    def __init__(self, id=-1, percentage=0.0, frequency=0.0):
        self.id = id
        self.percentage = percentage
        self.frequency = frequency

    def __str__(self) -> str:
        return f"CPU({self.id}), {(self.percentage)}%, {(self.frequency)}Mhz"

    @property
    def json(self):
        return {"id": self.id, "percentage": self.percentage, "frequency": self.frequency}


class CpuStatistics:
    def __init__(self, ctx_switches, interrupts, soft_interrupts, syscalls) -> None:
        self.ctx_switches = ctx_switches
        self.interrupts = interrupts
        self.soft_interrupts = soft_interrupts
        self.syscalls = syscalls

    @property
    def json(self):
        return {
            "ctxSwitches": self.ctx_switches,
            "interrupts": self.interrupts,
            "softInterrupts": self.soft_interrupts,
            "syscalls": self.syscalls,
        }

    def __str__(self) -> str:
        result = ""
        for k, v in self.json.items():
            result += f"{k}:\t{v}"
        return result


class MemoryStatus:
    def __init__(self, total, available, used, free) -> None:
        self.total = total
        self.available = available
        self.used = used
        self.free = free

    @property
    def json(self):
        return {
            "total": self.total,
            "available": self.available,
            "used": self.used,
            "free": self.free,
        }

    def __str__(self) -> str:
        result = ""
        for k, v in self.json.items():
            result += f"{k}:\t{v}"
        return result


class NvGpuStatus(GPU):
    @classmethod
    def parse(cls, other: GPU):
        return NvGpuStatus(
            ID=other.id,
            uuid=other.uuid,
            load=other.load,
            memoryTotal=other.memoryTotal,
            memoryUsed=other.memoryUsed,
            memoryFree=other.memoryFree,
            driver=other.driver,
            gpu_name=other.name,
            serial=other.serial,
            display_mode=other.display_mode,
            display_active=other.display_active,
            temp_gpu=other.temperature,
        )

    @property
    def json(self):
        return {
            "id": self.id,
            "name": self.name,
            "load": self.load,
            "memoryUtil": self.memoryUtil,
            "memoryTotal": self.memoryTotal,
            "memoryFree": self.memoryFree,
            "memoryUsed": self.memoryUsed,
            "temperature": self.temperature,
            "driver": self.driver,
        }

    def __str__(self) -> str:
        return super().__str__()


class Hardware(metaclass=Singleton):
    watch_thread: Thread = None
    _do_watch: bool = True
    _update_interval: float = 1.0

    # properties
    _cpus: List[CpuStatus]
    _gpus: List[NvGpuStatus]
    _cpu_statistics: CpuStatistics
    _memory: MemoryStatus

    def __init__(self) -> None:
        self._cpus = [CpuStatus() for _ in range(psutil.cpu_count(logical=True))]
        self._cpu_statistics = CpuStatistics(*psutil.cpu_stats())
        try:
            self._gpus = [NvGpuStatus.parse(gpu) for gpu in GPUtil.getGPUs()]
        except Exception as e:
            self._gpus = []
        self._with_gpu = False if len(self._gpus) == 0 else True
        virtual_memory = psutil.virtual_memory()
        self._memory = MemoryStatus(
            total=virtual_memory[0] / 1e6,
            available=virtual_memory[1] / 1e6,
            used=virtual_memory[3] / 1e6,
            free=virtual_memory[4] / 1e6,
        )

    @property
    def cpus(self):
        return self._cpus

    @property
    def cpu_statistics(self):
        return self._cpu_statistics

    @property
    def memory(self):
        return self._memory

    @property
    def gpus(self):
        return self._gpus

    @property
    def with_gpu(self):
        return self._with_gpu

    @property
    def json(self):
        return {
            "cpus": [cpu.json for cpu in self._cpus],
            "cpustat": self._cpu_statistics.json,
            "ram": self._memory.json,
            "gpus": [gpu.json for gpu in self._gpus],
        }

    _on_update_call_backs = []

    def add_on_update_call_back(self, func: Callable):
        self._on_update_call_backs.append(func)

    def set_start_update_intervel(self, intervel=1.0) -> None:
        if intervel < 0:
            self._do_watch = False
            return
        self._do_watch = True
        self._update_interval = intervel
        if not self.watch_thread or not self.watch_thread.is_alive():

            def watch_hardware(do_update_gpus: bool):
                while self._do_watch:
                    # update cpu usage
                    cpu_percent = psutil.cpu_percent(percpu=True)
                    cpu_freq = psutil.cpu_freq(percpu=True)
                    if len(cpu_freq) == 1:
                        cpu_freq = cpu_freq * len(cpu_percent)
                    for index in range(len(cpu_percent)):
                        self._cpus[index] = CpuStatus(
                            id=index,
                            percentage=cpu_percent[index],
                            frequency=cpu_freq[index],
                        )
                    # update memory usage
                    virtual_memory = psutil.virtual_memory()
                    self._memory = MemoryStatus(
                        total=virtual_memory[0] / 1e6,
                        available=virtual_memory[1] / 1e6,
                        used=virtual_memory[3] / 1e6,
                        free=virtual_memory[4] / 1e6,
                    )
                    # update gpu usage
                    if do_update_gpus:
                        try:
                            self._gpus = [NvGpuStatus.parse(gpu) for gpu in GPUtil.getGPUs()]
                        except Exception as e:
                            self._gpus = []
                    self._cpu_statistics = CpuStatistics(*psutil.cpu_stats())
                    for callback in self._on_update_call_backs:
                        callback(self.json)
                    time.sleep(self._update_interval)

            self.watch_thread = Thread(target=watch_hardware, args=(self._with_gpu,), daemon=True)
            self.watch_thread.start()


Hardware.get_available_NvGPU = _getAvailableNvGPU

# singleton
hardware = Hardware()


@export_default_config
def return_default_config() -> dict:
    return {"interval": 2}


# watch updates in daemon
@on_workspace_loaded(name="hardware-monit")
def load_monit_hardware():
    cfg = get_module_level_config()
    if cfg["interval"] > 0:  # if do monit hardware
        from neetbox._protocol import EVENT_TYPE_NAME_HARDWARE
        from neetbox.client import connection

        def ws_send_on_update(stat_json):
            connection.ws_send(
                event_type=EVENT_TYPE_NAME_HARDWARE,
                payload=stat_json,
                _history_len=1000,
            )

        hardware.add_on_update_call_back(ws_send_on_update)
        hardware.set_start_update_intervel(cfg["interval"])
