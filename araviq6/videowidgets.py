"""
Video widgets
=============

:mod:`araviq6.videowidgets` provides convenience widgets with pre-built video
pipelines.

"""

import numpy as np
from araviq6.qt_compat import QtCore, QtWidgets, QtMultimedia
from .labels import NDArrayLabel
from .videostream import NDArrayVideoPlayer, NDArrayMediaCaptureSession
from .util import MediaController


__all__ = [
    "NDArrayVideoPlayerWidget",
    "NDArrayCameraWidget",
]


class NDArrayVideoPlayerWidget(QtWidgets.QWidget):
    """
    Convenience widget to process and display numpy arrays from local video file.

    Examples
    ========

    >>> from PySide6.QtCore import QUrl
    >>> from PySide6.QtWidgets import QApplication
    >>> import sys
    >>> from araviq6 import get_samples_path, NDArrayVideoPlayerWidget
    >>> vidpath = get_samples_path('hello.mp4')
    >>> def runGUI():
    ...     app = QApplication(sys.argv)
    ...     w = NDArrayVideoPlayerWidget()
    ...     w.setSource(QUrl.fromLocalFile(vidpath))
    ...     w.show()
    ...     app.exec()
    ...     app.quit()
    >>> runGUI() # doctest: +SKIP

    Notes
    =====

    This widget processes the frames with single thread, therefore long
    processing blocks the GUI. Refer to the package examples for building
    multithread pipeline.

    """

    def __init__(self, parent=None):
        super().__init__(parent)

        self._videoPlayer = NDArrayVideoPlayer(self)
        self._videoLabel = NDArrayLabel()
        self._mediaController = MediaController()

        self._videoPlayer.arrayChanged.connect(self.setArray)
        self._videoLabel.setAlignment(QtCore.Qt.AlignCenter)
        self._mediaController.setPlayer(self._videoPlayer)

        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self._videoLabel)
        layout.addWidget(self._mediaController)
        self.setLayout(layout)

    @QtCore.Slot(QtCore.QUrl)
    def setSource(self, source: QtCore.QUrl):
        self._videoPlayer.setSource(source)

    @QtCore.Slot(np.ndarray)
    def setArray(self, array: np.ndarray):
        """
        Process the array with :meth:`processArray` and set to :meth:`videoLabel`.
        """
        ret = self.processArray(array)
        self._videoLabel.setArray(ret)

    def processArray(self, array: np.ndarray) -> np.ndarray:
        """Perform array processing. Redefine this method if needed."""
        return array


class NDArrayCameraWidget(QtWidgets.QWidget):
    """
    Convenience widget to process and display numpy arrays from camera.

    Examples
    ========

    >>> from PySide6.QtWidgets import QApplication
    >>> from PySide6.QtMultimedia import QCamera
    >>> import sys
    >>> from araviq6 import NDArrayCameraWidget
    >>> def runGUI():
    ...     app = QApplication(sys.argv)
    ...     widget = NDArrayCameraWidget()
    ...     camera = QCamera()
    ...     widget.setCamera(camera)
    ...     camera.start()
    ...     widget.show()
    ...     app.exec()
    ...     app.quit()
    >>> runGUI() # doctest: +SKIP

    Notes
    =====

    This widget processes the frames with single thread, therefore long
    processing blocks the GUI. Refer to the package examples for building
    multithread pipeline.

    """

    def __init__(self, parent=None):
        super().__init__(parent)

        self._mediaCaptureSession = NDArrayMediaCaptureSession()
        self._videoLabel = NDArrayLabel()

        self._mediaCaptureSession.arrayChanged.connect(self.setArray)
        self._videoLabel.setAlignment(QtCore.Qt.AlignCenter)

        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self._videoLabel)
        self.setLayout(layout)

    @QtCore.Slot(QtMultimedia.QCamera)
    def setCamera(self, camera: QtMultimedia.QCamera):
        self._mediaCaptureSession.setCamera(camera)

    @QtCore.Slot(np.ndarray)
    def setArray(self, array: np.ndarray):
        """
        Process the array with :meth:`processArray` and set to :meth:`videoLabel`.
        """
        ret = self.processArray(array)
        self._videoLabel.setArray(ret)

    def processArray(self, array: np.ndarray) -> np.ndarray:
        """Perform array processing. Redefine this method if needed."""
        return array
