# -----------------------------------------------------------------------------
#
#  Copyright (c) 2020, Enthought, Inc.
#  All rights reserved.
#
#  This software is provided without warranty under the terms of the BSD
#  license included in LICENSE.txt and may be redistributed only
#  under the conditions described in the aforementioned license.  The license
#  is also available online at http://www.enthought.com/licenses/BSD.txt
#
# -----------------------------------------------------------------------------

import unittest

from traits.api import HasTraits, Bool
from traitsui.api import BooleanEditor, Item, View
from traitsui.tests._tools import (
    BaseTestMixin,
    requires_toolkit,
    ToolkitName,
)

from traitsui.testing.api import MouseClick, UITester


class BoolModel(HasTraits):

    true_or_false = Bool()


# Run this against wx once enthought/traitsui#752 is also fixed for
# BooleanEditor
@requires_toolkit([ToolkitName.qt, ToolkitName.wx])
class TestBooleanEditor(BaseTestMixin, unittest.TestCase):

    def setUp(self):
        BaseTestMixin.setUp(self)

    def tearDown(self):
        BaseTestMixin.tearDown(self)

    def test_click_boolean(self):
        view = View(Item("true_or_false", editor=BooleanEditor()))
        obj = BoolModel()

        tester = UITester()
        with tester.create_ui(obj, dict(view=view)) as ui:
            # sanity check
            self.assertEqual(obj.true_or_false, False)
            checkbox = tester.find_by_name(ui, "true_or_false")
            checkbox.perform(MouseClick())
            self.assertEqual(obj.true_or_false, True)
