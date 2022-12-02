"""
Video player example with blurring pipeline on numpy array.

The converter receives video frame from the video sink of media capture session,
and emits numpy array. The processor then receives it and emits processed array.

"""

import cv2  # type: ignore
import numpy as np
import numpy.typing as npt
from PySide6.QtCore import QObject, Signal, Slot, Qt, QThread
from PySide6.QtMultimedia import QMediaCaptureSession, QVideoSink
from PySide6.QtWidgets import QMainWindow
from araviq6 import FrameToArrayConverter, NDArrayLabel


class BlurringProcessor(QObject):
    """Video pipeline component for Gaussian blurring on numpy array."""

    arrayChanged = Signal(np.ndarray)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._ready = True

    def ready(self) -> bool:
        return self._ready

    @Slot(np.ndarray)
    def setArray(self, array: np.ndarray):
        self._ready = False
        self.arrayChanged.emit(cv2.GaussianBlur(array, (0, 0), 25))
        self._ready = True


class Window(QMainWindow):

    _processRequested = Signal(np.ndarray)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._camera = QCamera()
        self._captureSession = QMediaCaptureSession()
        self._cameraSink = QVideoSink()
        self._arrayConverter = FrameToArrayConverter()
        self._arrayProcessor = BlurringProcessor()
        self._arrayLabel = NDArrayLabel()

        # set up the pipeline
        self._captureSession.setCamera(self._camera)
        self._captureSession.setVideoSink(self._cameraSink)
        self._cameraSink.videoFrameChanged.connect(self._arrayConverter.setVideoFrame)
        self._arrayConverter.arrayChanged.connect(self._displayImageFromCamera)
        self._processRequested.connect(self._arrayProcessor.setArray)
        self._arrayProcessor.arrayChanged.connect(self._arrayLabel.setArray)

        self._arrayLabel.setAlignment(Qt.AlignCenter)  # type: ignore[arg-type]
        self.setCentralWidget(self._arrayLabel)

        self._processorThread = QThread()
        self._arrayProcessor.moveToThread(self._processorThread)
        self._processorThread.start()

        self._camera.start()

    @Slot(np.ndarray)
    def _displayImageFromCamera(self, array: npt.NDArray[np.uint8]):
        processor = self._arrayProcessor
        if not processor.ready():
            return
        self._processRequested.emit(array)

    def closeEvent(self, event):
        self._processorThread.quit()
        self._processorThread.wait()
        super().closeEvent(event)


if __name__ == "__main__":
    from PySide6.QtWidgets import QApplication
    from PySide6.QtMultimedia import QCamera
    import sys

    app = QApplication(sys.argv)
    window = Window()
    window.show()
    app.exec()
    app.quit()
