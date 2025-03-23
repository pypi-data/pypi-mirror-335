import ctypes


class X:
    """A namespace class to communicate with the X server."""
    libX11 = ctypes.cdll.LoadLibrary("libX11.so")
    display = None
    root_window = None
    encoding = "utf-8"

    def __new__(_):
        """This class cannot be instantiated."""
        raise TypeError(f"You cannot instantiate X")

    def __init_subclass__(_):
        """This class cannot be subclassed."""
        raise TypeError(f"You cannot subclass X")

    @classmethod
    def connect(cls):
        """Creates a new connection to the X server."""
        cls.libX11.XOpenDisplay.argtypes = [ctypes.c_char_p]
        cls.libX11.XOpenDisplay.restype = ctypes.c_void_p
        cls.display = cls.libX11.XOpenDisplay(None)

    @classmethod
    def init_root_window(cls):
        """Sets an internal reference to the root window."""
        cls.libX11.XDefaultRootWindow.argtypes = [ctypes.c_void_p]
        cls.libX11.XDefaultRootWindow.restype = ctypes.c_ulong
        cls.root_window = cls.libX11.XDefaultRootWindow(cls.display)

    @classmethod
    def set_root_window_name(cls, name: str) -> bool:
        """Update the root window name."""
        if not cls.display or not cls.root_window:
            return False

        cls.libX11.XStoreName.argtypes = [
            ctypes.c_void_p, ctypes.c_ulong, ctypes.c_char_p
        ]
        cls.libX11.XStoreName.restype = ctypes.c_bool

        result = cls.libX11.XStoreName(
            cls.display, cls.root_window, name.encode(cls.encoding)
        )
        if not result:
            return False

        cls.libX11.XFlush.argtypes = [ctypes.c_void_p]
        cls.libX11.XFlush.restype = ctypes.c_bool
        return cls.libX11.XFlush(cls.display)

    @classmethod
    def reset_root_window_name(cls):
        if cls.display and cls.root_window:
            cls.set_root_window_name("")

    @classmethod
    def disconnect(cls):
        """Close the connection to the X server."""
        if cls.display:
            cls.libX11.XCloseDisplay.argtypes = [ctypes.c_void_p]
            cls.libX11.XCloseDisplay(cls.display)
        cls.display = None
        cls.root_window = None
