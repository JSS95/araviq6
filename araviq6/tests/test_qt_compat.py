from araviq6.qt_compat import QtCore, QtWidgets


def test_import_QtCore():
    assert hasattr(QtCore, "Qt")
    assert hasattr(QtCore, "Signal")
    assert hasattr(QtCore, "Slot")


def test_import_QtWidgets():
    assert hasattr(QtWidgets, "QWidget")
