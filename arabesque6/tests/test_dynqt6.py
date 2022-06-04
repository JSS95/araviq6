try:
    import PyQt6  # type: ignore[import]
    IGNORE = False
except ModuleNotFoundError:
    IGNORE = True


def test_PyQt6_QtCore_alias():
    """Test that pyqtSignal and pyqtSlot are accessible by Signal and Slot."""
    if not IGNORE:
        PyQt6.QtCore.Signal
        PyQt6.QtCore.Slot
