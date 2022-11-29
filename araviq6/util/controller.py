"""
Media controller
================

"""

from araviq6.qt_compat import QtCore, QtGui, QtMultimedia, QtWidgets
from typing import Optional


__all__ = [
    "ClickableSlider",
    "MediaController",
]


class ClickableSlider(QtWidgets.QSlider):
    """``QSlider`` whose groove can be clicked to move to position."""

    # https://stackoverflow.com/questions/52689047
    def mousePressEvent(self, event: QtGui.QMouseEvent):
        if event.button() == QtCore.Qt.LeftButton:
            val = self.pixelPosToRangeValue(event.position())
            self.setValue(val)
        super().mousePressEvent(event)

    def pixelPosToRangeValue(self, pos: QtCore.QPointF) -> int:
        opt = QtWidgets.QStyleOptionSlider()
        self.initStyleOption(opt)
        gr = self.style().subControlRect(
            QtWidgets.QStyle.CC_Slider, opt, QtWidgets.QStyle.SC_SliderGroove, self
        )
        sr = self.style().subControlRect(
            QtWidgets.QStyle.CC_Slider, opt, QtWidgets.QStyle.SC_SliderHandle, self
        )

        if self.orientation() == QtCore.Qt.Horizontal:
            sliderLength = sr.width()
            sliderMin = gr.x()
            sliderMax = gr.right() - sliderLength + 1
        else:
            sliderLength = sr.height()
            sliderMin = gr.y()
            sliderMax = gr.bottom() - sliderLength + 1
        pr = pos - sr.center() + sr.topLeft()
        p = pr.x() if self.orientation() == QtCore.Qt.Horizontal else pr.y()
        return QtWidgets.QStyle.sliderValueFromPosition(
            self.minimum(),
            self.maximum(),
            int(p - sliderMin),
            sliderMax - sliderMin,
            opt.upsideDown,  # type: ignore[attr-defined]
        )


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

        self.playButton().clicked.connect(self.onPlayButtonClicked)
        self.stopButton().clicked.connect(self.onStopButtonClicked)
        self.slider().sliderPressed.connect(self.onSliderPress)
        self.slider().sliderMoved.connect(self.onSliderMove)
        self.slider().sliderReleased.connect(self.onSliderRelease)

        layout = QtWidgets.QHBoxLayout()
        play_icon = self.style().standardIcon(QtWidgets.QStyle.SP_MediaPlay)
        self.playButton().setIcon(play_icon)
        layout.addWidget(self.playButton())
        stop_icon = self.style().standardIcon(QtWidgets.QStyle.SP_MediaStop)
        self.stopButton().setIcon(stop_icon)
        layout.addWidget(self.stopButton())
        self.slider().setOrientation(QtCore.Qt.Horizontal)
        layout.addWidget(self.slider())
        self.setLayout(layout)

    def slider(self) -> ClickableSlider:
        """Slider to change the media position."""
        return self._slider

    def playButton(self) -> QtWidgets.QPushButton:
        """Button to play and pause the media."""
        return self._playButton

    def stopButton(self) -> QtWidgets.QPushButton:
        """Button to stop the media."""
        return self._stopButton

    def player(self) -> Optional[QtMultimedia.QMediaPlayer]:
        """Media player which is controlled by *self*."""
        return self._player

    @QtCore.Slot()
    def onPlayButtonClicked(self):
        """Play or pause :meth:`player`."""
        player = self.player()
        if player is not None:
            if player.playbackState() == player.PlaybackState.PlayingState:
                player.pause()
            else:
                player.play()

    @QtCore.Slot()
    def onStopButtonClicked(self):
        """Stop :meth:`player`."""
        player = self.player()
        if player is not None:
            player.stop()

    @QtCore.Slot()
    def onSliderPress(self):
        """If the media was playing, pause and move to the pressed position."""
        player = self.player()
        if player is not None:
            if player.playbackState() == player.PlaybackState.PlayingState:
                self._pausedBySliderPress = True
                player.pause()
            player.setPosition(self.slider().value())

    @QtCore.Slot(int)
    def onSliderMove(self, position: int):
        """Move the media to current slider position."""
        player = self.player()
        if player is not None:
            player.setPosition(position)

    @QtCore.Slot()
    def onSliderRelease(self):
        """If the media was paused by slider press, play the media."""
        player = self.player()
        if player is not None and self._pausedBySliderPress:
            player.play()
            self._pausedBySliderPress = False

    def setPlayer(self, player: Optional[QtMultimedia.QMediaPlayer]):
        """Set :meth:`player` and connect the signals."""
        old_player = self.player()
        if old_player is not None:
            self.disconnectPlayer(old_player)
        self._player = player
        if player is not None:
            self.connectPlayer(player)

    def connectPlayer(self, player: QtMultimedia.QMediaPlayer):
        """Connect signals and slots with *player*."""
        player.durationChanged.connect(  # type: ignore[attr-defined]
            self.onMediaDurationChange
        )
        player.positionChanged.connect(  # type: ignore[attr-defined]
            self.onMediaPositionChange
        )
        player.playbackStateChanged.connect(  # type: ignore[attr-defined]
            self.onPlaybackStateChange
        )

    def disconnectPlayer(self, player: QtMultimedia.QMediaPlayer):
        """Disconnect signals and slots with *player*."""
        player.durationChanged.disconnect(  # type: ignore[attr-defined]
            self.onMediaDurationChange
        )
        player.positionChanged.disconnect(  # type: ignore[attr-defined]
            self.onMediaPositionChange
        )
        player.playbackStateChanged.disconnect(  # type: ignore[attr-defined]
            self.onPlaybackStateChange
        )

    @QtCore.Slot(int)
    def onMediaDurationChange(self, duration: int):
        """Set the slider range to media duration."""
        self.slider().setRange(0, duration)

    @QtCore.Slot(int)
    def onMediaPositionChange(self, position: int):
        """Update the slider position to video position."""
        self.slider().setValue(position)

    @QtCore.Slot(QtMultimedia.QMediaPlayer.PlaybackState)
    def onPlaybackStateChange(self, state: QtMultimedia.QMediaPlayer.PlaybackState):
        """Switch the play icon and pause icon by *state*."""
        if state == QtMultimedia.QMediaPlayer.PlaybackState.PlayingState:
            pause_icon = self.style().standardIcon(QtWidgets.QStyle.SP_MediaPause)
            self.playButton().setIcon(pause_icon)
        else:
            play_icon = self.style().standardIcon(QtWidgets.QStyle.SP_MediaPlay)
            self.playButton().setIcon(play_icon)
