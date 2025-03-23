import collections

import psutil

from dwm_status_bar.modules.base_module import BaseModule
from dwm_status_bar.util import format_number, trait
from dwm_status_bar.methods import __init__, __repr__, __new__


@trait(__init__, __repr__)
class LinuxRAMModule(BaseModule):
    width: int = 4
    precision: int = 1
    label: str
    delay: float = 1.0

    @property
    def info(self):
        return f"{self.label} {self._info()}" if self.label else self._info()

    def _info(self):
        memory = self._read_meminfo()

        mem_total = memory["MemTotal"]
        mem_free = memory["MemFree"]
        buffers = memory["Buffers"]
        cached = memory["Cached"]
        mem_used = mem_total - mem_free - buffers - cached

        mem_percent = mem_used / mem_total * 100

        return format_number(mem_percent, self.width, self.precision)

    def _read_meminfo(self):
        """Return memory usage information as a dictionary."""
        result = {}
        with open("/proc/meminfo", "r") as meminfo:
            for line in meminfo.readlines():
                label, value, *unit = line.strip().split()
                label = label.removesuffix(":")
                value = int(value)
                try:
                    if unit[0] == "kB":
                        value *= 1024
                except IndexError:
                    pass

                result[label] = value

        return result


@trait(__init__, __repr__)
class NetBSDRAMModule(BaseModule):
    width: int = 4
    precision: int = 1
    label: str
    delay: float = 1.0

    @property
    def info(self):
        return f"{self.label} {self._info()}" if self.label else self._info()

    def _info(self):
        memory = self._read_meminfo()

        mem_total = memory["MemTotal"]
        mem_free = memory["MemFree"]
        mem_used = mem_total - mem_free

        mem_percent = mem_used / mem_total * 100

        return format_number(mem_percent, self.width, self.precision)

    def _read_meminfo(self):
        """Return memory usage information as a dictionary."""
        result = {}
        with open("/proc/meminfo", "r") as meminfo:
            counter = 0
            while counter < 3:
                meminfo.readline()
                counter += 1

            for line in meminfo.readlines():
                label, value, unit = line.strip().split()
                label = label.removesuffix(":")
                value = int(value)
                if unit == "kB":
                    value *= 1024

                result[label] = value

        return result


@trait(__init__, __repr__)
class DefaultRAMModule(BaseModule):
    width: int = 4
    precision: int = 1
    label: str
    delay: float = 1.0

    @property
    def info(self):
        return f"{self.label} {self._info()}" if self.label else self._info()

    def _info(self):
        mem_percent = psutil.virtual_memory().percent
        return format_number(mem_percent, self.width, self.precision)


@trait(__new__)
class RAMModule:
    """
    A class representing a RAM module for system information retrieval.
    It generates the current RAM usage in percent numbers as a string,
    available through the 'info' readonly property.

    It accepts the following optional parameters as keyword arguments:

    Options:
        width: int
            Sets the total size of the resulting string. [default: 4]

        precision: int
            Sets the desired number of decimals in the resulting number.
            If the number gets too large, the precision is reduced in
            order to fit within the assigned 'width' parameter.
            [default: 1]

        label: str
            A label to identify the information on each module.
            [default: None]

        delay: float
            Sets the time it takes to update the module's information,
            in seconds. [default: 1.0]
    """
    modules = collections.defaultdict(
        lambda: DefaultRAMModule,
        {
            "Linux": LinuxRAMModule,
            "NetBSD": NetBSDRAMModule,
        }
    )
