"""
This example demonstrates how to test interacting with a ListEditor.

The GUI being tested is written in the demo under the same name (minus the
preceding 'test') in the outer directory.
"""

import os
import runpy
import unittest

# FIXME: Import from api instead
# enthought/traitsui#1173
from traitsui.testing.tester import command, locator
from traitsui.testing.tester.ui_tester import UITester

#: Filename of the demo script
FILENAME = "ListEditor_demo.py"

#: Path of the demo script
DEMO_PATH = os.path.join(os.path.dirname(__file__), "..", FILENAME)


class TestListEditorDemo(unittest.TestCase):

    def test_list_editor_demo(self):
        demo = runpy.run_path(DEMO_PATH)["demo"]

        tester = UITester()
        with tester.create_ui(demo) as ui:
            custom_list = tester.find_by_id(ui, "custom")
            item1 = custom_list.locate(locator.Index(1))
            for _ in range(6):
                item1.perform(command.KeyClick("Backspace"))
            item1.perform(command.KeySequence("Othello"))
            item1.perform(command.KeyClick("Enter"))
            self.assertEqual(demo.play_list,
                ["The Merchant of Venice", "Othello", "MacBeth"])


# Run the test(s)
unittest.TextTestRunner().run(
    unittest.TestLoader().loadTestsFromTestCase(TestListEditorDemo)
)