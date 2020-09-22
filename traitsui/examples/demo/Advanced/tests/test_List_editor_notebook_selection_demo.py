"""
This example demonstrates how to test interacting with a list created by
a ListEditor with use_notebook=True.

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
FILENAME = "List_editor_notebook_selection_demo.py"

#: Path of the demo script
DEMO_PATH = os.path.join(os.path.dirname(__file__), "..", FILENAME)

class TestListEditorNotebookSelectionDemo(unittest.TestCase):

    def test_list_editor_notebook_selection_demo(self):
        # Test List_editor_notebook_selection_demo.py in examples/demo/Advanced
        filepath = os.path.join(
            DEMO, "Advanced", "List_editor_notebook_selection_demo.py"
        )
        demo = load_demo(filepath, "demo")

        tester = UITester()
        with tester.create_ui(demo) as ui:
            people_list = tester.find_by_name(ui, "people")
            person2 = people_list.locate(locator.Index(2))
            person2.perform(command.MouseClick())
            self.assertEqual(demo.index, 2)
            age = person2.find_by_name("age")
            age.perform(command.KeyClick("Backspace"))
            age.perform(command.KeyClick("9"))
            self.assertEqual(demo.people[2].age, 39)


# Run the test(s)
unittest.TextTestRunner().run(
    unittest.TestLoader().loadTestsFromTestCase(TestListEditorNotebookSelectionDemo)
)