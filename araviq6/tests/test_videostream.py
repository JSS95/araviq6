from araviq6 import FrameToArrayConverter, get_samples_path
from araviq6.qt_compat import QtCore, QtMultimedia


def test_FrameToArrayConverter(qtbot):

    class ArraySink(QtCore.QObject):
        arrayChanged = QtCore.Signal()
        def setArray(self, array):
            self.array = array
            self.arrayChanged.emit()

    player = QtMultimedia.QMediaPlayer()
    playerSink = QtMultimedia.QVideoSink()
    converter = FrameToArrayConverter()
    arraySink = ArraySink()

    player.setVideoSink(playerSink)
    playerSink.videoFrameChanged.connect(converter.convertVideoFrame)
    converter.arrayConverted.connect(arraySink.setArray)
    arraySink.arrayChanged.connect(player.stop)

    with qtbot.waitSignal(arraySink.arrayChanged):
        player.setSource(QtCore.QUrl.fromLocalFile(get_samples_path("hello.mp4")))
        player.play()
    assert arraySink.array.size != 0

    with qtbot.waitSignal(arraySink.arrayChanged):
        converter.convertVideoFrame(QtMultimedia.QVideoFrame())
    assert arraySink.array.size == 0
