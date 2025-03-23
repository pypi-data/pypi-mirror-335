import time

import psutil

from dwm_status_bar.modules.base_module import BaseModule
from dwm_status_bar.util import format_number, trait
from dwm_status_bar.methods import __init__, __repr__


@trait(__init__, __repr__)
class DateTimeModule(BaseModule):
    """
    A class representing a date and time module for system information.
    It generates the current date and/or time according to the format
    string provided by the user as the 'format_str' keyword argument.
    The resulting string can be obtained by accessing the 'info'
    readonly property.

    It accepts the following optional parameters as keyword arguments:

    Options:
        format_str: str
            Sets the format string to be used for the date and time.
            [default:  "%A %d/%m/%Y %R"]

        label: str
            A label to identify the information on each module.
            [default: None]

        delay: float
            Sets the time it takes to update the module's information,
            in seconds. [default: 1.0]
    """
    format_str: str = "%A %d/%m/%Y %R"
    label: str
    delay: float = 1.0

    @property
    def info(self):
        return f"{self.label} {self._info()}" if self.label else self._info()

    def _info(self):
        return time.strftime(self.format_str)
