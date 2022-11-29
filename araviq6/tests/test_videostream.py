from araviq6 import FrameToArrayConverter, get_samples_path
import cv2  # type: ignore[import]
import numpy as np
import pytest
from qimage2ndarray import byte_view, gray2qimage, array2qimage  # type: ignore[import]


def test_FrameToArrayConverter(qtbot):
    bgr_array = cv2.imread(get_samples_path("hello.jpg"))
    gray_array = cv2.cvtColor(bgr_array, cv2.COLOR_BGR2GRAY)
    rgb_array = cv2.cvtColor(bgr_array, cv2.COLOR_BGR2RGB)
    gray_img = gray2qimage(gray_array)
    rgb_img = array2qimage(rgb_array)

    conv = FrameToArrayConverter()
    assert np.all(conv.convertQImageToArray(rgb_img) == rgb_array)
    with pytest.raises(ValueError):
        conv.convertQImageToArray(gray_img)

    conv.setConverter(byte_view)
    assert np.all(conv.convertQImageToArray(gray_img) == gray_array[..., np.newaxis])
