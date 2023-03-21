# (C) Copyright 2004-2023 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

"""Traits UI 'display only' video editor."""
from pyface.qt import is_qt5
from pyface.qt.QtCore import QPoint, Qt, QUrl, Signal
from pyface.qt.QtGui import QImage, QPainter, QPalette, QSizePolicy
from pyface.qt.QtMultimedia import (
    QAudio,
    QMediaPlayer,
    QVideoFrame,
)
from pyface.qt.QtMultimediaWidgets import QVideoWidget
from traits.api import (
    Any, Bool, Callable, Float, Instance, Range, Str, observe,
)
from traitsui.editors.video_editor import AspectRatio, MediaStatus, PlayerState

from .editor import Editor

#: Map from ApectRatio enum values to Qt aspect ratio behaviours.
aspect_ratio_map = {
    'ignore': Qt.AspectRatioMode.IgnoreAspectRatio,
    'keep': Qt.AspectRatioMode.KeepAspectRatio,
    'expand': Qt.AspectRatioMode.KeepAspectRatioByExpanding,
}

#: Map from PlayerState enum values to QMediaPlayer states.
if is_qt5:
    state_map = {
        'stopped': QMediaPlayer.State.StoppedState,
        'playing': QMediaPlayer.State.PlayingState,
        'paused': QMediaPlayer.State.PausedState,
    }
else:
    state_map = {
        'stopped': QMediaPlayer.PlaybackState.StoppedState,
        'playing': QMediaPlayer.PlaybackState.PlayingState,
        'paused': QMediaPlayer.PlaybackState.PausedState,
    }

#: Map from QMediaPlayer states to PlayerState enum values.
reversed_state_map = {value: key for key, value in state_map.items()}

#: Map from QMediaPlayer media status values to MediaStatus enum values.
media_status_map = {
    QMediaPlayer.MediaStatus.NoMedia: 'no_media',
    QMediaPlayer.MediaStatus.LoadingMedia: 'loading',
    QMediaPlayer.MediaStatus.LoadedMedia: 'loaded',
    QMediaPlayer.MediaStatus.StalledMedia: 'stalled',
    QMediaPlayer.MediaStatus.BufferingMedia: 'buffering',
    QMediaPlayer.MediaStatus.BufferedMedia: 'buffered',
    QMediaPlayer.MediaStatus.EndOfMedia: 'end',
    QMediaPlayer.MediaStatus.InvalidMedia: 'invalid',
}
if is_qt5:
    media_status_map[QMediaPlayer.MediaStatus.UnknownMediaStatus] = 'unknown'


if is_qt5:
    # These classes support dynamically modifying the video stream frames but
    # only work on Qt5
    from pyface.qt.QtMultimedia import QAbstractVideoSurface

    class ImageWidget(QVideoWidget):
        """Paints a QImage to the window body."""

        def __init__(self, parent=None, image_func=None):
            import numpy as np

            super().__init__(parent)
            self.image = QImage()
            self._np_image = np.zeros(shape=(0, 0, 4))
            self.painter = None
            self.resizeEvent(None)
            if image_func is None:
                # Don't bother with creating an ndarray version
                self.image_func = lambda image, bbox: image, self._np_image
            else:
                self.image_func = image_func

        def resizeEvent(self, event):
            s = self.size()
            self.width = s.width()
            self.height = s.height()

        def setImage(self, image):
            self.image, self._np_image = self.image_func(
                image, (self.width, self.height)
            )
            self.update()

        def paintEvent(self, event):
            super().paintEvent(event)
            if self.painter is None:
                self.painter = QPainter()
            self.painter.begin(self)
            if self.image:
                self.painter.drawImage(QPoint(0, 0), self.image)
            self.painter.end()

    class VideoSurface(QAbstractVideoSurface):

        frameAvailable = Signal(['QImage'])

        def __init__(self, widget=None):
            super().__init__()
            self.widget = widget

        def supportedPixelFormats(self, handleType):
            return [QVideoFrame.Format_RGB32]

        def present(self, frame):
            from pyface.qt.QtMultimedia import QAbstractVideoBuffer

            cloned_frame = QVideoFrame(frame)
            cloned_frame.map(QAbstractVideoBuffer.ReadOnly)
            image = QImage(
                cloned_frame.bits(),
                cloned_frame.width(),
                cloned_frame.height(),
                cloned_frame.bytesPerLine(),
                QVideoFrame.imageFormatFromPixelFormat(
                    cloned_frame.pixelFormat()
                ),
            )
            self.frameAvailable.emit(image)
            return True


class VideoEditor(Editor):
    """Traits UI 'display only' video editor.

    This editor uses the Qt QMultimedia machinery to display video streams
    to the screen.  Rather than being self-contained, the editor only concerns
    itself with displaying the video, and provides traits that control
    behaviour and provide internal state of the control during playback.
    """

    #: Does the drawing onto the image plane
    control = Instance(QVideoWidget)

    #: Handles the image pulling so the frames can be processed.  Qt5 only.
    surface = Any()

    #: The QMediaObject (Qt5) or QUrl (Qt6+) that holds the connection to the
    #: video stream.
    media_content = Any()

    #: The QMediaPlayer that controls playback of the video stream.
    media_player = Instance(QMediaPlayer)

    #: The aspect ratio of the video editor.
    aspect_ratio = AspectRatio()

    #: The current state of the player, synchronized to the trait named
    #: by factory.state.
    state = PlayerState()

    #: The current playback position of the player, synchronized to the trait
    #: named by factory.position.
    position = Float()

    #: The total duration of the current video, synchronized to the trait
    #: named by factory.duration.
    duration = Float()

    #: The media player playback status (loading, buffering, etc.),
    #: synchronized to the trait named by factory.media_status.
    media_status = MediaStatus()

    #: The percentage of the buffer currently filled, synchronized to the trait
    #: named by factory.buffer.
    buffer = Range(0, 100)

    #: A string holding the video error state, or "" if no error. Synchronized
    #: to the trait named by factory.video_error.
    video_error = Str()

    #: Whether the audio is muted or not, synchronized to the trait named by
    #: factory.muted.
    muted = Bool(False)

    #: The playback volume on a logarithmic scale (perceptually linear),
    #: synchronized to the trait named by factory.volume.
    volume = Range(0.0, 100.0)

    #: The playback rate.  Negative values rewind the video.
    #: Synchronized to the trait named by factory.playback_rate.
    playback_rate = Float(1.0)

    #: Function to apply to the image. Takes ref to new frame and a size tuple.
    #: Synchronized to the trait named by factory.image_func.
    image_func = Callable()

    #: The change in position required for an update to be emitted.
    #: Synchronized to the trait named by factory.notify_interval.
    #: This is only used on Qt5.
    notify_interval = Float(1.0)

    #: Qt6-specific QAudioOutput handler.
    _audio = Any()

    def update_to_regular(self):
        if self.surface is not None:
            self.surface.frameAvailable.disconnect(self.control.setImage)
            self.surface = None

        self.control = QVideoWidget()
        self.control.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
        )
        self.control.setBackgroundRole(QPalette.ColorRole.Window)
        self.media_player.setVideoOutput(self.control)

    def update_to_functional(self):
        self.control = ImageWidget(image_func=self.image_func)
        self.control.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
        )
        self.control.setBackgroundRole(QPalette.ColorRole.Window)

        self.surface = VideoSurface(widget=self.control)
        self.surface.frameAvailable.connect(self.control.setImage)

        self.media_player.setVideoOutput(self.surface)

    # ------------------------------------------------------------------------
    # Editor interface
    # ------------------------------------------------------------------------

    def init(self, parent):
        """Initialize the editor by creating the underlying toolkit widget.

        Parameters
        ----------
        parent : QWidget or None
            The parent widget for this widget.
        """
        self.control = QVideoWidget()
        self.control.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
        )
        self.control.setBackgroundRole(QPalette.ColorRole.Window)

        if is_qt5:
            self.media_player = QMediaPlayer(None, QMediaPlayer.VideoSurface)
        else:
            self.media_player = QMediaPlayer()
        self._set_video_url()
        self.media_player.setVideoOutput(self.control)
        if is_qt5:
            self.media_player.setMuted(self.muted)
        else:
            from pyface.qt.QtMultimedia import QAudioOutput

            self._audio = QAudioOutput()
            self._audio.setMuted(self.muted)
            self.media_player.setAudioOutput(self._audio)
        self._update_state()
        self._update_aspect_ratio()
        self._update_muted()
        self._update_volume()
        self._update_playback_rate()
        self._update_notify_interval()

        self._connect_signals()

        self.set_tooltip()

    def dispose(self):
        self._disconnect_signals()
        if self.media_player is not None:
            # Avoid a segfault if the media player is currently playing
            self.media_player.setVideoOutput(None)
            if not is_qt5:
                self.media_player.setAudioOutput(None)

        super().dispose()

    def update_editor(self):
        """Update the editor when the object trait changes externally."""
        self._set_video_url()

    # ------------------------------------------------------------------------
    # Private interface
    # ------------------------------------------------------------------------

    def _connect_signals(self):
        if self.media_player is not None:
            if is_qt5:
                self.media_player.stateChanged.connect(
                    self._state_changed_emitted
                )
                self.media_player.error.connect(self._error_emitted)
                self.media_player.bufferStatusChanged.connect(
                    self._buffer_status_changed_emitted
                )
                self.media_player.notifyIntervalChanged.connect(
                    self._notify_interval_changed_emitted
                )
            else:
                self.media_player.playbackStateChanged.connect(
                    self._state_changed_emitted
                )
                self.media_player.errorOccurred.connect(self._error_emitted)
                self.media_player.bufferProgressChanged.connect(
                    self._buffer_status_changed_emitted
                )
            self.media_player.positionChanged.connect(
                self._position_changed_emitted
            )
            self.media_player.durationChanged.connect(
                self._duration_changed_emitted
            )
            self.media_player.mediaStatusChanged.connect(
                self._media_status_changed_emitted
            )

    def _disconnect_signals(self):
        if self.media_player is not None:
            if is_qt5:
                self.media_player.stateChanged.disconnect(
                    self._state_changed_emitted
                )
                self.media_player.error.disconnect(self._error_emitted)
                self.media_player.bufferStatusChanged.disconnect(
                    self._buffer_status_changed_emitted
                )
                self.media_player.notifyIntervalChanged.disconnect(
                    self._notify_interval_changed_emitted
                )
            else:
                self.media_player.playbackStateChanged.disconnect(
                    self._state_changed_emitted
                )
                self.media_player.errorOccurred.disconnect(self._error_emitted)
                self.media_player.bufferProgressChanged.disconnect(
                    self._buffer_status_changed_emitted
                )
            self.media_player.positionChanged.disconnect(
                self._position_changed_emitted
            )
            self.media_player.durationChanged.disconnect(
                self._duration_changed_emitted
            )
            self.media_player.mediaStatusChanged.disconnect(
                self._media_status_changed_emitted
            )

    def _set_video_url(self):
        qurl = QUrl.fromUserInput(self.value)
        if is_qt5:
            from pyface.qt.QtMultimedia import QMediaContent
            if qurl.isValid():
                self.media_content = QMediaContent(qurl)
            else:
                self.media_content = QMediaContent(None)
        else:
            self.media_content = qurl
        self.control.updateGeometry()

    # Signal handlers -------------------------------------------------------

    def _state_changed_emitted(self, state):
        self.state = reversed_state_map[state]

    def _position_changed_emitted(self, position):
        # Avoid telling Qt about the new position in `_position_changed`
        with self.updating_value():
            self.position = position / 1000.0

    def _duration_changed_emitted(self, duration):
        self.duration = duration / 1000.0

    def _error_emitted(self, error):
        if error != QMediaPlayer.Error.NoError:
            self.video_error = self.media_player.errorString()
        else:
            self.video_error = ''

    def _media_status_changed_emitted(self, error):
        self.media_status = media_status_map[self.media_player.mediaStatus()]

    def _buffer_status_changed_emitted(self, error):
        if is_qt5:
            self.buffer = self.media_player.bufferStatus()
        else:
            self.buffer = int(self.media_player.bufferProgress() * 100)

    def _notify_interval_changed_emitted(self, interval):
        self.notify_interval = interval / 1000.0

    # Trait change handlers -------------------------------------------------

    @observe('aspect_ratio')
    def _aspect_ratio_observer(self, event):
        if self.control is not None:
            self._update_aspect_ratio()

    @observe('image_func')
    def _image_func_observer(self, event):
        if self.image_func is None:
            self.update_to_regular()
        elif not is_qt5:
            raise ValueError("image_func is not supported on Qt6")
        else:
            self.update_to_functional()

    @observe('media_content')
    def _media_content_observer(self, event):
        self.video_error = ''
        if self.media_player is not None:
            if is_qt5:
                self.media_player.setMedia(self.media_content)
            else:
                self.media_player.setSource(self.media_content)

    @observe('muted')
    def _muted_observer(self, event):
        if self.media_player is not None:
            self._update_muted()

    @observe('playback_rate')
    def _playback_rate_observer(self, event):
        if self.media_player is not None:
            self._update_playback_rate()

    @observe('position')
    def _position_observer(self, event):
        if self.media_player is not None and not self.updating:
            # position is given in ms
            self.media_player.setPosition(int(self.position * 1000))

    @observe('state')
    def _state_observer(self, event):
        if self.media_player is not None:
            self._update_state()

    @observe('volume')
    def _volume_observer(self, event):
        if self.media_player is not None:
            self._update_volume()

    @observe('notify_interval')
    def _notify_interval_observer(self, event):
        if self.media_player is not None:
            self._update_notify_interval()

    # MediaPlayer management ------------------------------------------------

    def _update_aspect_ratio(self):
        self.control.setAspectRatioMode(aspect_ratio_map[self.aspect_ratio])

    def _update_muted(self):
        if is_qt5:
            self.media_player.setMuted(self.muted)
        else:
            self._audio.setMuted(self.muted)

    def _update_playback_rate(self):
        self.media_player.setPlaybackRate(self.playback_rate)

    def _update_state(self):
        if self.state == 'stopped':
            self.media_player.stop()
            self.control.repaint()
        elif self.state == 'playing':
            # XXX forcing a resize so video is scaled correctly on MacOS
            s = self.control.size()
            w = s.width()
            h = s.height()
            self.media_player.play()
            self.control.resize(w + 1, h + 1)
            self.control.resize(w, h)
        elif self.state == 'paused':
            self.media_player.pause()

    def _update_volume(self):
        linear_volume = QAudio.convertVolume(
            self.volume / 100.0,
            QAudio.VolumeScale.LogarithmicVolumeScale,
            QAudio.VolumeScale.LinearVolumeScale,
        )
        if is_qt5:
            self.media_player.setVolume(int(linear_volume * 100))
        else:
            self._audio.setVolume(linear_volume)

    def _update_notify_interval(self):
        # only used on Qt5
        if is_qt5:
            # interval is given in ms
            interval = int(self.notify_interval * 1000)
            self.media_player.setNotifyInterval(interval)
