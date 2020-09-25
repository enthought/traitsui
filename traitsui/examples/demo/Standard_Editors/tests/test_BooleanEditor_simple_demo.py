"""
This example demonstrates how to test interacting with a boolean
using BooleanEditor.

The GUI being tested is written in the demo under the same name (minus the
preceding 'test') in the outer directory.
"""

import os
import runpy
import unittest

from traitsui.testing.api import (
    DisplayedText, KeyClick, KeySequence, MouseClick, UITester
)

#: Filename of the demo script
FILENAME = "BooleanEditor_simple_demo.py"

#: Path of the demo script
DEMO_PATH = os.path.join(os.path.dirname(__file__), "..", FILENAME)


class TestBooleanEditorSimpleDemo(unittest.TestCase):

    def test_boolean_editor_simple_demo(self):
        demo = runpy.run_path(DEMO_PATH)["demo"]

        tester = UITester()
        with tester.create_ui(demo) as ui:
            simple = tester.find_by_id(ui, 'simple')
            readonly = tester.find_by_id(ui, 'readonly')
            text = tester.find_by_id(ui, 'text')
            count_changes = tester.find_by_name(ui, "count_changes")

            simple.perform(MouseClick())
            self.assertEqual(demo.my_boolean_trait, True)

            for _ in range(4):
                text.perform(KeyClick("Backspace"))
            text.perform(KeySequence("False"))
            text.perform(KeyClick("Enter"))
            self.assertEqual(demo.my_boolean_trait, False)

            displayed_count_changes = count_changes.inspect(DisplayedText())
            self.assertEqual(displayed_count_changes, '2')
            self.assertEqual(displayed_count_changes, str(demo.count_changes))

            demo.my_boolean_trait = True
            displayed = readonly.inspect(DisplayedText())
            self.assertEqual(displayed, "True")

            displayed_count_changes = count_changes.inspect(DisplayedText())
            self.assertEqual(displayed_count_changes, '3')
            self.assertEqual(displayed_count_changes, str(demo.count_changes))


# Run the test(s)
unittest.TextTestRunner().run(
    unittest.TestLoader().loadTestsFromTestCase(TestBooleanEditorSimpleDemo)
)
