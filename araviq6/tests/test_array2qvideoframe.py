import cv2  # type: ignore[import]
import numpy as np
import qimage2ndarray  # type: ignore[import]
from araviq6 import array2qvideoframe
from araviq6.util import get_samples_path


def test_array2qvideoframe(qtbot):
    bgr_array = cv2.imread(get_samples_path("hello.jpg"))
    rgb_array = cv2.cvtColor(bgr_array, cv2.COLOR_BGR2RGB)
    frame = array2qvideoframe(bgr_array)
    assert np.all(qimage2ndarray.rgb_view(frame.toImage()) == rgb_array)
