from araviq6 import get_data_path, ClickableSlider

try:
    from PySide6.QtCore import Qt, QPoint  # type: ignore[import]
except ModuleNotFoundError:
    from PyQt6.QtCore import Qt, QPoint  # type: ignore[import, no-redef]


VID_PATH = get_data_path("hello.mp4")


def test_ClickableSlider(qtbot):
    slider = ClickableSlider()
    qtbot.addWidget(slider)
    assert slider.value() == 0

    pos = QPoint(10, 10)
    qtbot.mouseClick(slider, Qt.LeftButton, pos=pos)
    assert slider.value() == slider.pixelPosToRangeValue(pos)
