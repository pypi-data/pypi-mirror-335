import xml.dom as dom
import xml.dom.minidom as minidom
import importlib
import os
import runpy
import re

from dwm_status_bar.modules.base_module import BaseModule


class ConfigError(Exception):
    """Error class for exceptions related to configuration."""
    def add_note(self, note):
        spaces = self._count_spaces(note)
        pat = r"^\s{" + str(spaces) + r"}"
        newnote = "\n" + re.sub(pat, "", note, flags=re.MULTILINE)
        super().add_note(f"{newnote.strip()}\n")

    def _count_spaces(self, text):
        min_spaces = float("Infinity")
        lines = text.splitlines()
        for line in lines[1:]:
            spaces = len(line) - len(line.lstrip())
            min_spaces = min(min_spaces, spaces)

        return min_spaces


class Config:
    """
    An object that holds configuration parameters for the bar modules.
    It reads the configuration file and parses it into a proper format
    to be read by the App object.
    """

    def __init__(self, filename=None):
        if filename is None:
            from dwm_status_bar.modules.datetime_module import DateTimeModule
            self.module_classes = {"DateTimeModule": DateTimeModule}
            self.module_list = [DateTimeModule()]
            return

        self.module_classes = {}
        self.module_list = []

        current_dir = os.path.dirname(__file__)
        modules_dir = os.path.join(current_dir, "modules")
        module_names = self._get_module_names(os.listdir(modules_dir))
        self._import_modules(module_names)

        self._read_config_file(filename)

    def _get_module_names(self, file_list):
        filtered = filter(lambda f: f.endswith("_module.py"), file_list)
        names = [f"dwm_status_bar.modules.{f.replace('.py', '')}" for f in filtered]
        return names

    def _import_modules(self, names):
        for name in names:
            py_module = importlib.import_module(name)
            obj_names = dir(py_module)
            mod_names = [n for n in obj_names if n.endswith("Module")]

            for mod in mod_names:
                self.module_classes[mod] = getattr(py_module, mod)

        del self.module_classes["BaseModule"]

    def _holds_text(self, node):
        """
        Returns True if node is an element with text and no child elements
        and False otherwise.
        """
        if not isinstance(node, dom.minidom.Node):
            return False

        if node.nodeType != node.ELEMENT_NODE:
            return False

        if not node.hasChildNodes():
            return False

        for child in node.childNodes:
            if node.nodeType == node.ELEMENT_NODE:
                return False

        return True

    def _purge_whitespace(self, node):
        """Removes unwanted whitespace from XML nodes."""
        if node.nodeType == node.DOCUMENT_NODE:
            return self._purge_whitespace(node.documentElement)

        if not node.hasChildNodes() or self._holds_text(node):
            return

        for child in node.childNodes:
            if child.nodeType == node.TEXT_NODE:
                node.removeChild(child)

            elif child.nodeType == node.ELEMENT_NODE:
                self._purge_whitespace(child)

    def _read_config_file(self, filename):
        """Parse XML configuration file."""
        configs = minidom.parse(filename)
        self._purge_whitespace(configs)

        root = configs.documentElement
        root_attr = dict(root.attributes.items())
        if "extend" in root_attr:
            self._extend_configs(root_attr["extend"])

        for elem in root.childNodes:
            if elem.nodeType != elem.ELEMENT_NODE:
                continue

            if elem.tagName not in self.module_classes:
                msg = f"Module class '{elem.tagName}' was not found."
                note = f"""
            This error ocurred because the '{elem.tagName}' class specified
            in your configuration file could not be located or instantiated.
            This could be due to a typo in the class name or a missing
            attribute.
                """
                note2 = "To resolve this issue, please ensure that:"
                note3 = f"""
            1. The class name is spelled correctly and matches the name of
               an existing module or class.
            2. If '{elem.tagName}' is meant to be a custom class defined in
               an external file, ensure that you have specified the correct
               path or filename in the 'extend' attribute of the root element
               in your configuration file.
                """
                err = ConfigError(msg)
                err.add_note("")
                err.add_note(note)
                err.add_note(note2)
                err.add_note(note3)
                raise err

            constructor = self.module_classes[elem.tagName]
            module_obj = constructor(**dict(elem.attributes.items()))
            self.module_list.append(module_obj)

    @staticmethod
    def _is_module(cls):
        """Return True if cls is a subclass of BaseModule."""
        try:
            return issubclass(cls, BaseModule)
        except Exception:
            return False

    def _extend_configs(self, filename):
        init_globals = {"BaseModule": BaseModule}
        name = os.path.basename(filename.replace(".py", ""))
        scope = runpy.run_path(filename, init_globals, name)
        ext_modules = {k: v for k, v in scope.items() if self._is_module(v)}

        for name, cls in ext_modules.items():
            self.module_classes[name] = cls
