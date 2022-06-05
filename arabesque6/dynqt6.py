"""
Dynamically import PySide6 or PyQt6
"""

try:
    from PySide6 import QtCore, QtGui, QtWidgets, QtMultimedia  # type: ignore
except ModuleNotFoundError:
    from PyQt6 import QtCore, QtGui, QtWidgets, QtMultimedia  # type: ignore

    QtCore.Signal = QtCore.pyqtSignal  # type: ignore
    QtCore.Slot = QtCore.pyqtSlot  # type: ignore


__all__ = [
    "QtCore",
    "QtGui",
    "QtWidgets",
    "QtMultimedia",
]
