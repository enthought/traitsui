#  Copyright (c) 2005-2020, Enthought, Inc.
#  All rights reserved.
#
#  This software is provided without warranty under the terms of the BSD
#  license included in LICENSE.txt and may be redistributed only
#  under the conditions described in the aforementioned license.  The license
#  is also available online at http://www.enthought.com/licenses/BSD.txt
#
#  Thanks for using Enthought open source!
#
""" Tests to exercise logic for layouts, e.g. VGroup, HGroup.
"""

import unittest

import pkg_resources

from traits.api import Bool, File, HasTraits,
from traitsui.api import Item, View
from traitsui.tests._tools import (
    create_ui,
    skip_if_not_wx,
)

filename = pkg_resources.resource_filename("traitsui", "examples/demo/Extras/images/logo_32x32.gif")

class AnimatedGIF(HasTraits):

    gif_file = File(filename)

    playing = Bool(True)


@skip_if_not_wx
class TestAnimatedGIFEditor(unittest.TestCase):

    def test_animated_gif_editor(self):
        # Regression test for enthought/traitsui#1087
        obj1 = AnimatedGIF()
        view = View(
            Item('gif_file', editor=AnimatedGIFEditor(playing='playing')),
            Item('playing'),
        )
        
        # This should not fail.
        with create_ui(obj1, dict(view=view)):
            pass
