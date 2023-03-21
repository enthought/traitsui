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
This example demonstrates how to test a simple application using UI Tester.

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
FILENAME = "converter.py"

#: Path of the demo script
DEMO_PATH = os.path.join(os.path.dirname(__file__), "..", FILENAME)


class TestConverter(unittest.TestCase):
    def test_converter(self):
        demo = runpy.run_path(DEMO_PATH)["popup"]
        tester = UITester()
        with tester.create_ui(demo) as ui:
            input_amount = tester.find_by_name(ui, "input_amount")
            output_amount = tester.find_by_name(ui, "output_amount")
            for _ in range(4):
                input_amount.perform(KeyClick("Backspace"))
            input_amount.perform(KeySequence("14.0"))
            self.assertEqual(
                output_amount.inspect(DisplayedText())[:4],
                "1.16",
            )
            tester.find_by_id(ui, "Undo").perform(MouseClick())
            self.assertEqual(
                output_amount.inspect(DisplayedText()),
                "1.0",
            )


# Run the test(s)
unittest.TextTestRunner().run(
    unittest.TestLoader().loadTestsFromTestCase(TestConverter)
)
