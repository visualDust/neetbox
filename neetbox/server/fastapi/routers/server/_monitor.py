# -*- coding: utf-8 -*-
#
# Author: GavinGong aka VisualDust
# Github: github.com/visualDust
# Date:   20240118

import time
from threading import Thread
from typing import Callable, List

import psutil
from vdtoys.localstorage import get_folder_size_in_bytes
from vdtoys.mvc import Singleton

from neetbox._protocol import *
from neetbox.config.user import get as get_global_config


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


class Hardware(metaclass=Singleton):
    def add_on_update_callback(self, func: Callable):
        self._on_update_call_backs.append(func)

    # properties
    _cpus: List[CpuStatus]
    _cpu_statistics: CpuStatistics
    _memory: MemoryStatus

    def __init__(self) -> None:
        self._cpus = [CpuStatus() for _ in range(psutil.cpu_count(logical=True))]
        self._cpu_statistics = CpuStatistics(*psutil.cpu_stats())
        virtual_memory = psutil.virtual_memory()
        self._memory = MemoryStatus(
            total=virtual_memory[0] / 1e6,
            available=virtual_memory[1] / 1e6,
            used=virtual_memory[3] / 1e6,
            free=virtual_memory[4] / 1e6,
        )

        def watch_thread():
            while True:
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
                self._cpu_statistics = CpuStatistics(*psutil.cpu_stats())
                time.sleep(1)

        Thread(target=watch_thread, daemon=True).start()

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
    def json(self):
        return {
            "cpus": [cpu.json for cpu in self._cpus],
            "cpustat": self._cpu_statistics.json,
            "ram": self._memory.json,
        }


hardware = Hardware()  # singleton


class Disks(metaclass=Singleton):
    def __init__(self) -> None:
        def watch_thread():
            while True:
                time.sleep(30)

        Thread(target=watch_thread, daemon=True).start()

    @property
    def json(self):
        """Docstring.

        Returns:
            TYPE: Description
        """
        try:
            neetbox_data_dir = get_global_config("vault")
            neetbox_storage_in_bytes = get_folder_size_in_bytes(neetbox_data_dir)
            drive = psutil.disk_usage(neetbox_data_dir)
            return {
                "total": drive.total / 1e6,
                "used": drive.used / 1e6,
                "neetbox": neetbox_storage_in_bytes / 1e6,
                "free": drive.free / 1e6,
            }
        except Exception as e:
            return {ERROR_KEY: f"failed to get disk usage cause {e}"}


disks = Disks()  # singleton
