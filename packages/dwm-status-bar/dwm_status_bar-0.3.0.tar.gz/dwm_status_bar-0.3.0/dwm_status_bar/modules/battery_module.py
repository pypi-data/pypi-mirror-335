import collections
import subprocess as sp
import re
import json

import psutil

from dwm_status_bar.modules.base_module import BaseModule
from dwm_status_bar.util import format_number, trait
from dwm_status_bar.methods import __init__, __repr__, __new__


@trait(__init__, __repr__)
class NetBSDBatteryModule(BaseModule):
    width: int = 5
    precision: int = 2
    label: str
    delay: float = 1.0
    pattern = re.compile("[(%)]")

    @property
    def info(self):
        """
        Returns battery information as a formatted string.
        If no battery is installed, returns None.
        """
        if self._info() is None:
            return None

        return f"{self.label} {self._info()}" if self.label else self._info()

    def _info(self):
        ENVSTAT = "/usr/sbin/envstat"
        command = [ENVSTAT, "-s", "acpibat0:charge,acpibat0:charging"]

        command_output = sp.run(
            command, stdout=sp.PIPE, stderr=sp.DEVNULL, text=True
        )

        if command_output.returncode != 0:
            return None

        output_lines = command_output.stdout.strip().split("\n")

        charge = output_lines[2]
        charging = output_lines[3].split()[1]

        percent = min(float(self.pattern.split(charge)[1]), 100)
        power_plugged = json.loads(charging.lower())

        charging_state = "✓" if power_plugged else "✗"
        num = format_number(percent, self.width, self.precision)
        return f"{charging_state} {num}"


@trait(__init__, __repr__)
class DefaultBatteryModule(BaseModule):
    width: int = 5
    precision: int = 2
    label: str
    delay: float = 1.0

    @property
    def info(self):
        """
        Returns battery information as a formatted string.
        If no battery is installed, returns None.
        """
        if self._info() is None:
            return None

        return f"{self.label} {self._info()}" if self.label else self._info()

    def _info(self):
        try:
            percent, _, power_plugged = psutil.sensors_battery()
        except (AttributeError, ValueError, TypeError):
            return None

        charging_state = "✓" if power_plugged else "✗"
        num = format_number(percent, self.width, self.precision)
        return f"{charging_state} {num}"


@trait(__new__)
class BatteryModule:
    """
    A class representing a battery module for system information
    retrieval. It generates the current energy available in percent
    numbers as a string through the 'info' readonly property. If no
    battery is present, the 'info' property will return None.

    It accepts the following optional parameters as keyword arguments:

    Options:
        width: int
            Sets the total size of the resulting string. [default: 5]

        precision: int
            Sets the desired number of decimals in the resulting number.
            If the number gets too large, the precision is reduced in
            order to fit within the assigned 'width' parameter.
            [default: 2]

        label: str
            A label to identify the information on each module.
            [default: None]

        delay: float
            Sets the time it takes to update the module's information,
            in seconds. [default: 1.0]
    """
    modules = collections.defaultdict(
        lambda: DefaultBatteryModule,
        {
            "NetBSD": NetBSDBatteryModule,
        }
    )
