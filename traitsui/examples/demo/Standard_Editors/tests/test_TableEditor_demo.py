"""
This example demonstrates how to test interacting with a TableEditor.

The GUI being tested is written in the demo under the same name (minus the
preceding 'test') in the outer directory.
"""

import os
import runpy
import unittest


from traitsui.testing.api import (
    Cell, KeyClick, KeySequence, MouseClick, UITester
)
from traitsui.tests._tools import requires_toolkit, ToolkitName

#: Filename of the demo script
FILENAME = "TableEditor_demo.py"

#: Path of the demo script
DEMO_PATH = os.path.join(os.path.dirname(__file__), "..", FILENAME)


class TestTableEditorDemo(unittest.TestCase):

    @requires_toolkit([ToolkitName.qt])
    def test_list_editor_demo(self):
        demo = runpy.run_path(DEMO_PATH)["demo"]

        tester = UITester()
        with tester.create_ui(demo) as ui:
            employees_table = tester.find_by_name(ui, "employees")

            # clicking a cell enters edit mode and selects full text
            cell_21 = employees_table.locate(Cell(2, 1))
            cell_21.perform(MouseClick())
            cell_21.perform(KeySequence("Jones"))
            cell_21.perform(KeyClick("Enter"))

            self.assertEqual(demo.employees[0].last_name, 'Jones')

            # third column corresponds to Full Name property
            cell_32 = employees_table.locate(Cell(3, 2))
            cell_32.perform(MouseClick())


# Run the test(s)
unittest.TextTestRunner().run(
    unittest.TestLoader().loadTestsFromTestCase(TestTableEditorDemo)
)
