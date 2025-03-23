from abc import ABCMeta, abstractmethod


class BaseModule(metaclass=ABCMeta):
    """
    This is a base class for dwm bar modules. Each module should return
    its relevant information as a formatted string through a 'info'
    property. The information from all the modules will be condensed and
    then printed in the bar.
    """

    @property
    @abstractmethod
    def info(self):
        """The module's information as a formatted string."""
