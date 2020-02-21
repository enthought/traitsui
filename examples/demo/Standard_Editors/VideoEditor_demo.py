#  Copyright (c) 2020, Enthought, Inc.
#  All rights reserved.

"""
VideoEditor


"""

from traits.api import Bool, Button, Float, HasTraits, Range, Str
from traitsui.api import ButtonEditor, Item, UItem, View, HGroup
from traitsui.editors.video_editor import VideoEditor, MediaStatus, PlayerState


class VideoEditorDemo(HasTraits):
    """Defines the main VideoEditor demo class."""

    #: The URL that holds the video data.
    video_url = Str()

    #: A button that
    play_pause_button = Button()

    button_label = Str('Play')

    state = PlayerState

    duration = Float

    position = Range(low=0.0, high='duration')

    error = Str

    status = MediaStatus

    buffer = Range(0, 100)

    muted = Bool(True)

    volume = Range(0.0, 100.0, value=100.0)

    playback_rate = Float(1.0)

    def _state_changed(self, new):
        if new == 'stopped' or new == 'paused':
            self.button_label = 'Play'
        elif new == 'playing':
            self.button_label = 'Pause'

    def _play_pause_button_changed(self):
        if self.state == 'stopped' or self.state == 'paused':
            self.state = 'playing'
        else:
            self.state = 'paused'

    # Demo view
    traits_view = View(
        UItem('video_url'),
        UItem(
            'video_url',
            editor=VideoEditor(
                state='state',
                position='position',
                duration='duration',
                video_error='error',
                media_status='status',
                buffer='buffer',
                muted='muted',
                volume='volume',
                playback_rate='playback_rate',
            ),
        ),
        HGroup(
            UItem(
                'play_pause_button',
                editor=ButtonEditor(label_value='button_label'),
                enabled_when='not bool(error)',
                width=100,
            ),
            UItem('position'),
        ),
        HGroup(
            Item('playback_rate'),
            Item('muted', label='Mute'),
            Item('volume'),
        ),
        HGroup(
            Item('state', style='readonly'),
            Item('status', style='readonly'),
            Item('buffer', style='readonly'),
            Item('error', visible_when="bool(error)", style='readonly'),
        ),
        title='VideoEditor',
        buttons=['OK'],
        width=800,
        height=600,
        resizable=True,
    )


# Create the demo:
demo = VideoEditorDemo()
demo.video_url = "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerEscapes.mp4"  # noqa: E501

# Run the demo (if invoked from the command line):
if __name__ == '__main__':
    demo.configure_traits()
