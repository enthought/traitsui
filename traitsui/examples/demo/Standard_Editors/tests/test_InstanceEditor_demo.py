# (C) Copyright 2004-2023 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

"""
This example demonstrates how to test interacting with a UI created
using InstanceEditor.

The GUI being tested is written in the demo under the same name (minus the
preceding 'test') in the outer directory.
"""

import os
import runpy
import unittest

from traitsui.testing.api import (
    DisplayedText,
    KeyClick,
    KeySequence,
    MouseClick,
    UITester,
)

#: Filename of the demo script
FILENAME = "InstanceEditor_demo.py"

#: Path of the demo script
DEMO_PATH = os.path.join(os.path.dirname(__file__), "..", FILENAME)


class TestInstanceEditorDemo(unittest.TestCase):
    def test_instance_editor_demo(self):
        demo = runpy.run_path(DEMO_PATH)["demo"]

        tester = UITester()
        with tester.create_ui(demo) as ui:
            simple = tester.find_by_id(ui, "simple")
            custom = tester.find_by_id(ui, "custom")
            occupation = custom.find_by_name("occupation")
            occupation.perform(KeySequence("Job"))
            occupation.perform(KeyClick("Enter"))
            self.assertEqual(demo.sample_instance.occupation, "Job")

            simple.perform(MouseClick())
            name = simple.find_by_name("name")
            name.perform(KeySequence("ABC"))
            name.perform(KeyClick("Enter"))
            self.assertEqual(demo.sample_instance.name, "ABC")

            demo.sample_instance.name = "XYZ"
            simple_displayed = name.inspect(DisplayedText())
            custom_name = custom.find_by_name("name")
            custom_displayed = custom_name.inspect(DisplayedText())
            self.assertEqual(simple_displayed, "XYZ")
            self.assertEqual(custom_displayed, "XYZ")


# Run the test(s)
unittest.TextTestRunner().run(
    unittest.TestLoader().loadTestsFromTestCase(TestInstanceEditorDemo)
)
