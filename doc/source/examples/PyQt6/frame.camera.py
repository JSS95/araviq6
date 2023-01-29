"""
Camera example with blurring pipeline on QVideoframe.

The processor receives video frame from the video sink of media capture session,
and emits processed video frame.

"""

import cv2  # type: ignore[import]
import numpy as np
from PyQt6.QtCore import pyqtSlot
from PyQt6.QtWidgets import QMainWindow
from PyQt6.QtMultimedia import QCamera, QMediaCaptureSession, QVideoFrame, QVideoSink
from PyQt6.QtMultimediaWidgets import QVideoWidget
from araviq6 import VideoFrameWorker, VideoFrameProcessor


class BlurWorker(VideoFrameWorker):
    def processArray(self, array: np.ndarray) -> np.ndarray:
        return cv2.GaussianBlur(array, (0, 0), 25)


class Window(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._camera = QCamera()
        self._captureSession = QMediaCaptureSession()
        self._cameraVideoSink = QVideoSink()
        self._frameProcessor = VideoFrameProcessor()
        self._blurWorker = BlurWorker()
        self._videoWidget = QVideoWidget()

        # set up the pipeline
        self._captureSession.setCamera(self._camera)
        self._captureSession.setVideoSink(self._cameraVideoSink)
        self._cameraVideoSink.videoFrameChanged.connect(
            self._frameProcessor.processVideoFrame
        )
        self._frameProcessor.videoFrameProcessed.connect(self.displayVideoFrame)

        self._frameProcessor.setWorker(self._blurWorker)
        self.setCentralWidget(self._videoWidget)

        self._camera.start()

    @pyqtSlot(QVideoFrame)
    def displayVideoFrame(self, frame: QVideoFrame):
        self._videoWidget.videoSink().setVideoFrame(frame)

    def closeEvent(self, event):
        self._frameProcessor.stop()
        super().closeEvent(event)


if __name__ == "__main__":
    from PyQt6.QtWidgets import QApplication
    import sys

    app = QApplication(sys.argv)
    window = Window()
    window.show()
    app.exec()
    app.quit()
