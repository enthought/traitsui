# (C) Copyright 2004-2022 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

"""
This example demonstrates how to test interacting with a checklist created
using CheckListEditor.

The GUI being tested is written in the demo under the same name (minus the
preceding 'test') in the outer directory.
"""

import os
import runpy
import unittest

from traitsui.testing.api import Index, MouseClick, UITester

#: Filename of the demo script
FILENAME = "CheckListEditor_simple_demo.py"

#: Path of the demo script
DEMO_PATH = os.path.join(os.path.dirname(__file__), "..", FILENAME)


class TestCheckListEditorSimpleDemo(unittest.TestCase):
    def test_checklist_editor_simple_demo(self):
        demo = runpy.run_path(DEMO_PATH)["demo"]

        tester = UITester()
        with tester.create_ui(demo) as ui:
            checklist = tester.find_by_id(ui, "custom")
            item3 = checklist.locate(Index(2))
            item3.perform(MouseClick())
            self.assertEqual(demo.checklist, ["three"])
            item3.perform(MouseClick())
            self.assertEqual(demo.checklist, [])


# Run the test(s)
unittest.TextTestRunner().run(
    unittest.TestLoader().loadTestsFromTestCase(TestCheckListEditorSimpleDemo)
)
