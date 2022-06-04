"""
Dynamically import PySide6 or PyQt6
"""

import os
from qimage2ndarray.qt_driver import QtDriver  # type: ignore[import]


class Qt6Driver(QtDriver):
    DRIVERS = ("PySide6", "PyQt6")
    DEFAULT = "PySide6"

    def __init__(self, drv=os.environ.get("QT_DRIVER")):
        super().__init__(drv)
        if self._drv == "PyQt6":
            self.QtCore.Signal = self.QtCore.pyqtSignal
            self.QtCore.Slot = self.QtCore.pyqtSlot


Qt6 = Qt6Driver()
QtCore = Qt6.QtCore
