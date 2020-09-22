"""
This example demonstrates how to test a simple application using UI Tester.

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
FILENAME = "converter.py"

#: Path of the demo script
DEMO_PATH = os.path.join(os.path.dirname(__file__), "..", FILENAME)


class TestConverter(unittest.TestCase):
    def test_converter(self):
        demo = runpy.run_path(DEMO_PATH)["popup"]
        tester = UITester()
        with tester.create_ui(demo) as ui:
            input_amount = tester.find_by_name(ui, "input_amount")
            output_amount = tester.find_by_name(ui, "output_amount")
            for _ in range(4):
                input_amount.perform(command.KeyClick("Backspace"))
            input_amount.perform(command.KeySequence("14.0"))
            self.assertEqual(
                output_amount.inspect(query.DisplayedText())[:4],
                "1.16",
            )
            tester.find_by_id(ui, "Undo").perform(command.MouseClick())
            self.assertEqual(
                output_amount.inspect(query.DisplayedText()),
                "1.0",
            )


# Run the test(s)
unittest.TextTestRunner().run(
    unittest.TestLoader().loadTestsFromTestCase(TestConverter)
)
