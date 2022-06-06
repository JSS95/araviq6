from araviq6.dynqt6 import QtCore

try:
    import PyQt6 as Qt6  # type: ignore[import]
except ModuleNotFoundError:
    import PySide6 as Qt6  # type: ignore[import, no-redef]


def test_QtCore_alias():
    """Test that pyqtSignal and pyqtSlot are accessible by Signal and Slot."""
    assert Qt6.QtCore == QtCore
    QtCore.Signal
    QtCore.Slot
