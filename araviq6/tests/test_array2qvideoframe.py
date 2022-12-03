# pytest-xvfb may fail by running this code in ubuntu.
# It's because for unknown reason, ``QVideoFrame.toImage()`` suffers memory issue
# when the video frame is manually constructed and modified.
# This issue happens only when any other test file is run before this one.
# Should the user encounter such error, run the test for this file separately.

import cv2  # type: ignore[import]
import numpy as np
import qimage2ndarray  # type: ignore[import]
from araviq6 import array2qvideoframe


def test_array2qvideoframe(qtbot):
    bgr_array = np.array([[[1, 2, 3]]], dtype=np.uint8)
    rgb_array = cv2.cvtColor(bgr_array, cv2.COLOR_BGR2RGB)
    frame = array2qvideoframe(bgr_array)
    assert np.all(qimage2ndarray.rgb_view(frame.toImage()) == rgb_array)
