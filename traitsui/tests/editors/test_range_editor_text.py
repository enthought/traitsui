# (C) Copyright 2004-2023 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

"""
Test case for bug (wx, Mac OS X)

A RangeEditor in mode 'text' for an Int allows values out of range.
"""
import unittest

from traits.has_traits import HasTraits
from traits.trait_types import Float, Int
from traitsui.item import Item
from traitsui.view import View
from traitsui.editors.range_editor import RangeEditor

from traitsui.testing.tester import command
from traitsui.testing.tester.ui_tester import UITester
from traitsui.tests._tools import (
    BaseTestMixin,
    requires_toolkit,
    ToolkitName,
)


class NumberWithRangeEditor(HasTraits):
    """Dialog containing a RangeEditor in 'spinner' mode for an Int."""

    number = Int()

    traits_view = View(
        Item(label="Range should be 3 to 8. Enter 1, then press OK"),
        Item("number", editor=RangeEditor(low=3, high=8, mode="text")),
        buttons=["OK"],
    )


class FloatWithRangeEditor(HasTraits):
    """Dialog containing a RangeEditor in 'spinner' mode for an Int."""

    number = Float(5.0)

    traits_view = View(
        Item("number", editor=RangeEditor(low=0.0, high=12.0)), buttons=["OK"]
    )


class TestRangeEditorText(BaseTestMixin, unittest.TestCase):
    def setUp(self):
        BaseTestMixin.setUp(self)

    def tearDown(self):
        BaseTestMixin.tearDown(self)

    @requires_toolkit([ToolkitName.wx])
    def test_wx_text_editing(self):
        # behavior: when editing the text part of a spin control box, pressing
        # the OK button should update the value of the HasTraits class
        # (tests a bug where this fails with an AttributeError)

        num = NumberWithRangeEditor()
        tester = UITester()
        with tester.create_ui(num) as ui:
            # the following is equivalent to setting the text in the text
            # control, then pressing OK
            text = tester.find_by_name(ui, "number")
            text.perform(command.KeyClick("1"))
            text.perform(command.KeyClick("Enter"))

        # the number traits should be between 3 and 8
        self.assertTrue(3 <= num.number <= 8)


if __name__ == "__main__":
    # Executing the file opens the dialog for manual testing
    num = NumberWithRangeEditor()
    num.configure_traits()
    print(num.number)
