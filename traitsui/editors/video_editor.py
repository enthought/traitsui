#  Copyright (c) 2020, Enthought, Inc.
#  All rights reserved.
#
#  This software is provided without warranty under the terms of the BSD
#  license included in LICENSE.txt and may be redistributed only
#  under the conditions described in the aforementioned license.  The license
#  is also available online at http://www.enthought.com/licenses/BSD.txt

"""Traits UI 'display only' video editor."""


from __future__ import absolute_import

from traits.api import Enum, Property, Str

from ..basic_editor_factory import BasicEditorFactory
from ..toolkit import toolkit_object


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
    aspect_ratio = AspectRatio

    #: The name of a trait to synchronise with the audio muted state of
    #: the video.  The referenced trait should be a Bool.
    muted = Str(sync_value='from', sync_name='muted')

    #: The name of a trait to synchronise with the audio volume of
    #: the video player.  The referenced trait should be a Range(0.0, 100.0).
    #: Values are on a logarithmic scale.
    volume = Str(sync_value='from', sync_name='volume')

    #: The name of a trait to synchronise with the audio muted state of
    #: the video.  The referenced trait should be a Float.
    playback_rate = Str(sync_value='from', sync_name='playback_rate')

    #: The name of a trait to synchronise with the player's state.
    #: The referenced trait should be a PlayerState.
    state = Str(sync_value='both', sync_name='state')

    #: The name of a trait to synchronise with the player's position.
    #: The referenced trait should be a Float representing time in seconds.
    position = Str(sync_value='both', sync_name='position')

    #: The name of a trait to synchronise with the player's duration.
    #: The referenced trait should be a Float representing time in seconds.
    duration = Str(sync_value='to', sync_name='duration')

    #: The name of a trait to synchronise with the player's media status.
    #: The referenced trait should be a Str.
    media_status = Str(sync_value='to', sync_name='media_status')

    #: The name of a trait to synchronise with the player's buffer status.
    #: The referenced trait should be an Range(0, 100).
    buffer = Str(sync_value='to', sync_name='buffer')

    #: The name of a trait to synchronise with the player's error state.
    #: The referenced trait should be a Str.
    video_error = Str(sync_value='to', sync_name='video_error')

    def _get_klass(self):
        """ Returns the editor class to be instantiated.
        """
        return toolkit_object("video_editor:VideoEditor")
