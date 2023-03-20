# (C) Copyright 2004-2023 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

import os
import unittest
import subprocess
import sys

try:
    import numpy as np  # noqa: F401
except ImportError:
    raise unittest.SkipTest("Can't import NumPy: skipping")
import pkg_resources

from traits.api import Bool, Callable, File, Float, HasTraits, Range, Str
from traitsui.api import ContextValue, Item, View
from traitsui.editors.video_editor import MediaStatus, PlayerState, VideoEditor
from traitsui.tests._tools import BaseTestMixin, create_ui, is_qt5, is_qt6

filename = pkg_resources.resource_filename('traitsui.testing', 'data/test.mp4')


# Is a MacOS machine lacking the standard Metal APIs?
metal_api_missing = False
if sys.platform == 'darwin' and is_qt6:
    # TODO: would be nice to detect if Qt build _uses_ Metal
    result = subprocess.run(
        ["system_profiler", "SPDisplaysDataType"],
        capture_output=True,
        check=True,
    )
    metal_api_missing = (b'Metal Family: Supported' not in result.stdout)


class MovieTheater(HasTraits):
    url = File(filename)

    state = PlayerState()
    duration = Float()
    position = Range(low=0.0, high='duration')
    error = Str()
    status = MediaStatus()
    buffer = Range(0, 100)
    muted = Bool(True)
    volume = Range(0.0, 100.0)
    playback_rate = Float(1.0)
    image_func = Callable()


@unittest.skipIf(not is_qt5() and not is_qt6(), 'Requires Qt5 or 6')
@unittest.skipIf(metal_api_missing, "Mac Qt6 video editor requires Metal API")
class TestVideoEditor(BaseTestMixin, unittest.TestCase):
    def setUp(self):
        BaseTestMixin.setUp(self)

    def tearDown(self):
        BaseTestMixin.tearDown(self)

    def test_video_editor_basics(self):
        obj = MovieTheater()

        # Test an editor with trait syncronizations
        view = View(
            Item(
                'url',
                editor=VideoEditor(
                    state=ContextValue('state'),
                    position=ContextValue('position'),
                    duration=ContextValue('duration'),
                    video_error=ContextValue('error'),
                    media_status=ContextValue('status'),
                    buffer=ContextValue('buffer'),
                    muted=ContextValue('muted'),
                    volume=ContextValue('volume'),
                    playback_rate=ContextValue('playback_rate'),
                    image_func=ContextValue('image_func'),
                    notify_interval=0.5,
                ),
            ),
        )
        with create_ui(obj, {'view': view}):
            pass

        # And an editor with no synced traits
        view = View(Item('url', editor=VideoEditor()))
        with create_ui(obj, {'view': view}):
            pass
