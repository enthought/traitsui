"""
This example demonstrates how to test interacting with a textbox created
using InstanceEditor.

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
FILENAME = "InstanceEditor_demo.py"

#: Path of the demo script
DEMO_PATH = os.path.join(os.path.dirname(__file__), "..", FILENAME)


class TestInstanceEditorDemo(unittest.TestCase):

    def test_instance_editor_demo(self):
        # Test InstanceEditor_demo.py in examples/demo/Standard_Edtiors
        demo = runpy.run_path(DEMO_PATH)["demo"]

        tester = UITester()
        with tester.create_ui(demo) as ui:
            simple = tester.find_by_id(ui, "simple")
            custom = tester.find_by_id(ui, "custom")
            occupation = custom.find_by_name("occupation")
            occupation.perform(command.KeySequence("Job"))
            occupation.perform(command.KeyClick("Enter"))
            self.assertEqual(demo.sample_instance.occupation, "Job")

            simple.perform(command.MouseClick())
            name = simple.find_by_name("name")
            name.perform(command.KeySequence("ABC"))
            name.perform(command.KeyClick("Enter"))
            self.assertEqual(demo.sample_instance.name, "ABC")

            demo.sample_instance.name = "XYZ"
            simple_displayed = name.inspect(query.DisplayedText())
            custom_name = custom.find_by_name("name")
            custom_displayed = custom_name.inspect(query.DisplayedText())
            self.assertEqual(simple_displayed, "XYZ")
            self.assertEqual(custom_displayed, "XYZ")


# Run the test(s)
unittest.TextTestRunner().run(
    unittest.TestLoader().loadTestsFromTestCase(TestInstanceEditorDemo)
)