"""
This script defines default methods for use with the module classes.
Each method described here can be used with the 'trait' decorator to
apply it directly to a class.
"""
import platform


def __init__(self, **options):
    """
    Initialize the module with optional parameters. Each optional
    parameter passed this way must be provided as a keyword argument.
    """
    types = {k: v for k, v in self.__annotations__.items()}
    values = {k: (t, getattr(self, k, None)) for k, t in types.items()}

    for key, (value_type, default_value) in values.items():
        value = options.get(key, default_value)
        if value is not None:
            value = value_type(value)

        if value == "":
            value = None

        setattr(self, key, value)


def __repr__(self):
    """Showcase a bar module object with its attributes."""
    cls = type(self).__name__
    attrs = ", ".join([f"{k}={repr(v)}" for k, v in self.__dict__.items()])
    return f"{cls}({attrs})"


def __new__(cls, **options):
    """
    Create a proper instance of the module according to
    the host machine's operating system.
    """
    system = platform.system()
    module = cls.modules[system]
    module.__doc__ = cls.__doc__
    return module(**options)
