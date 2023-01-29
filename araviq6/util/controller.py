"""
Media controller
================

:mod:`araviq6.util.controller` provides widget to control media player.

"""

from araviq6.qt_compat import QtCore, QtGui, QtMultimedia, QtWidgets
from typing import Optional

try:
    from typing import Protocol
except ImportError:
    from typing_extensions import Protocol  # type: ignore[assignment]


__all__ = [
    "ClickableSlider",
    "SignalProtocol",
    "PlayerProtocol",
    "MediaController",
]


class ClickableSlider(QtWidgets.QSlider):
    """``QSlider`` whose groove can be clicked to move to position."""

    # https://stackoverflow.com/questions/52689047
    def mousePressEvent(self, event: QtGui.QMouseEvent):
        if event.button() == QtCore.Qt.MouseButton.LeftButton:
            val = self.pixelPosToRangeValue(event.position())
            self.setValue(val)
        super().mousePressEvent(event)

    def pixelPosToRangeValue(self, pos: QtCore.QPointF) -> int:
        opt = QtWidgets.QStyleOptionSlider()
        self.initStyleOption(opt)
        gr = self.style().subControlRect(
            QtWidgets.QStyle.ComplexControl.CC_Slider,
            opt,
            QtWidgets.QStyle.SubControl.SC_SliderGroove,
            self,
        )
        sr = self.style().subControlRect(
            QtWidgets.QStyle.ComplexControl.CC_Slider,
            opt,
            QtWidgets.QStyle.SubControl.SC_SliderHandle,
            self,
        )

        if self.orientation() == QtCore.Qt.Orientation.Horizontal:
            sliderLength = sr.width()
            sliderMin = gr.x()
            sliderMax = gr.right() - sliderLength + 1
        else:
            sliderLength = sr.height()
            sliderMin = gr.y()
            sliderMax = gr.bottom() - sliderLength + 1
        if self.orientation() == QtCore.Qt.Orientation.Horizontal:
            p = pos.x() - sr.center().x() + sr.topLeft().x()
        else:
            p = pos.y() - sr.center().y() + sr.topLeft().y()
        return QtWidgets.QStyle.sliderValueFromPosition(
            self.minimum(),
            self.maximum(),
            int(p - sliderMin),
            sliderMax - sliderMin,
            opt.upsideDown,  # type: ignore[attr-defined]
        )


class SignalProtocol(Protocol):
    def connect(
        self,
        receiver,
        type: QtCore.Qt.ConnectionType = QtCore.Qt.ConnectionType.AutoConnection,
    ):
        ...

    def disconnect(self, receiver):
        ...


class PlayerProtocol(Protocol):

    durationChanged: SignalProtocol
    positionChanged: SignalProtocol
    playbackStateChanged: SignalProtocol

    def playbackState(self) -> QtMultimedia.QMediaPlayer.PlaybackState:
        ...

    def play(self):
        ...

    def pause(self):
        ...

    def stop(self):
        ...

    def setPosition(self, position: int):
        ...


class MediaController(QtWidgets.QWidget):
    """
    Widget to control :class:`QtMultimedia.QMediaPlayer`.

    This controller can change the playback state and media position by
    :meth:`playButton`, :meth:`stopButton`, and :meth:`slider`.

    :meth:`setPlayer` sets the player to be controlled by this widget.

    """

    def __init__(self, parent=None):
        super().__init__(parent)

        self._slider = ClickableSlider()
        self._playButton = QtWidgets.QPushButton()
        self._stopButton = QtWidgets.QPushButton()
        self._player = None
        self._pausedBySliderPress = False

        self._playButton.clicked.connect(self._onPlayButtonClick)
        self._stopButton.clicked.connect(self._onStopButtonClick)
        self._slider.sliderPressed.connect(self._onSliderPress)
        self._slider.sliderMoved.connect(self._onSliderMove)
        self._slider.sliderReleased.connect(self._onSliderRelease)

        layout = QtWidgets.QHBoxLayout()
        play_icon = self.style().standardIcon(
            QtWidgets.QStyle.StandardPixmap.SP_MediaPlay
        )
        self._playButton.setIcon(play_icon)
        layout.addWidget(self._playButton)
        stop_icon = self.style().standardIcon(
            QtWidgets.QStyle.StandardPixmap.SP_MediaStop
        )
        self._stopButton.setIcon(stop_icon)
        layout.addWidget(self._stopButton)
        self._slider.setOrientation(QtCore.Qt.Orientation.Horizontal)
        layout.addWidget(self._slider)
        self.setLayout(layout)

    def player(self) -> Optional[PlayerProtocol]:
        """Media player which is controlled by *self*."""
        return self._player

    @QtCore.Slot()
    def _onPlayButtonClick(self):
        """Play or pause :meth:`player`."""
        player = self.player()
        if player is not None:
            if (
                player.playbackState()
                == QtMultimedia.QMediaPlayer.PlaybackState.PlayingState
            ):
                player.pause()
            else:
                player.play()

    @QtCore.Slot()
    def _onStopButtonClick(self):
        """Stop :meth:`player`."""
        player = self.player()
        if player is not None:
            player.stop()

    @QtCore.Slot()
    def _onSliderPress(self):
        """If the media was playing, pause and move to the pressed position."""
        player = self.player()
        if player is not None:
            if (
                player.playbackState()
                == QtMultimedia.QMediaPlayer.PlaybackState.PlayingState
            ):
                self._pausedBySliderPress = True
                player.pause()
            player.setPosition(self._slider.value())

    @QtCore.Slot(int)
    def _onSliderMove(self, position: int):
        """Move the media to current slider position."""
        player = self.player()
        if player is not None:
            player.setPosition(position)

    @QtCore.Slot()
    def _onSliderRelease(self):
        """If the media was paused by slider press, play the media."""
        player = self.player()
        if player is not None and self._pausedBySliderPress:
            player.play()
            self._pausedBySliderPress = False

    def setPlayer(self, player: Optional[PlayerProtocol]):
        """Set :meth:`player` and connect the signals."""
        old_player = self.player()
        if old_player is not None:
            old_player.durationChanged.disconnect(  # type: ignore[attr-defined]
                self._onMediaDurationChange
            )
            old_player.positionChanged.disconnect(  # type: ignore[attr-defined]
                self._onMediaPositionChange
            )
            old_player.playbackStateChanged.disconnect(  # type: ignore[attr-defined]
                self._onPlaybackStateChange
            )
        self._player = player
        if player is not None:
            player.durationChanged.connect(  # type: ignore[attr-defined]
                self._onMediaDurationChange
            )
            player.positionChanged.connect(  # type: ignore[attr-defined]
                self._onMediaPositionChange
            )
            player.playbackStateChanged.connect(  # type: ignore[attr-defined]
                self._onPlaybackStateChange
            )

    @QtCore.Slot("qint64")
    def _onMediaDurationChange(self, duration: int):
        """Set the slider range to media duration."""
        self._slider.setRange(0, duration)

    @QtCore.Slot("qint64")
    def _onMediaPositionChange(self, position: int):
        """Update the slider position to video position."""
        self._slider.setValue(position)

    @QtCore.Slot(QtMultimedia.QMediaPlayer.PlaybackState)
    def _onPlaybackStateChange(self, state: QtMultimedia.QMediaPlayer.PlaybackState):
        """Switch the play icon and pause icon by *state*."""
        if state == QtMultimedia.QMediaPlayer.PlaybackState.PlayingState:
            pause_icon = self.style().standardIcon(
                QtWidgets.QStyle.StandardPixmap.SP_MediaPause
            )
            self._playButton.setIcon(pause_icon)
        else:
            play_icon = self.style().standardIcon(
                QtWidgets.QStyle.StandardPixmap.SP_MediaPlay
            )
            self._playButton.setIcon(play_icon)
