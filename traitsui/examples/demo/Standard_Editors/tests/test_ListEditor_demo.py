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
This example demonstrates how to test interacting with a ListEditor.

The GUI being tested is written in the demo under the same name (minus the
preceding 'test') in the outer directory.
"""

import os
import runpy
import unittest

from traitsui.testing.api import Index, KeyClick, KeySequence, UITester

#: Filename of the demo script
FILENAME = "ListEditor_demo.py"

#: Path of the demo script
DEMO_PATH = os.path.join(os.path.dirname(__file__), "..", FILENAME)


class TestListEditorDemo(unittest.TestCase):
    def test_list_editor_demo(self):
        demo = runpy.run_path(DEMO_PATH)["demo"]

        tester = UITester()
        with tester.create_ui(demo) as ui:
            custom_list = tester.find_by_id(ui, "custom")
            item1 = custom_list.locate(Index(1))
            for _ in range(6):
                item1.perform(KeyClick("Backspace"))
            item1.perform(KeySequence("Othello"))
            item1.perform(KeyClick("Enter"))
            self.assertEqual(
                demo.play_list,
                ["The Merchant of Venice", "Othello", "MacBeth"],
            )


# Run the test(s)
unittest.TextTestRunner().run(
    unittest.TestLoader().loadTestsFromTestCase(TestListEditorDemo)
)
