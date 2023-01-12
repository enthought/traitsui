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
This example demonstrates how to test interacting with the various modes of
the EnumEditor.

The GUI being tested is written in the demo under the same name (minus the
preceding 'test') in the outer directory.
"""

import os
import runpy
import unittest

from traitsui.testing.api import (
    DisplayedText,
    Index,
    KeyClick,
    KeySequence,
    MouseClick,
    SelectedText,
    UITester,
)

#: Filename of the demo script
FILENAME = "EnumEditor_demo.py"

#: Path of the demo script
DEMO_PATH = os.path.join(os.path.dirname(__file__), "..", FILENAME)


class TestEnumEditorDemo(unittest.TestCase):
    def test_enum_editor_demo(self):
        demo = runpy.run_path(DEMO_PATH)["demo"]

        tester = UITester()
        with tester.create_ui(demo) as ui:
            simple_enum = tester.find_by_id(ui, "simple")
            simple_text_enum = tester.find_by_id(ui, "simple_text")
            radio_enum = tester.find_by_id(ui, "radio")
            list_enum = tester.find_by_id(ui, "list")
            text = tester.find_by_id(ui, "text")
            readonly = tester.find_by_id(ui, "readonly")

            self.assertEqual(demo.name_list, 'A-495')
            simple_enum.locate(Index(1)).perform(MouseClick())
            self.assertEqual(demo.name_list, 'A-498')

            for _ in range(5):
                simple_text_enum.perform(KeyClick("Backspace"))
            simple_text_enum.perform(KeySequence("R-1226"))
            simple_text_enum.perform(KeyClick("Enter"))
            self.assertEqual(demo.name_list, 'R-1226')

            radio_enum.locate(Index(5)).perform(MouseClick())
            self.assertEqual(demo.name_list, 'Foo')

            list_enum.locate(Index(3)).perform(MouseClick())
            self.assertEqual(demo.name_list, 'TS-17')

            for _ in range(5):
                text.perform(KeyClick("Backspace"))
            text.perform(KeySequence("A-498"))
            text.perform(KeyClick("Enter"))
            self.assertEqual(demo.name_list, 'A-498')

            demo.name_list = 'Foo'

            displayed_simple = simple_enum.inspect(DisplayedText())
            disp_simple_text = simple_text_enum.inspect(DisplayedText())
            selected_radio = radio_enum.inspect(SelectedText())
            selected_list = list_enum.inspect(SelectedText())
            displayed_text = text.inspect(DisplayedText())
            displayed_readonly = readonly.inspect(DisplayedText())

            displayed_selected = [
                displayed_simple,
                disp_simple_text,
                selected_radio,
                selected_list,
                displayed_text,
                displayed_readonly,
            ]
            for text in displayed_selected:
                self.assertEqual(text, 'Foo')


# Run the test(s)
unittest.TextTestRunner().run(
    unittest.TestLoader().loadTestsFromTestCase(TestEnumEditorDemo)
)
