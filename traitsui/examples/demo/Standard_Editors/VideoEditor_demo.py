# (C) Copyright 2004-2021 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

"""
VideoEditor

Demonstrates a 'display only' video editor for Qt5+

"""
import numpy as np
from PIL import Image
from pyface.qt.QtGui import QImage
from traits.api import Bool, Button, Callable, Float, HasTraits, Range, Str
from traitsui.api import ButtonEditor, HGroup, Item, UItem, View
from traitsui.editors.video_editor import MediaStatus, PlayerState, VideoEditor


def QImage_from_np(image):
    assert (np.max(image) <= 255)
    image8 = image.astype(np.uint8, order='C', casting='unsafe')
    height, width, colors = image8.shape
    bytesPerLine = 4 * width

    image = QImage(image8.data, width, height, bytesPerLine,
                   QImage.Format_RGB32)
    return image


def np_from_QImage(qimage):
    # Creates a numpy array from a pyqt(5) QImage object
    width, height = qimage.width(), qimage.height()
    channels = qimage.pixelFormat().channelCount()
    return np.array(
        qimage.bits().asarray(width * height * channels)
    ).reshape(height, width, channels).astype('u1')


def qimage_function(antialiasing=True):
    def antialis_fun(image_fun):
        """
        Turns a image funciton into a QImage function,
        bound within the viewing frames box.
        """
        def qimage_conv_fun(image, box_dims):
            _np_image = image_fun(np_from_QImage(image))
            pil_image = Image.fromarray(_np_image)
            if antialiasing:
                pil_image.thumbnail(box_dims, Image.ANTIALIAS)
            else:
                pil_image.thumbnail(box_dims)
            _np_image = np.array(pil_image)
            image = QImage_from_np(_np_image)
            return image, _np_image
        return qimage_conv_fun
    return antialis_fun


@qimage_function(antialiasing=False)
def test_image_fun(image):
    return image.transpose(1, 0, 2)


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

    image_fun = Callable()

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
                image_fun='image_fun'
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
demo = VideoEditorDemo(image_fun=test_image_fun)
# demo = VideoEditorDemo()
demo.video_url = "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerEscapes.mp4"  # noqa: E501

# Run the demo (if invoked from the command line):
if __name__ == '__main__':
    demo.configure_traits()
