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
This example demonstrates how to test interacting with a button created
using ButtonEditor.

The GUI being tested is written in the demo under the same name (minus the
preceding 'test') in the outer directory.
"""

import os
import runpy
import unittest

from traitsui.testing.api import DisplayedText, MouseClick, UITester

#: Filename of the demo script
FILENAME = "ButtonEditor_simple_demo.py"

#: Path of the demo script
DEMO_PATH = os.path.join(os.path.dirname(__file__), "..", FILENAME)


class TestButtonEditorSimpleDemo(unittest.TestCase):
    def test_button_editor_simple_demo(self):
        demo = runpy.run_path(DEMO_PATH)["demo"]

        tester = UITester()
        with tester.create_ui(demo) as ui:
            button = tester.find_by_name(ui, "my_button_trait")
            for index in range(5):
                button.perform(MouseClick())
                self.assertEqual(demo.click_counter, index + 1)

            click_counter = tester.find_by_name(ui, "click_counter")
            displayed_count = click_counter.inspect(DisplayedText())
            self.assertEqual(displayed_count, '5')

            demo.click_counter = 10
            displayed_count = click_counter.inspect(DisplayedText())
            self.assertEqual(displayed_count, '10')


# Run the test(s)
unittest.TextTestRunner().run(
    unittest.TestLoader().loadTestsFromTestCase(TestButtonEditorSimpleDemo)
)
