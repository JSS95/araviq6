"""
Testing helpers
===============

:mod:`araviq6.util.testing` provides functions to help writing unit tests.

"""

import os
import numpy as np
import qimage2ndarray  # type: ignore[import]
import araviq6
from araviq6.qt_compat import QtCore, QtGui, QtMultimedia
from araviq6.videostream import VideoProcessWorker
from typing import Optional


__all__ = [
    "get_samples_path",
    "VideoProcessWorkerTester",
]


def get_samples_path(*paths: str) -> str:
    """
    Get the absolute path to the directory where the sample data are stored.

    Parameters
    ==========

    paths
        Subpaths under ``araviq6/samples/`` directory.

    Returns
    =======

    path
        Absolute path to the sample depending on the user's system.

    """
    module_path = os.path.abspath(araviq6.__file__)
    module_path = os.path.split(module_path)[0]
    sample_dir = os.path.join(module_path, "samples")
    sample_dir = os.path.normpath(sample_dir)
    sample_dir = os.path.normcase(sample_dir)

    path = os.path.join(sample_dir, *paths)
    return path


class VideoProcessWorkerTester(QtCore.QObject):

    maximumReached = QtCore.Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._worker = None
        self._ready = True

        self._inputArray = np.empty((0,))

        self._count = 0
        self._maxCount = 1

    def worker(self) -> Optional[VideoProcessWorker]:
        return self._worker

    def setWorker(self, worker: Optional[VideoProcessWorker]):
        oldWorker = self.worker()
        if oldWorker is not None:
            oldWorker.videoFrameChanged.disconnect(self._onVideoFramePassedByWorker)
        self._worker = worker
        if worker is not None:
            worker.videoFrameChanged.connect(self._onVideoFramePassedByWorker)

    def count(self) -> int:
        return self._count

    def maxCount(self) -> int:
        return self._maxCount

    def setMaxCount(self, maxCount: int):
        self._maxCount = maxCount

    def setVideoFrame(self, frame: QtMultimedia.QVideoFrame):
        if not self._ready:
            return
        self._ready = False

        inputImg = frame.toImage()
        if not inputImg.isNull():
            self._inputArray = self.imageToArray(inputImg).copy()

        worker = self.worker()
        if worker is not None:
            worker.setVideoFrame(frame)

    def _onVideoFramePassedByWorker(self, frame: QtMultimedia.QVideoFrame):
        worker = self.worker()
        outputImg = frame.toImage()
        if not outputImg.isNull() and worker is not None:
            outputArray = self.imageToArray(outputImg)
            assert np.all(worker.processArray(self._inputArray) == outputArray)

        self._count += 1
        if self._count >= self._maxCount:
            self._ready = False
            self.maximumReached.emit()
        else:
            self._ready = True

    def imageToArray(self, image: QtGui.QImage) -> np.ndarray:
        return qimage2ndarray.rgb_view(image, byteorder=None)

    def reset(self):
        self._ready = False
        self._inputArray = np.empty((0,))
        self._count = 0
        self._ready = True
