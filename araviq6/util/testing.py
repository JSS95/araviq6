"""
Testing helpers
===============

:mod:`araviq6.util.testing` provides utilities to help writing unit tests.

"""

import os
import numpy as np
import araviq6
from araviq6.qt_compat import QtCore, QtMultimedia
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
    """
    Class to test :class:`VideoProcessWorker` by checking frame bits.

    To test a worker, set it to :meth:`worker` and pass proper video frame to
    :meth:`testVideoFrame`. The tester checks if the video frame emittd by the
    worker is correctly processed. :class:`AssertionError` is raised on error.

    Notes
    =====

    ``QVideoFrame`` easily faces memory issue when assigned to a variable outside
    video pipeline. Use ``QVideoSink.videoFrame()`` to test with video frame.

    .. code-block:: python

       player.setVideoSink(sink)
       sink.videoFrameChanged.connect(player.stop)
       player.play()  # immediately stops after passing first frame to sink
       tester.testVideoFrame(sink.videoFrame())
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self._worker = None
        self._inputArray = np.empty((0,))

    def worker(self) -> Optional[VideoProcessWorker]:
        """
        Worker instance which will be tested.

        See also :meth:`setWorker`.
        """
        return self._worker

    def setWorker(self, worker: Optional[VideoProcessWorker]):
        """
        Set *worker* to be tested.

        See also :meth:`worker`.
        """
        oldWorker = self.worker()
        if oldWorker is not None:
            oldWorker.videoFrameProcessed.disconnect(self._onVideoFramePassedByWorker)
        self._worker = worker
        if worker is not None:
            worker.videoFrameProcessed.connect(self._onVideoFramePassedByWorker)

    def testVideoFrame(self, frame: QtMultimedia.QVideoFrame):
        """Test :meth:`worker` with *frame*."""
        inputImg = frame.toImage()
        worker = self.worker()
        if not inputImg.isNull() and worker is not None:
            self._inputArray = worker.imageToArray(inputImg).copy()
            worker.processVideoFrame(frame)

    def _onVideoFramePassedByWorker(self, frame: QtMultimedia.QVideoFrame):
        worker = self.worker()
        outputImg = frame.toImage()
        if not outputImg.isNull() and worker is not None:
            outputArray = worker.imageToArray(outputImg)
            assert np.all(worker.processArray(self._inputArray) == outputArray)
