# (C) Copyright 2004-2021 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!
import unittest

import pkg_resources

from traits.api import Bool, Callable, File, Float, HasTraits, Range, Str
from traitsui.api import Item, View
from traitsui.editors.video_editor import MediaStatus, PlayerState, VideoEditor
from traitsui.tests._tools import BaseTestMixin, create_ui, is_qt5

filename = pkg_resources.resource_filename("traitsui.testing", "data/test.mp4")


class MovieTheater(HasTraits):
    url = File(filename)

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


@unittest.skipIf(not is_qt5(), "Requires Qt5")
class TestVideoEditor(BaseTestMixin, unittest.TestCase):

    def setUp(self):
        BaseTestMixin.setUp(self)

    def tearDown(self):
        BaseTestMixin.tearDown(self)

    def test_video_editor_basics(self):
        obj = MovieTheater()
        view = View(
            Item(
                'url',
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
        )

        # This should not fail.
        with create_ui(obj, {'view': view}):
            pass
