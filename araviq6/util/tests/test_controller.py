from araviq6 import get_samples_path, ClickableSlider
from araviq6.qt_compat import QtCore


VID_PATH = get_samples_path("hello.mp4")


def test_ClickableSlider(qtbot):
    slider = ClickableSlider()
    qtbot.addWidget(slider)
    assert slider.value() == 0

    pos = QtCore.QPoint(10, 10)
    qtbot.mouseClick(slider, QtCore.Qt.MouseButton.LeftButton, pos=pos)
    assert slider.value() == slider.pixelPosToRangeValue(pos)

    slider.close()
