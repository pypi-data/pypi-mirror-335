import psutil

from dwm_status_bar.modules.base_module import BaseModule
from dwm_status_bar.util import format_number, trait
from dwm_status_bar.methods import __init__, __repr__


@trait(__init__, __repr__)
class CPUModule(BaseModule):
    """
    A class representing a CPU module for system information retrieval.
    It generates the current CPU usage in percent numbers as a string,
    available through the 'info' readonly property.

    It accepts the following optional parameters as keyword arguments:

    Options:
        interval: float
            Sets the interval time for comparing system CPU times.
            If interval is 0.0 or None, then the class returns the CPU
            times elapsed since the last call.
            If interval > 0.0, then the class's 'info' getter will block
            execution upon value retrieval.
            [default: None]

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
    interval: float
    width: int = 4
    precision: int = 1
    label: str
    delay: float = 1.0

    @property
    def info(self):
        return f"{self.label} {self._info()}" if self.label else self._info()

    def _info(self):
        cpu_percent = psutil.cpu_percent(interval=self.interval)
        return format_number(cpu_percent, self.width, self.precision)
