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
This example demonstrates how to test interacting with the various styles of
RangeEditor.

The GUI being tested is written in the demo under the same name (minus the
preceding 'test') in the outer directory.
"""

import os
import runpy
import unittest

from traitsui.testing.api import (
    DisplayedText,
    Index,
    KeyClick,
    KeySequence,
    MouseClick,
    Slider,
    Textbox,
    UITester,
)

#: Filename of the demo script
FILENAME = "RangeEditor_demo.py"

#: Path of the demo script
DEMO_PATH = os.path.join(os.path.dirname(__file__), "..", FILENAME)


class TestRangeEditorDemo(unittest.TestCase):
    def test_run_demo(self):
        demo = runpy.run_path(DEMO_PATH)["demo"]

        tester = UITester()
        with tester.create_ui(demo) as ui:
            simple_small = tester.find_by_id(ui, 'simple_small')
            custom_small = tester.find_by_id(ui, 'custom_small')
            text_small = tester.find_by_id(ui, 'text_small')
            readonly_small = tester.find_by_id(ui, 'readonly_small')

            simple_medium = tester.find_by_id(ui, 'simple_medium')
            custom_medium = tester.find_by_id(ui, 'custom_medium')
            text_medium = tester.find_by_id(ui, 'text_medium')
            readonly_medium = tester.find_by_id(ui, 'readonly_medium')

            # Testing for SimpleSpinEditor is not supported yet so the simple
            # and custom styles for the large_range_int are not included here
            text_large = tester.find_by_id(ui, 'text_large')
            readonly_large = tester.find_by_id(ui, 'readonly_large')

            simple_float = tester.find_by_id(ui, 'simple_float')
            custom_float = tester.find_by_id(ui, 'custom_float')
            text_float = tester.find_by_id(ui, 'text_float')
            readonly_float = tester.find_by_id(ui, 'readonly_float')

            # Tests for the small_int_range ##################################
            simple_small_slider = simple_small.locate(Slider())
            simple_small_slider.perform(KeyClick("Page Up"))
            self.assertEqual(demo.small_int_range, 2)
            simple_small_text = simple_small.locate(Textbox())
            simple_small_text.perform(KeyClick("Backspace"))
            simple_small_text.perform(KeyClick("3"))
            simple_small_text.perform(KeyClick("Enter"))
            self.assertEqual(demo.small_int_range, 3)

            custom_small.locate(Index(0)).perform(MouseClick())
            self.assertEqual(demo.small_int_range, 1)

            text_small.perform(KeyClick("0"))
            text_small.perform(KeyClick("Enter"))
            self.assertEqual(demo.small_int_range, 10)

            demo.small_int_range = 7
            displayed_small = readonly_small.inspect(DisplayedText())
            self.assertEqual(displayed_small, '7')

            # Tests for the medium_int_range #################################
            simple_medium_slider = simple_medium.locate(Slider())
            # on this range, page up/down corresponds to a change of 2.
            simple_medium_slider.perform(KeyClick("Page Up"))
            self.assertEqual(demo.medium_int_range, 3)
            simple_medium_text = simple_medium.locate(Textbox())
            simple_medium_text.perform(KeyClick("Backspace"))
            simple_medium_text.perform(KeyClick("4"))
            simple_medium_text.perform(KeyClick("Enter"))
            self.assertEqual(demo.medium_int_range, 4)

            custom_medium_slider = custom_medium.locate(Slider())
            custom_medium_slider.perform(KeyClick("Page Down"))
            self.assertEqual(demo.medium_int_range, 2)
            custom_medium_text = custom_medium.locate(Textbox())
            custom_medium_text.perform(KeyClick("Backspace"))
            custom_medium_text.perform(KeyClick("1"))
            custom_medium_text.perform(KeyClick("Enter"))
            self.assertEqual(demo.medium_int_range, 1)

            text_medium.perform(KeyClick("0"))
            text_medium.perform(KeyClick("Enter"))
            self.assertEqual(demo.medium_int_range, 10)

            demo.medium_int_range = 7
            displayed_medium = readonly_medium.inspect(DisplayedText())
            self.assertEqual(displayed_medium, '7')

            # Tests for the large_int_range ##################################
            # Testing for SimpleSpinEditor is not supported yet
            text_large.perform(KeySequence("00"))
            text_large.perform(KeyClick("Enter"))
            self.assertEqual(demo.large_int_range, 100)

            demo.large_int_range = 77
            displayed_large = readonly_large.inspect(DisplayedText())
            self.assertEqual(displayed_large, '77')

            # Tests for the float_range ######################################
            simple_float_slider = simple_float.locate(Slider())
            # on this range, page up/down corresponds to a change of 1.000.
            simple_float_slider.perform(KeyClick("Page Up"))
            self.assertEqual(demo.float_range, 1.000)
            simple_float_text = simple_float.locate(Textbox())
            for _ in range(3):
                simple_float_text.perform(KeyClick("Backspace"))
            simple_float_text.perform(KeyClick("5"))
            simple_float_text.perform(KeyClick("Enter"))
            self.assertEqual(demo.float_range, 1.5)

            custom_float_slider = custom_float.locate(Slider())
            # after the trait is set to 1.5 above, the active range shown by
            # the LargeRangeSliderEditor for the custom style is [0,11.500]
            # so a page down is now a decrement of 1.15
            custom_float_slider.perform(KeyClick("Page Down"))
            self.assertEqual(round(demo.float_range, 2), 0.35)
            custom_float_text = custom_float.locate(Textbox())
            for _ in range(5):
                custom_float_text.perform(KeyClick("Backspace"))
            custom_float_text.perform(KeySequence("50.0"))
            custom_float_text.perform(KeyClick("Enter"))
            self.assertEqual(demo.float_range, 50.0)

            text_float.perform(KeyClick("5"))
            text_float.perform(KeyClick("Enter"))
            self.assertEqual(demo.float_range, 50.05)

            demo.float_range = 72.0
            displayed_float = readonly_float.inspect(DisplayedText())
            self.assertEqual(displayed_float, '72.0')


# Run the test(s)
unittest.TextTestRunner().run(
    unittest.TestLoader().loadTestsFromTestCase(TestRangeEditorDemo)
)
