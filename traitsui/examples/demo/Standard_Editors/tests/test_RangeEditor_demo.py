"""
This example demonstrates how to test interacting with the various styles of 
RangeEditor.

The GUI being tested is written in the demo under the same name (minus the
preceding 'test') in the outer directory.
"""

import os
import runpy
import unittest

# FIXME: Import from api instead
# enthought/traitsui#1173
from traitsui.testing.tester import command, locator, query
from traitsui.testing.tester.ui_tester import UITester

#: Filename of the demo script
FILENAME = "RangeEditor_demo.py"

#: Path of the demo script
DEMO_PATH = os.path.join(os.path.dirname(__file__), "..", FILENAME)


class TestRangeEditorDemo(unittest.TestCase):

    def test_run_demo(self):
        demo = runpy.run_path(DEMO_PATH)["demo"]

        tester = UITester(delay=200)
        with tester.create_ui(demo) as ui:
            simple_small = tester.find_by_id(ui, 'simple_small')  # SimpleSliderEditor
            custom_small = tester.find_by_id(ui, 'custom_small')  # CustomEnumEditor
            text_small = tester.find_by_id(ui, 'text_small')  # RangeTextEditor
            readonly_small = tester.find_by_id(ui, 'readonly_small')

            simple_medium = tester.find_by_id(ui, 'simple_medium')  # SimpleSliderEditor
            custom_medium = tester.find_by_id(ui, 'custom_medium')  # SimpleSliderEditor
            text_medium = tester.find_by_id(ui, 'text_medium')  # RangeTextEditor
            readonly_medium = tester.find_by_id(ui, 'readonly_medium')

            simple_large = tester.find_by_id(ui, 'simple_large')  # SimpleSpinEditor
            custom_large = tester.find_by_id(ui, 'custom_large')  # SimpleSpinEditor
            text_large = tester.find_by_id(ui, 'text_large')  # RangeTextEditor
            readonly_large = tester.find_by_id(ui, 'readonly_large')

            simple_float = tester.find_by_id(ui, 'simple_float')  # LargeRangeSliderEditor
            custom_float = tester.find_by_id(ui, 'custom_float')  # LargeRangeSliderEditor
            text_float = tester.find_by_id(ui, 'text_float')  # RangeTextEditor
            readonly_float = tester.find_by_id(ui, 'readonly_float')


            # Tests for the small_int_range 
            simple_small_slider = simple_small.locate(locator.Slider())
            simple_small_slider.perform(command.KeyClick("Page Up"))
            self.assertEqual(demo.small_int_range, 2)
            simple_small_text = simple_small.locate(locator.Textbox())
            simple_small_text.perform(command.KeyClick("Backspace"))
            simple_small_text.perform(command.KeyClick("3"))
            simple_small_text.perform(command.KeyClick("Enter"))
            self.assertEqual(demo.small_int_range, 3)

            custom_small.locate(locator.Index(0)).perform(command.MouseClick())
            self.assertEqual(demo.small_int_range, 1)

            text_small.perform(command.KeyClick("0"))
            text_small.perform(command.KeyClick("Enter"))
            self.assertEqual(demo.small_int_range, 10)

            demo.small_int_range = 7
            displayed_small = readonly_small.inspect(query.DisplayedText())
            self.assertEqual(displayed_small, '7')


            # Tests for the medium_int_range 
            simple_medium_slider = simple_medium.locate(locator.Slider())
            simple_medium_slider.perform(command.KeyClick("Page Up"))
            self.assertEqual(demo.medium_int_range, 2)
            simple_medium_text = simple_medium.locate(locator.Textbox())
            simple_medium_text.perform(command.KeyClick("Backspace"))
            simple_medium_text.perform(command.KeyClick("3"))
            simple_medium_text.perform(command.KeyClick("Enter"))
            self.assertEqual(demo.medium_int_range, 3)

            custom_medium_slider = custom_medium.locate(locator.Slider())
            custom_medium_slider.perform(command.KeyClick("Page Down"))
            self.assertEqual(demo.medium_int_range, 2)
            custom_medium_text = custom_medium.locate(locator.Textbox())
            custom_medium_text.perform(command.KeyClick("Backspace"))
            custom_medium_text.perform(command.KeyClick("1"))
            custom_medium_text.perform(command.KeyClick("Enter"))
            self.assertEqual(demo.medium_int_range, 1)

            text_medium.perform(command.KeyClick("0"))
            text_medium.perform(command.KeyClick("Enter"))
            self.assertEqual(demo.medium_int_range, 10)

            demo.medium_int_range = 7
            displayed_medium = readonly_medium.inspect(query.DisplayedText())
            self.assertEqual(displayed_medium, '7')

            


# Run the test(s)
unittest.TextTestRunner().run(
    unittest.TestLoader().loadTestsFromTestCase(TestRangeEditorDemo)
)
