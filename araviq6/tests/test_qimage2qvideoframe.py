# pytest-xvfb may fail by running this code in ubuntu.
# It's because for unknown reason, ``QVideoFrame.toImage()`` suffers memory issue
# when the video frame is manually constructed and modified.
# This issue happens only when any other test file is run before this one.
# Should the user encounter such error, run the test for this file separately.

import cv2  # type: ignore[import]
import qimage2ndarray  # type: ignore[import]
from araviq6 import qimage2qvideoframe, get_samples_path


def test_qimage2qvideoframe(qtbot):
    image1 = qimage2ndarray.array2qimage(cv2.imread(get_samples_path("hello.jpg")))
    assert not image1.isNull()

    image2 = qimage2qvideoframe(image1).toImage()
    image2.convertTo(image1.format())
    assert not image2.isNull()
    assert image1.format() == image2.format()
    assert image1 == image2
