from PySide6.QtCore import QObject, Signal, Slot
from PySide6.QtWidgets import QMainWindow
from PySide6.QtMultimedia import QCamera, QMediaCaptureSession, QVideoFrame, QVideoSink
from PySide6.QtMultimediaWidgets import QVideoWidget


class VideoFrameProcessor(QObject):
    videoFrameChanged = Signal(QVideoFrame)

    def setVideoFrame(self, frame: QVideoFrame):
        # TODO: implement video processing
        self.videoFrameChanged.emit(frame)


class Window(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._camera = QCamera()
        self._captureSession = QMediaCaptureSession()
        self._cameraVideoSink = QVideoSink()
        self._frameProcessor = VideoFrameProcessor()
        self._videoWidget = QVideoWidget()

        # set up the pipeline
        self._captureSession.setCamera(self._camera)
        self._captureSession.setVideoSink(self._cameraVideoSink)
        self._cameraVideoSink.videoFrameChanged.connect(
            self._frameProcessor.setVideoFrame
        )
        self._frameProcessor.videoFrameChanged.connect(self._onVideoFrameChange)

        self.setCentralWidget(self._videoWidget)

        self._camera.start()

    @Slot(QVideoFrame)
    def _onVideoFrameChange(self, frame: QVideoFrame):
        self._videoWidget.videoSink().setVideoFrame(frame)


if __name__ == "__main__":
    from PySide6.QtWidgets import QApplication
    import sys

    app = QApplication(sys.argv)
    window = Window()
    window.show()
    app.exec()
    app.quit()
