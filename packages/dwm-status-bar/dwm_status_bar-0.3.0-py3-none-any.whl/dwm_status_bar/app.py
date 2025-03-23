import signal
import asyncio
import subprocess as sp
import sys
import os
import time
import getopt
import traceback

import psutil

from dwm_status_bar.modules.base_module import BaseModule
from dwm_status_bar.config import Config
from dwm_status_bar.util import find_process, close
from dwm_status_bar.x11 import X


class App:
    """The entrypoint class that starts the application."""
    short_opts = "xc:v"

    def __new__(cls):
        """
        The application entrypoint. Creates a new instance of the
        status bar application, calls the initialization method and
        returns the status code to the calling process upon exiting.
        """
        app = super().__new__(cls)
        app.init()

        X.connect()
        if X.display is None:
            return 2

        X.init_root_window()
        if X.root_window is None:
            X.disconnect()
            return 3

        return app.main()

    def init(self):
        """Initializes the application before starting the main loop."""
        self.returncode = 0
        self.bar = None
        self.filename = None
        self.should_restart = False

        opts, _ = self.parse_args()

        for flag, value in opts:
            if flag == "-x":
                close()
                sys.exit(0)
            if flag == "-c":
                self.filename = value
            elif flag == "-v":
                from dwm_status_bar import __version__
                print(__version__)
                sys.exit(0)

        process = find_process()
        if process is not None:
            sys.exit("A previous bar process is already running.")

        cache_dir = os.environ.get("XDG_CACHE_HOME", os.path.join(
            os.environ["HOME"], ".cache"
        ))
        if not os.path.exists(cache_dir):
            os.mkdir(cache_dir, mode=0o755)

        self.logfile = os.path.join(cache_dir, "dwm_status_bar.log")

        signal.signal(signal.SIGHUP, self._restart)
        signal.signal(signal.SIGTERM, self._close)

    def main(self):
        """
        Instantiate the bar and execute it as an async coroutine.

        After all the tasks finish execution, the application either
        exits, or re-reads its configuration on SIGHUP.

        If any error occurs, it gets printed to stderr and to a log
        file.
        """
        running_loop = True
        while running_loop:
            try:
                self.configs = self.get_configs(self.filename)
                asyncio.run(self._start())
            except Exception as e:
                with open(self.logfile, mode="a") as file:
                    print(time.strftime("--- %d/%b/%Y %X ---"), file=file)
                    traceback.print_exc(file=file)
                print(f"{type(e).__name__}:", e, file=sys.stderr)
                self.returncode = 1
                self.should_restart = False
            finally:
                if self.should_restart:
                    self.should_restart = False
                else:
                    running_loop = False

        X.reset_root_window_name()
        X.disconnect()
        return self.returncode

    def get_configs(self, filename=None):
        """Read and parse config information from an XML file."""
        if filename and not os.path.exists(filename):
            msg = f"Configuration file '{filename}' not found."
            raise FileNotFoundError(msg)

        if filename is None:
            home = os.environ["HOME"]
            config_home = os.environ.get("XDG_CONFIG_HOME", f"{home}/.config")
            config_dirs = os.environ.get("XDG_CONFIG_DIRS", "/etc/xdg").split(":")

            name = os.path.join(config_home, "dwm_status_bar/config.xml")
            if os.path.exists(name):
                filename = name
            else:
                for name in map(
                    lambda d: os.path.join(d, "dwm_status_bar/config.xml"),
                    config_dirs
                ):
                    if os.path.exists(name):
                        filename = name
                        break

        try:
            return Config(filename)
        except FileNotFoundError:
            return Config()

    def parse_args(self):
        """Read and parse commandline arguments."""
        try:
            return getopt.getopt(sys.argv[1:], self.short_opts)
        except getopt.GetoptError as err:
            print("Error:", err, file=sys.stderr)
            sys.exit(1)

    async def _start(self):
        with self.BarLogger(self.configs) as bar:
            self.bar = bar
            await bar()

    def _restart(self, s, f):
        self.should_restart = True
        self.bar.close()

    def _close(self, s, f):
        self.bar.close()

    class BarLogger:
        """
        This class sends information to the status bar. It receives a
        Config object and use it to write and update information on the
        bar.

        It is meant to be used as a context manager, which returns an
        async callable object that starts the loop. Ex:

            with BarLogger(configs) as bar:
                await bar()
        """
        def __init__(self, configs: Config):
            """Set attributes and asynchronous signal handlers."""
            self.configs = configs
            self.module_list = self.configs.module_list
            self.info_list = [m.info for m in self.module_list]
            self.tasks = set()

            loop = asyncio.get_running_loop()
            loop.add_signal_handler(signal.SIGUSR1, self._log_info)

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc_value, traceback):
            """Ensure graceful exit upon cancelling tasks."""
            try:
                loop = asyncio.get_running_loop()
                loop.remove_signal_handler(signal.SIGUSR1)
            except RuntimeError:
                pass

            return exc_type is asyncio.CancelledError

        async def __call__(self):
            """Start running tasks."""
            signal.raise_signal(signal.SIGUSR1)
            async with asyncio.TaskGroup() as tg:
                for index, module in enumerate(self.module_list):
                    self._create_watcher(tg, index, module)

        def close(self):
            """Cancel every running task."""
            for task in self.tasks:
                task.cancel()

        def _log_info(self):
            """Retrieve information and write to the bar."""
            info = " | ".join(v for v in self.info_list if v is not None)
            if not X.set_root_window_name(info):
                self.close()

        def _create_watcher(self, tg, index, module):
            """Create a new task for a given module."""
            async def watch():
                while self.module_list[index] is not None:
                    self.info_list[index] = module.info
                    await asyncio.sleep(module.delay)
                    signal.raise_signal(signal.SIGUSR1)

            task = tg.create_task(watch(), name=type(module).__name__)
            self.tasks.add(task)
            task.add_done_callback(self.tasks.discard)
