# (C) Copyright 2004-2021 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

"""Traits UI 'display only' video editor."""

from traits.api import Bool, Callable, Enum, Float, Property, Range, Str

from traitsui.basic_editor_factory import BasicEditorFactory
from traitsui.toolkit import toolkit_object

AspectRatio = Enum('keep', 'ignore', 'expand')
PlayerState = Enum('stopped', 'playing', 'paused')
MediaStatus = Enum(
    'unknown', 'no_media', 'loading', 'loaded', 'stalled', 'buffering',
    'buffered', 'end', 'invalid',
)


class VideoEditor(BasicEditorFactory):
    """Traits UI 'display only' video editor.

    This editor only displays the video stream, and does not attempt to
    provide UI elements for controlling playback.  It does provide a
    rich set of trait references that can be synchronised with the internal
    state of the video player.
    """

    #: The editor class to be created:
    klass = Property()

    #: The behaviour of the video display when the widget aspect ratio
    #: doesn't match the aspect ratio of the video stream.
    aspect_ratio = AspectRatio()

    #: The name of a trait to synchronise with the audio muted state of
    #: the video.
    muted_name = Str()
    #: True if the audio is muted, False otherwise
    muted = Bool(sync_value='from', sync_name='muted_name')

    #: The name of a trait to synchronise with the audio volume of
    #: the video player.
    volume_name = Str()
    #: Audio volume on a logarithmic scale
    volume = Range(0.0, 100.0, 50.0,
                   sync_value='from', sync_name='volume_name')

    #: The name of a trait to synchronise with the playback rate of
    #: the video.
    playback_rate_name = Str()
    #: The playback speed of the video. Negative values are allowed but may not
    #: be supported by the underlying implementation.
    playback_rate = Float(sync_value='from', sync_name='playback_rate_name')

    #: The name of a trait to synchronise with the player's state.
    state_name = Str()
    #: The state (stopped, playing, paused) of the player
    state = PlayerState(sync_value='both', sync_name='state_name')

    #: The name of a trait to synchronise with the player's position.
    position_name = Str()
    #: The current position, in seconds, in the video.
    position = Float(sync_value='both', sync_name='position_name')

    #: The name of a trait to synchronise with the player's duration.
    duration_name = Str()
    #: Duration of the loaded video in seconds
    duration = Float(sync_value='to', sync_name='duration_name')

    #: The name of a trait to synchronise with the player's media status.
    media_status_name = Str()
    #: The status of the loaded video (see ``MediaStatus``)
    media_status = MediaStatus(sync_value='to', sync_name='media_status_name')

    #: The name of a trait to synchronise with the player's buffer status.
    buffer_name = Str()
    #: An integer percentage representing how much of the player's buffer
    #: is filled.
    buffer = Range(0, 100, sync_value='to', sync_name='buffer_name')

    #: The name of a trait to synchronise with the player's error state.
    video_error_name = Str()
    #: A string describing an error encountered by the player
    video_error = Str(sync_value='to', sync_name='video_error_name')

    #: The name of a trait to synchronise with the player's image function.
    image_func_name = Str()
    #: Callable to apply to video frames. Takes ref to new frame and a size
    #: tuple. Must return a QImage and a numpy array.
    image_func = Callable(sync_value='both', sync_name='image_func_name')

    #: The name of a trait to synchronise with the player's notify interval.
    #: The referenced trait should be a Float representing time in seconds.
    notify_interval = Str(sync_value='from', sync_name='notify_interval')

    def _get_klass(self):
        """ Returns the editor class to be instantiated.
        """
        return toolkit_object('video_editor:VideoEditor')
