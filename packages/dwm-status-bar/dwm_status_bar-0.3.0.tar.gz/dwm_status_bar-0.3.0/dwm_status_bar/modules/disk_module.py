import psutil

from dwm_status_bar.modules.base_module import BaseModule
from dwm_status_bar.util import format_number, trait
from dwm_status_bar.methods import __init__, __repr__


@trait(__init__, __repr__)
class DiskModule(BaseModule):
    """
    A class representing a disk module for system information retrieval.
    It generates the total disk space used for a particular partition.
    The value is available as string with the percentage number through
    the 'info' readonly property.

    It accepts the following optional parameters as keyword arguments:

    Options:
        path: str
            Sets the mountpoint path for a partition. [default: "/"]

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
    path: str = "/"
    width: int = 4
    precision: int = 1
    label: str
    delay: float = 1.0

    @property
    def info(self):
        return f"{self.label} {self._info()}" if self.label else self._info()

    def _info(self):
        disk_percent = psutil.disk_usage(self.path).percent
        return format_number(disk_percent, self.width, self.precision)
