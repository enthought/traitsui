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
This example demonstrates how to test interacting with a boolean
using BooleanEditor.

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
FILENAME = "BooleanEditor_demo.py"

#: Path of the demo script
DEMO_PATH = os.path.join(os.path.dirname(__file__), "..", FILENAME)


class TestBooleanEditorDemo(unittest.TestCase):
    def test_boolean_editor_demo(self):
        demo = runpy.run_path(DEMO_PATH)["demo"]

        tester = UITester()
        with tester.create_ui(demo) as ui:
            simple = tester.find_by_id(ui, 'simple')
            custom = tester.find_by_id(ui, 'custom')
            text = tester.find_by_id(ui, 'text')
            readonly = tester.find_by_id(ui, 'readonly')

            simple.perform(MouseClick())
            self.assertEqual(demo.boolean_trait, True)
            custom.perform(MouseClick())
            self.assertEqual(demo.boolean_trait, False)

            for _ in range(5):
                text.perform(KeyClick("Backspace"))
            text.perform(KeySequence("True"))
            text.perform(KeyClick("Enter"))
            self.assertEqual(demo.boolean_trait, True)

            demo.boolean_trait = False
            displayed = readonly.inspect(DisplayedText())
            self.assertEqual(displayed, "False")


# Run the test(s)
unittest.TextTestRunner().run(
    unittest.TestLoader().loadTestsFromTestCase(TestBooleanEditorDemo)
)
