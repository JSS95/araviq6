"""
Dynamic Qt import
=================

Qt API for PyQt6 and PySide6.

To access Qt objects independently to the installed Qt binding, import the Qt
subpackages from this module as if importing from the Qt binding package.

.. code:: python

    from araviq6.qt_compat import QtCore

Or you can use :obj:`qt_api` which is an instance of :class:`QtAPI`.

.. code:: python

    from araviq6.qt_compat import qt_api
    widget = qt_api.QtWidgets.QWidget()

Notes
-----

This module is not part of public API, therefore users must not rely on it.

Based on https://github.com/hmeine/qimage2ndarray and
https://github.com/pytest-dev/pytest-qt.

"""


import os


__all__ = [
    "QtAPI",
    "QtAPIError",
    "qt_api",
]


class QtAPI:
    """
    Interface to access the Qt binding package installed in the environment.

    The instance of this class can be treated as root namespace of Qt package.
    At construction, this object determines the Qt binding package where it will
    import the submodules. When attribute starting with ``Qt`` is called
    (e.g. ``QtCore`` - this is the naming rule for Qt subpackages) this object
    imports the module from root package.

    For example, the following code imports :mod:`PyQt6.QtWidgets` module where
    :class:`QWidget` is retrieved.

    .. code:: python

        from araviq6.qt_compat import QtAPI
        widget = QtAPI("PyQt6").QtWidgets.QWidget()

    Qt binding is determined by following steps.

    1. If *api* argument is passed, use it.

    2. If ``ARAVIQ_QT_API`` environment variable is set, use it.

    3. Try import the packages in following order.

        * PySide6
        * PyQt6

    Letter case does not matter when specifying the API. If importing fails,
    :class:`QtAPIError` is raised.

    """

    # When new API is supported, update README and intro.rst

    def __init__(self, api=os.environ.get("ARAVIQ_QT_API")):
        self._import_errors = {}

        def _can_import(name):
            try:
                __import__(name)
                return True
            except ModuleNotFoundError as e:
                self._import_errors[name] = str(e)
                return False

        # If api is specified, use it.
        if api is not None:
            qtapi = {
                "pyside6": "PySide6",
                "pyqt6": "PyQt6",
            }.get(api.lower())
            if qtapi is None:
                raise QtAPIError(f"Specified Qt API is not supported: '{api}'")
            try:
                __import__(f"{qtapi}.QtCore")
            except ModuleNotFoundError:
                raise QtAPIError(f"Specified Qt API is not installed: '{qtapi}'")
            self.qt_binding = qtapi
        # If api is not specified, try import supported Qt modules.
        # Not importing only the root namespace because when uninstalling from
        # conda, the namespace can still be there.
        elif _can_import("PySide6.QtCore"):
            self.qt_binding = "PySide6"
        elif _can_import("PyQt6.QtCore"):
            self.qt_binding = "PyQt6"
        else:
            errors = "\n".join(
                f"  {module}: {reason}"
                for module, reason in sorted(self._import_errors.items())
            )
            msg = "Supported Qt not installed.\n" + errors
            raise QtAPIError(msg)

        if self.qt_binding in ("PyQt6",):
            self.QtCore.Signal = self.QtCore.pyqtSignal
            self.QtCore.Slot = self.QtCore.pyqtSlot

    def _import_module(self, module_name):
        m = __import__(self.qt_binding, globals(), locals(), [module_name], 0)
        return getattr(m, module_name)

    def __getattr__(self, name):
        if name.startswith("Qt"):
            return self._import_module(name)
        return self.__getattribute__(name)


class QtAPIError(Exception):
    pass


qt_api = QtAPI()

QtCore = qt_api.QtCore
QtWidgets = qt_api.QtWidgets
QtGui = qt_api.QtGui
QtMultimedia = qt_api.QtMultimedia
QtMultimediaWidgets = qt_api.QtMultimediaWidgets
