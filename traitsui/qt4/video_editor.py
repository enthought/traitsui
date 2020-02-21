#  Copyright (c) 2020, Enthought, Inc.
#  All rights reserved.
#
#  This software is provided without warranty under the terms of the BSD
#  license included in LICENSE.txt and may be redistributed only
#  under the conditions described in the aforementioned license.  The license
#  is also available online at http://www.enthought.com/licenses/BSD.txt

"""Traits UI 'display only' video editor."""


from __future__ import absolute_import

from pyface.qt.QtCore import Qt, QUrl
from pyface.qt.QtGui import QPalette, QSizePolicy
from pyface.qt.QtMultimedia import QAudio, QMediaContent, QMediaPlayer
from pyface.qt.QtMultimediaWidgets import QVideoWidget
from traits.api import Bool, Float, Instance, Range, Str

from traitsui.editors.video_editor import AspectRatio, MediaStatus, PlayerState
from .editor import Editor


#: Map from ApectRatio enum values to Qt aspect ratio behaviours.
aspect_ratio_map = {
    'ignore': Qt.IgnoreAspectRatio,
    'keep': Qt.KeepAspectRatio,
    'expand': Qt.KeepAspectRatioByExpanding,
}

#: Map from PlayerState enum values to QMediaPlayer states.
state_map = {
    'stopped': QMediaPlayer.StoppedState,
    'playing': QMediaPlayer.PlayingState,
    'paused': QMediaPlayer.PausedState,
}

#: Map from QMediaPlayer states to PlayerState enum values.
reversed_state_map = {value: key for key, value in state_map.items()}

#: Map from QMediaPlayer media status values to MediaStatus enum values.
media_status_map = {
    QMediaPlayer.UnknownMediaStatus: 'unknown',
    QMediaPlayer.NoMedia: 'no_media',
    QMediaPlayer.LoadingMedia: 'loading',
    QMediaPlayer.LoadedMedia: 'loaded',
    QMediaPlayer.StalledMedia: 'stalled',
    QMediaPlayer.BufferingMedia: 'buffering',
    QMediaPlayer.BufferedMedia: 'buffered',
    QMediaPlayer.EndOfMedia: 'end',
    QMediaPlayer.InvalidMedia: 'invalid',
}


class VideoEditor(Editor):
    """Traits UI 'display only' video editor.

    This editor uses the Qt QMultimedia machinery to display video streams
    to the screen.  Rather than being self-contained, the editor only concerns
    itself with displaying the video, and provides traits that control
    behaviour and provide internal state of the control during playback.
    """

    control = Instance(QVideoWidget)

    #: The QMediaObject that holds the connection to the video stream.
    media_content = Instance(QMediaContent)

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

    #: The media player playback status (loading, buffering, etc.).
    media_status = MediaStatus()

    #: The percentage of the buffer currently filled.
    buffer = Range(0, 100)

    #: A string holding the video error state, or "" if no error.
    video_error = Str()

    #: Whether the audio is muted or not.
    muted = Bool(False)

    #: The playback volume on a logarithmic scale (perceptually linear).
    volume = Range(0.0, 100.0)

    #: The playback rate.  Negative values rewind the video.
    playback_rate = Float(1.0)

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
            QSizePolicy.Expanding, QSizePolicy.Expanding
        )
        self.control.setBackgroundRole(QPalette.Window)

        self.media_player = QMediaPlayer(None, QMediaPlayer.VideoSurface)
        self._set_video_url()
        self.media_player.setVideoOutput(self.control)
        self.media_player.setMuted(self.muted)
        self._state_changed()
        self._aspect_ratio_changed()
        self._muted_changed()
        self._volume_changed()
        self._playback_rate_changed()

        self._connect_signals()

        self.set_tooltip()

    def dispose(self):
        self._disconnect_signals()

    def update_editor(self):
        """Update the editor when the object trait changes externally."""
        self._set_video_url()

    # ------------------------------------------------------------------------
    # Private interface
    # ------------------------------------------------------------------------

    def _connect_signals(self):
        if self.media_player is not None:
            self.media_player.stateChanged.connect(self._state_changed_emitted)
            self.media_player.positionChanged.connect(
                self._position_changed_emitted)
            self.media_player.durationChanged.connect(
                self._duration_changed_emitted)
            self.media_player.error.connect(self._error_emitted)
            self.media_player.mediaStatusChanged.connect(
                self._media_status_changed_emitted)
            self.media_player.bufferStatusChanged.connect(
                self._buffer_status_changed_emitted)

    def _disconnect_signals(self):
        if self.media_player is not None:
            self.media_player.stateChanged.disconnect(
                self._state_changed_emitted)
            self.media_player.positionChanged.disconnect(
                self._position_changed_emitted)
            self.media_player.durationChanged.disconnect(
                self._duration_changed_emitted)
            self.media_player.error.disconnect(self._error_emitted)
            self.media_player.mediaStatusChanged.disconnect(
                self._media_status_changed_emitted)
            self.media_player.bufferStatusChanged.disconnect(
                self._buffer_status_changed_emitted)

    def _set_video_url(self):
        qurl = QUrl.fromUserInput(self.value)
        if qurl.isValid():
            self.media_content = QMediaContent(qurl)
            self.control.updateGeometry()
        else:
            self.media_content = QMediaContent(None)
            self.control.updateGeometry()

    # Signal handlers -------------------------------------------------------

    def _state_changed_emitted(self, state):
        self.state = reversed_state_map[state]

    def _position_changed_emitted(self, position):
        self.position = position / 1000.0

    def _duration_changed_emitted(self, duration):
        self.duration = duration / 1000.0

    def _error_emitted(self, error):
        if error != QMediaPlayer.NoError:
            self.video_error = self.media_player.errorString()
        else:
            self.video_error = ''

    def _media_status_changed_emitted(self, error):
        self.media_status = media_status_map[self.media_player.mediaStatus()]

    def _buffer_status_changed_emitted(self, error):
        self.buffer = self.media_player.bufferStatus()

    # Trait change handlers -------------------------------------------------

    def _media_content_changed(self):
        self.video_error = ''
        if self.media_player is not None:
            self.media_player.setMedia(self.media_content)

    def _aspect_ratio_changed(self):
        if self.control is not None:
            self.control.setAspectRatioMode(
                aspect_ratio_map[self.aspect_ratio]
            )

    def _state_changed(self):
        if self.media_player is not None:
            if self.state == 'stopped':
                self.media_player.stop()
                self.control.repaint()
            elif self.state == 'playing':
                # XXX forcing a resize so video is scaled correctly on MacOS
                s = self.control.size()
                w = s.width()
                h = s.height()
                self.media_player.play()
                self.control.resize(w+1, h+1)
                self.control.resize(w, h)
            elif self.state == 'paused':
                self.media_player.pause()

    def _position_changed(self):
        if self.media_player is not None:
            # position is given in ms
            self.media_player.setPosition(int(self.position * 1000))

    def _muted_changed(self):
        if self.media_player is not None:
            self.media_player.setMuted(self.muted)

    def _volume_changed(self):
        if self.media_player is not None:
            linear_volume = QAudio.convertVolume(
                self.volume/100.0,
                QAudio.LogarithmicVolumeScale,
                QAudio.LinearVolumeScale,
            )
            self.media_player.setVolume(int(linear_volume * 100))

    def _playback_rate_changed(self):
        if self.media_player is not None:
            self.media_player.setPlaybackRate(self.playback_rate)
