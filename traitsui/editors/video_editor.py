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

from traits.api import Bool, Callable, Enum, Float, Instance, Property, Range

from traitsui.context_value import ContextValue, CVType
from traitsui.basic_editor_factory import BasicEditorFactory
from traitsui.toolkit import toolkit_object

AspectRatio = Enum('keep', 'ignore', 'expand')
PlayerState = Enum('stopped', 'playing', 'paused')
MediaStatus = Enum(
    'unknown',
    'no_media',
    'loading',
    'loaded',
    'stalled',
    'buffering',
    'buffered',
    'end',
    'invalid',
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

    #: True if the audio is muted, False otherwise
    muted = CVType(Bool, default_value=False, sync_value='from')

    #: Audio volume on a logarithmic scale
    volume = CVType(Range(0.0, 100.0), default_value=75.0, sync_value='from')

    #: The playback speed of the video. Negative values are allowed but may not
    #: be supported by the underlying implementation.
    playback_rate = CVType(Float, default_value=1.0, sync_value='from')

    #: The state (stopped, playing, paused) of the player
    state = CVType(PlayerState, default_value='stopped', sync_value='both')

    #: The current position, in seconds, in the video.
    position = CVType(Float, default_value=0.0, sync_value='both')

    #: Duration of the loaded video in seconds
    duration = Instance(
        ContextValue, args=('',), allow_none=False, sync_value='to'
    )

    #: The status of the loaded video (see ``MediaStatus``)
    media_status = Instance(
        ContextValue, args=('',), allow_none=False, sync_value='to'
    )

    #: An integer percentage representing how much of the player's buffer
    #: is filled.
    buffer = Instance(
        ContextValue, args=('',), allow_none=False, sync_value='to'
    )

    #: A string describing an error encountered by the player
    video_error = Instance(
        ContextValue, args=('',), allow_none=False, sync_value='to'
    )

    #: Callable to apply to video frames. Takes ref to new frame and a size
    #: tuple. Must return a QImage and a numpy array.
    image_func = CVType(Callable, sync_value='from')

    #: The name of a trait to synchronise with the player's notify interval.
    #: The referenced trait should be a Float representing time in seconds.
    notify_interval = CVType(Float, default_value=1.0, sync_value='from')

    def _get_klass(self):
        """Returns the editor class to be instantiated."""
        return toolkit_object('video_editor:VideoEditor')
