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
This example demonstrates how to test interacting with a list created by
a ListEditor with use_notebook=True.

The GUI being tested is written in the demo under the same name (minus the
preceding 'test') in the outer directory.
"""

import os
import runpy
import unittest

from traitsui.testing.api import Index, KeyClick, MouseClick, UITester

#: Filename of the demo script
FILENAME = "List_editor_notebook_selection_demo.py"

#: Path of the demo script
DEMO_PATH = os.path.join(os.path.dirname(__file__), "..", FILENAME)


class TestListEditorNotebookSelectionDemo(unittest.TestCase):
    def test_list_editor_notebook_selection_demo(self):
        demo = runpy.run_path(DEMO_PATH)["demo"]

        tester = UITester()
        with tester.create_ui(demo) as ui:
            people_list = tester.find_by_name(ui, "people")
            person2 = people_list.locate(Index(2))
            person2.perform(MouseClick())
            self.assertEqual(demo.index, 2)
            age = person2.find_by_name("age")
            age.perform(KeyClick("Backspace"))
            age.perform(KeyClick("9"))
            self.assertEqual(demo.people[2].age, 39)


# Run the test(s)
unittest.TextTestRunner().run(
    unittest.TestLoader().loadTestsFromTestCase(
        TestListEditorNotebookSelectionDemo
    )
)
