import os
import sys
import math
from os.path import basename

import psutil


def trait(*methods, **named_methods):
    """
    A decorator to be used with class definitions. Dynamically add any
    functions passed as arguments to a class as methods. You can also
    choose method names by passing them as keyword arguments.
    """
    def implement(cls):
        for method in methods:
            name = method.__name__
            setattr(cls, name, method)

        for name, method in named_methods.items():
            method.__name__ = name
            setattr(cls, name, method)

        return cls
    return implement


def number_size(num):
    """
    Return how many characters are necessary to write a number. This
    function should only be used for numbers ranging from 0 to 100.
    """
    if num == 0:
        return 1
    log10 = math.log(abs(num), 10)
    result = math.floor(log10) + 1
    return result


def format_number(num, width, precision):
    """
    Format a number with a given width and precision. If the resulting
    string representation is too large, the precision is reduced so the
    number can fit within the chosen width.
    """
    size = number_size(num)
    if size + precision + 1 > width:
        precision = max(width - size - 1, 0)
    return f"{num:>{width}.{precision}f}"


def find_process():
    """
    Find the previous running instance of the current script.
    If more than one process is found, raise an error.
    """
    current_pid = os.getpid()
    executable = basename(sys.executable)
    script_names = {"dwm-status-bar", "dwm_status_bar", "__main__.py"}

    found_processes = []
    for process in psutil.process_iter(["name", "cmdline"]):
        if process.pid != current_pid:
            name = process.info["name"]
            cmdline = process.info["cmdline"]

            if len(cmdline) < 2:
                continue

            if name == executable and basename(cmdline[1]) in script_names:
                found_processes.append(process)

    if len(found_processes) == 0:
        return None
    elif len(found_processes) == 1:
        return found_processes[0]
    else:
        raise RuntimeError("Multiple processes running the same script found.")


def close():
    """Close the bar process."""
    process = find_process()
    process.terminate()
