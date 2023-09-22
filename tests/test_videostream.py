# pytest-xvfb may fail by running this code in ubuntu.
# It's because for unknown reason, ``QVideoFrame.toImage()`` suffers memory issue
# when the video frame is manually constructed and modified.
# This issue happens only when any other test file is run before this one.
# Should the user encounter such error, run the test for this file separately.

import numpy as np
import qimage2ndarray  # type: ignore[import]
from araviq6 import (
    array2qvideoframe,
    QVideoFrameProperty,
    FrameToArrayConverter,
    ArrayToFrameConverter,
)
from araviq6.qt_compat import QtMultimedia


def test_array2qvideoframe(qtbot):
    bgr_array1 = np.array([[[1]]], dtype=np.uint8)
    frame1 = array2qvideoframe(bgr_array1)
    assert np.all(
        qimage2ndarray.byte_view(frame1.toImage())
        == np.array([[[1, 1, 1, 255]]], dtype=np.uint8)
    )
    assert np.all(
        qimage2ndarray.rgb_view(frame1.toImage()) == np.array([[[1]]], dtype=np.uint8)
    )
    assert np.all(
        qimage2ndarray.alpha_view(frame1.toImage())
        == np.array([[[255]]], dtype=np.uint8)
    )

    bgr_array2 = np.array([[[1, 2]]], dtype=np.uint8)
    frame2 = array2qvideoframe(bgr_array2)
    assert np.all(
        qimage2ndarray.byte_view(frame2.toImage())
        == np.array([[[1, 1, 1, 2]]], dtype=np.uint8)
    )
    assert np.all(
        qimage2ndarray.rgb_view(frame2.toImage()) == np.array([[[1]]], dtype=np.uint8)
    )
    assert np.all(
        qimage2ndarray.alpha_view(frame2.toImage()) == np.array([[[2]]], dtype=np.uint8)
    )

    bgr_array3 = np.array([[[1, 2, 3]]], dtype=np.uint8)
    frame3 = array2qvideoframe(bgr_array3)
    assert np.all(
        qimage2ndarray.byte_view(frame3.toImage())
        == np.array([[[1, 2, 3, 255]]], dtype=np.uint8)
    )
    assert np.all(
        qimage2ndarray.rgb_view(frame3.toImage())
        == np.array([[[3, 2, 1]]], dtype=np.uint8)
    )
    assert np.all(
        qimage2ndarray.alpha_view(frame3.toImage())
        == np.array([[[255]]], dtype=np.uint8)
    )

    bgr_array4 = np.array([[[1, 2, 3, 4]]], dtype=np.uint8)
    frame4 = array2qvideoframe(bgr_array4)
    assert np.all(
        qimage2ndarray.byte_view(frame4.toImage())
        == np.array([[[1, 2, 3, 4]]], dtype=np.uint8)
    )
    assert np.all(
        qimage2ndarray.rgb_view(frame4.toImage())
        == np.array([[[3, 2, 1]]], dtype=np.uint8)
    )
    assert np.all(
        qimage2ndarray.alpha_view(frame4.toImage()) == np.array([[[4]]], dtype=np.uint8)
    )


def test_FrameToArrayConverter(qtbot):
    frame = array2qvideoframe(np.array([[[1, 2, 3]]], dtype=np.uint8))
    converter = FrameToArrayConverter()

    with qtbot.waitSignal(
        converter.arrayConverted,
        check_params_cb=lambda array, prop: array.size != 0
        and prop.startTime == frame.startTime()
        and prop.endTime == frame.endTime(),
    ):
        converter.convertVideoFrame(frame)

    with qtbot.waitSignal(
        converter.arrayConverted, check_params_cb=lambda array, _: array.size == 0
    ):
        converter.convertVideoFrame(QtMultimedia.QVideoFrame())


def test_ArrayToFrameConverter(qtbot):
    converter = ArrayToFrameConverter()

    prop = QVideoFrameProperty(startTime=10, endTime=20)
    with qtbot.waitSignal(
        converter.frameConverted,
        check_params_cb=lambda frame: frame.isValid()
        and frame.startTime() == prop.startTime
        and frame.endTime() == prop.endTime,
    ):
        converter.convertArray(np.array([[[1, 2, 3]]], dtype=np.uint8), prop)

    nullProp = QVideoFrameProperty()
    with qtbot.waitSignal(
        converter.frameConverted,
        check_params_cb=lambda frame: frame.isValid()
        and frame.startTime() == nullProp.startTime
        and frame.endTime() == nullProp.endTime,
    ):
        converter.convertArray(np.array([[[1, 2, 3]]], dtype=np.uint8))

    with qtbot.waitSignal(
        converter.frameConverted, check_params_cb=lambda frame: not frame.isValid()
    ):
        converter.convertArray(np.empty((0, 0, 0), dtype=np.uint8))
