"""
This example demonstrates how to test interacting with a button created
using ButtonEditor.

The GUI being tested is written in the demo under the same name (minus the
preceding 'test') in the outer directory.
"""

import os
import runpy
import unittest

# FIXME: Import from api instead
# enthought/traitsui#1173
from traitsui.testing.tester import command, query
from traitsui.testing.tester.ui_tester import UITester

#: Filename of the demo script
FILENAME = "ButtonEditor_simple_demo.py"

#: Path of the demo script
DEMO_PATH = os.path.join(os.path.dirname(__file__), "..", FILENAME)


class TestButtonEditorSimpleDemo(unittest.TestCase):

    def test_button_editor_simple_demo(self):
        # Test ButtonEditor_simple_demo.py in examples/demo/Standard_Edtiors
        demo = runpy.run_path(DEMO_PATH)["demo"]

        tester = UITester()
        with tester.create_ui(demo) as ui:
            button = tester.find_by_name(ui, "my_button_trait")
            for index in range(5):
                button.perform(command.MouseClick())
                self.assertEqual(demo.click_counter, index + 1)

            click_counter = tester.find_by_name(ui, "click_counter")
            displayed_count = click_counter.inspect(query.DisplayedText())
            self.assertEqual(displayed_count, '5')

            demo.click_counter = 10
            displayed_count = click_counter.inspect(query.DisplayedText())
            self.assertEqual(displayed_count, '10')


# Run the test(s)
unittest.TextTestRunner().run(
    unittest.TestLoader().loadTestsFromTestCase(TestButtonEditorSimpleDemo)
)
