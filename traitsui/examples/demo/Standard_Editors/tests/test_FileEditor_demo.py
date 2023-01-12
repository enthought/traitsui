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
using FileEditor.

The GUI being tested is written in the demo under the same name (minus the
preceding 'test') in the outer directory.
"""

import os
import runpy
import unittest

from traitsui.testing.api import DisplayedText, KeyClick, KeySequence, UITester

#: Filename of the demo script
FILENAME = "FileEditor_demo.py"

#: Path of the demo script
DEMO_PATH = os.path.join(os.path.dirname(__file__), "..", FILENAME)


class TestFileEditorDemo(unittest.TestCase):
    def test_run_demo(self):
        demo = runpy.run_path(DEMO_PATH)["demo"]

        tester = UITester()
        with tester.create_ui(demo) as ui:
            # simple FileEditor
            simple_file_field = tester.find_by_id(ui, "simple_file")

            # Modify the value on the GUI
            # The path does not exist, which is allowed by the trait.
            # The custom FileEditor will ignore nonexisting file path.
            simple_file_field.perform(KeySequence("some_path"))
            simple_file_field.perform(KeyClick("Enter"))
            self.assertEqual(demo.file_name, "some_path")

            # Modify the value on the object
            demo.file_name = FILENAME
            self.assertEqual(
                simple_file_field.inspect(DisplayedText()), FILENAME
            )

            # On wx, an assertion error occurs upon disposing the UI.
            # That error is linked to the custom FileEditor.
            # See enthought/traitsui#752


# Run the test(s)
unittest.TextTestRunner().run(
    unittest.TestLoader().loadTestsFromTestCase(TestFileEditorDemo)
)
