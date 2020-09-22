"""
This example demonstrates how to test interacting with a checklist created
using CheckListEditor.

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
FILENAME = "CheckListEditor_simple_demo.py"

#: Path of the demo script
DEMO_PATH = os.path.join(os.path.dirname(__file__), "..", FILENAME)


class TestCheckListEditorSimpleDemo(unittest.TestCase):

    def test_checklist_editor_simple_demo(self):
        # Test CheckListEditor_simple_demo.py in examples/demo/Standard_Edtiors
        demo = runpy.run_path(DEMO_PATH)["demo"]

        tester = UITester()
        with tester.create_ui(demo) as ui:
            checklist = tester.find_by_id(ui, "custom")
            item3 = checklist.locate(locator.Index(2))
            item3.perform(command.MouseClick())
            self.assertEqual(demo.checklist, ["three"])
            item3.perform(command.MouseClick())
            self.assertEqual(demo.checklist, [])


# Run the test(s)
unittest.TextTestRunner().run(
    unittest.TestLoader().loadTestsFromTestCase(TestCheckListEditorSimpleDemo)
)
