from importlib.metadata import version


__version__: str | None
try:
    __version__ = version("dwm_status_bar")
except ModuleNotFoundError:
    __version__ = None
