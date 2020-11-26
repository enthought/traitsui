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

from traits.api import HasTraits, Int
from traitsui.api import HGroup, Item, spring, VGroup, View
from traitsui.tests._tools import (
    BaseTestMixin,
    create_ui,
    requires_toolkit,
    ToolkitName,
)


class ObjectWithNumber(HasTraits):
    number1 = Int()
    number2 = Int()
    number3 = Int()


@requires_toolkit([ToolkitName.qt, ToolkitName.wx])
class TestUIPanel(BaseTestMixin, unittest.TestCase):

    def setUp(self):
        BaseTestMixin.setUp(self)

    def tearDown(self):
        BaseTestMixin.tearDown(self)

    def test_grouped_layout_with_springy(self):
        # Regression test for enthought/traitsui#1066
        obj1 = ObjectWithNumber()
        view = View(
            HGroup(
                VGroup(
                    Item("number1"),
                ),
                VGroup(
                    Item("number2"),
                ),
                spring,
            )
        )
        # This should not fail.
        with create_ui(obj1, dict(view=view)):
            pass
