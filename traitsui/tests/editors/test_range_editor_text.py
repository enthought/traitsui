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
Test case for bug (wx, Mac OS X)

A RangeEditor in mode 'text' for an Int allows values out of range.
"""

# from traits.etsconfig.api import ETSConfig
# ETSConfig.toolkit = 'wx'

import unittest

from traits.has_traits import HasTraits
from traits.trait_types import Float, Int
from traitsui.item import Item
from traitsui.view import View
from traitsui import editor
from traitsui.editors.range_editor import RangeEditor

from traitsui.testing.tester import command
from traitsui.testing.api import UITester, DisplayedText, Textbox
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
        Item("number", editor=RangeEditor(low=3, high=8, mode="text",
                                          show_error_dialog=False,
                                          enter_set=True,
                                          auto_set=False)),
        buttons=["OK", "Cancel"],
    )


class FloatWithRangeEditor(HasTraits):
    """Dialog containing a RangeEditor in 'spinner' mode for an Int."""

    number = Float(5.0)
    number2 = int(3)

    traits_view = View(
        Item("number", editor=RangeEditor(low=-1.0, high=None, mode='spinner',
                                          enter_set=True,
                                          auto_set=False)),
        Item("number2", editor=RangeEditor(low=-1, high=1100000, mode='text',
                                           enter_set=True,
                                           auto_set=False)),
        Item('number2', style='readonly'),
        Item('number', style='readonly'),
        buttons=["OK", "Cancel"]
    )


class TestRangeEditorText(BaseTestMixin, unittest.TestCase):
    def setUp(self):
        BaseTestMixin.setUp(self)
        editor.UNITTESTING = True  # if True raise error on all errors. Makes it easier to test

    def tearDown(self):
        BaseTestMixin.tearDown(self)
        editor.UNITTESTING = False  # Reset so it does not affect the other test.

    @requires_toolkit([ToolkitName.wx])
    def test_text_editing(self):
        # behavior: when editing the text part of a range control box, pressing
        # the OK button should update the value of the HasTraits class
        # (tests a bug where this fails with an AttributeError)

        num = NumberWithRangeEditor()
        tester = UITester()
        with tester.create_ui(num) as ui:
            # the following is equivalent to setting the text in the text
            # control, then pressing OK
            number_field = tester.find_by_name(ui, "number")
            text = number_field.locate(Textbox())
            # text = number_field

            displayed = text.inspect(DisplayedText())
            assert displayed == '3'
            assert num.number == 3
            text.perform(command.KeyClick("Backspace"))  # make sure to delete 3
            text.perform(command.KeyClick("6"))

            displayed = text.inspect(DisplayedText())
            assert displayed == '6'
            assert num.number == 3  # num.number is not updated yet
            text.perform(command.KeyClick("Enter"))  # Update num.number
            displayed = text.inspect(DisplayedText())
            assert displayed == '6'
            assert num.number == 6
            text.perform(command.KeyClick("Backspace"))  # make sure to delete 6
            text.perform(command.KeyClick("7"))

            displayed = text.inspect(DisplayedText())
            assert displayed == '7'
            assert num.number == 6

            ok_button = tester.find_by_id(ui, "OK")
            ok_button.perform(command.MouseClick())

        # the number traits should be 7
        assert num.number == 7

    @requires_toolkit([ToolkitName.wx])
    def test_text_editing_out_of_bounds(self):
        # behavior:
        # When the value entered is out of bounds an error should be raised
        # when editing the text part of a range control box, pressing
        # the Cancel button should update the value of the HasTraits class
        # since the focus is changed.
        # (tests a bug where this fails with an AttributeError)

        num = NumberWithRangeEditor()
        assert num.number == 0
        tester = UITester()
        with tester.create_ui(num) as ui:
            # the following is equivalent to setting the text in the text
            # control, then pressing OK
            text = tester.find_by_name(ui, "number")
            displayed = text.inspect(DisplayedText())
            assert displayed == '3'
            assert num.number == 3
            text.perform(command.KeyClick("Backspace"))  # make sure to delete 3
            text.perform(command.KeyClick("1"))
            displayed = text.inspect(DisplayedText())
            assert displayed == '1'
            with self.assertRaises(RuntimeError) as context:
                text.perform(command.KeyClick("Enter"))
            self.assertTrue("The value (1) must be larger than 3!" in str(context.exception))
            # the number traits should be 3
            assert num.number == 3
            text.perform(command.KeyClick("Backspace"))
            text.perform(command.KeyClick("4"))
            displayed = text.inspect(DisplayedText())
            assert displayed == '4'
            assert num.number == 3

            cancel_button = tester.find_by_id(ui, "Cancel")
            cancel_button.perform(command.MouseClick())

        assert num.number == 4


if __name__ == "__main__":
    editor.UNITTESTING = False  # if False show errordialog on all errors. Makes it easier to test manually
    # Executing the file opens the dialog for manual testing
    # num = NumberWithRangeEditor()
    num = FloatWithRangeEditor()
    num.configure_traits()
    print(num.number)
