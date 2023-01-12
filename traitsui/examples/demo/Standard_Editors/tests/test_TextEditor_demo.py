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
This example demonstrates how to test interacting with a textbox created
using TextEditor.

The GUI being tested is written in the demo under the same name (minus the
preceding 'test') in the outer directory.
"""

import os
import runpy
import unittest

from traitsui.testing.api import DisplayedText, KeyClick, KeySequence, UITester

#: Filename of the demo script
FILENAME = "TextEditor_demo.py"

#: Path of the demo script
DEMO_PATH = os.path.join(os.path.dirname(__file__), "..", FILENAME)


class TestTextEditorDemo(unittest.TestCase):
    def test_run_demo(self):
        demo = runpy.run_path(DEMO_PATH)["demo"]

        tester = UITester()
        with tester.create_ui(demo) as ui:
            simple_int_field = tester.find_by_id(ui, "simple_int")
            custom_int_field = tester.find_by_id(ui, "custom_int")
            text_int_field = tester.find_by_id(ui, "text_int")
            readonly_int_field = tester.find_by_id(ui, "readonly_int")

            # Modify the value to something invalid
            simple_int_field.perform(KeyClick("Backspace"))
            simple_int_field.perform(KeySequence("a"))  # not a number!

            # Check the value has not changed
            self.assertEqual(demo.int_trait, 1)
            self.assertEqual(custom_int_field.inspect(DisplayedText()), "1")
            self.assertEqual(text_int_field.inspect(DisplayedText()), "1")
            self.assertEqual(readonly_int_field.inspect(DisplayedText()), "1")

            # Modify the value on the GUI to a good value
            simple_int_field.perform(KeyClick("Backspace"))
            simple_int_field.perform(KeySequence("2"))

            # Check
            self.assertEqual(demo.int_trait, 2)
            self.assertEqual(custom_int_field.inspect(DisplayedText()), "2")
            self.assertEqual(text_int_field.inspect(DisplayedText()), "2")
            self.assertEqual(readonly_int_field.inspect(DisplayedText()), "2")


# Run the test(s)
unittest.TextTestRunner().run(
    unittest.TestLoader().loadTestsFromTestCase(TestTextEditorDemo)
)
