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

from traits.api import Bool, Callable, Enum, Float, Instance, Property, Range

from traitsui.basic_editor_factory import BasicEditorFactory
from traitsui.context_value import CVType, ContextValue
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

    #: The default audio muted state of the video player or a ContextValue
    #: reference to a trait that will synchronize to the muted state.
    muted = CVType(Bool, sync_value='from')

    #: The default audio volume of the video player or a ContextValue
    #: reference to a trait that will synchronize to the volume.
    #: Values are on a logarithmic scale.
    volume = CVType(Range(0.0, 100.0), sync_value='from')

    #: The default playback rate of the video player or a ContextValue
    #: reference to a trait that will synchronize to the playback rate.
    playback_rate = CVType(Float, sync_value='from')

    #: The initial player state of the video player or a ContextValue
    #: reference to a trait that will synchronize to the player state.
    state = CVType(PlayerState, sync_value='both')

    #: The initial playback position of the video player or a ContextValue
    #: reference to a trait that will synchronize to the playback position.
    #: The value is a floating point time in seconds.
    position = CVType(Float, sync_value='both')

    #: A ContextValue reference to a trait that will synchronize to the
    #: duration of the video.  The value is a floating point time in
    #: seconds.
    duration = Instance(ContextValue, args=(), allow_none=False,
                        sync_value='to')

    #: A ContextValue reference to a trait that will synchronize to the
    #: media status of the player.  The value is a valid MediaStatus string.
    media_status = Instance(ContextValue, args=(), allow_none=False,
                            sync_value='to')

    #: A ContextValue reference to a trait that will synchronize to the
    #: buffering percentage of the playe.  The value is a number from 0 to
    #: 100.
    buffer = Instance(ContextValue, args=(), allow_none=False, sync_value='to')

    #: A ContextValue reference to a trait that will synchronize to the
    #: media status of the player.  The value is a string.
    video_error = Instance(ContextValue, args=(), allow_none=False, sync_value='to')

    #: The default image transformation function to apply to each frame in
    #: the video, ContextValue reference to a trait that will synchronize to
    #: the image transformation function, or None if no transformation is
    #: needed.
    image_func = CVType(Callable, sync_value='both')

    #: The default notification interval of the video player or a ContextValue
    #: reference to a trait that will synchronize to the notification
    #: interval. The value is a floating point time in seconds.
    notify_interval = CVType(Float, sync_value='from')

    def _get_klass(self):
        """ Returns the editor class to be instantiated.
        """
        return toolkit_object('video_editor:VideoEditor')
