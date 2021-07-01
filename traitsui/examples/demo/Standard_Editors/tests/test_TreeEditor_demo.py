# (C) Copyright 2004-2021 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

"""
This example demonstrates how to test interacting with a TreeEditor.

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
    MouseDClick,
    TreeNode,
    UITester
)
from traitsui.tests._tools import requires_toolkit, ToolkitName

#: Filename of the demo script
FILENAME = "TreeEditor_demo.py"

#: Path of the demo script
DEMO_PATH = os.path.join(os.path.dirname(__file__), "..", FILENAME)


class TestTreeEditorDemo(unittest.TestCase):

    @requires_toolkit([ToolkitName.qt])
    def test_tree_editor_demo(self):
        demo = runpy.run_path(DEMO_PATH)["demo"]
        tester = UITester()
        with tester.create_ui(demo) as ui:
            root_actor = tester.find_by_name(ui, "company")

            # Enthought->Department->Business->(First employee)
            node = root_actor.locate(TreeNode((0, 0, 0, 0), 0))
            node.perform(MouseClick())

            name_actor = node.find_by_name("name")
            for _ in range(5):
                name_actor.perform(KeyClick("Backspace"))
            name_actor.perform(KeySequence("James"))
            self.assertEqual(
                demo.company.departments[0].employees[0].name,
                "James",
            )

            # Enthought->Department->Scientific
            demo.company.departments[1].name = "Scientific Group"
            node = root_actor.locate(TreeNode((0, 0, 1), 0))
            self.assertEqual(
                node.inspect(DisplayedText()), "Scientific Group"
            )

            # Enthought->Department->Business
            node = root_actor.locate(TreeNode((0, 0, 0), 0))
            node.perform(MouseClick())
            node.perform(MouseDClick())

            name_actor = node.find_by_name("name")
            name_actor.perform(KeySequence(" Group"))
            self.assertEqual(
                demo.company.departments[0].name,
                "Business Group",
            )


# Run the test(s)
unittest.TextTestRunner().run(
    unittest.TestLoader().loadTestsFromTestCase(TestTreeEditorDemo)
)
