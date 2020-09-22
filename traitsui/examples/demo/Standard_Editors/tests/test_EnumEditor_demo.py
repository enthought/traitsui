"""
This example demonstrates how to test interacting with the various modes of
the EnumEditor.

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
FILENAME = "EnumEditor_demo.py"

#: Path of the demo script
DEMO_PATH = os.path.join(os.path.dirname(__file__), "..", FILENAME)


class TestEnumEditorDemo(unittest.TestCase):

    def test_enum_editor_demo(self):
        # Test EnumEditor_demo.py in examples/demo/Standard_Edtiors
        demo = runpy.run_path(DEMO_PATH)["demo"]

        tester = UITester()
        with tester.create_ui(demo) as ui:
            simple_enum = tester.find_by_id(ui, "simple")
            simple_text_enum = tester.find_by_id(ui, "simple_text")
            radio_enum = tester.find_by_id(ui, "radio")
            list_enum = tester.find_by_id(ui, "list")
            text = tester.find_by_id(ui, "text")
            readonly = tester.find_by_id(ui, "readonly")

            self.assertEqual(demo.name_list, 'A-495')
            simple_enum.locate(locator.Index(1)).perform(command.MouseClick())
            self.assertEqual(demo.name_list, 'A-498')

            for _ in range(5):
                simple_text_enum.perform(command.KeyClick("Backspace"))
            simple_text_enum.perform(command.KeySequence("R-1226"))
            simple_text_enum.perform(command.KeyClick("Enter"))
            self.assertEqual(demo.name_list, 'R-1226')

            radio_enum.locate(locator.Index(5)).perform(command.MouseClick())
            self.assertEqual(demo.name_list, 'Foo')

            list_enum.locate(locator.Index(3)).perform(command.MouseClick())
            self.assertEqual(demo.name_list, 'TS-17')

            for _ in range(5):
                text.perform(command.KeyClick("Backspace"))
            text.perform(command.KeySequence("A-498"))
            text.perform(command.KeyClick("Enter"))
            self.assertEqual(demo.name_list, 'A-498')

            demo.name_list = 'Foo'

            displayed_simple = simple_enum.inspect(query.DisplayedText())
            disp_simple_text = simple_text_enum.inspect(query.DisplayedText())
            selected_radio = radio_enum.inspect(query.SelectedText())
            selected_list = list_enum.inspect(query.SelectedText())
            displayed_text = text.inspect(query.DisplayedText())
            displayed_readonly = readonly.inspect(query.DisplayedText())

            displayed_selected = [
                displayed_simple, disp_simple_text, selected_radio,
                selected_list, displayed_text, displayed_readonly
            ]
            for text in displayed_selected:
                self.assertEqual(text, 'Foo')


# Run the test(s)
unittest.TextTestRunner().run(
    unittest.TestLoader().loadTestsFromTestCase(TestEnumEditorDemo)
)
