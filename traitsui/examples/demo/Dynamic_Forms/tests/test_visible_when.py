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
This example demonstrates how to test the use of visible_when to make UI
components visible or not

The GUI being tested is written in the demo under the same name (minus the
preceding 'test') in the outer directory.
"""

import os
import runpy
import unittest

from traitsui.testing.api import IsVisible, UITester

#: Filename of the demo script
FILENAME = "visible_when.py"

#: Path of the demo script
DEMO_PATH = os.path.join(os.path.dirname(__file__), "..", FILENAME)


class TestVisibleWhenDemo(unittest.TestCase):
    def test_visible_when_demo(self):
        demo = runpy.run_path(DEMO_PATH)["demo"]

        tester = UITester()
        with tester.create_ui(demo) as ui:
            # person should be 16 by default
            self.assertLess(demo.age, 18)

            marital_status_field = tester.find_by_name(ui, 'marital_status')
            legal_guardian_field = tester.find_by_name(ui, 'legal_guardian')
            self.assertFalse(marital_status_field.inspect(IsVisible()))
            self.assertTrue(legal_guardian_field.inspect(IsVisible()))

            # UITester is yet to support SimpleSpinEditor so we change the
            # value of the trait directly
            demo.age = 20

            registered_voter_field = tester.find_by_name(
                ui, 'registered_voter'
            )
            school_field = tester.find_by_name(ui, 'school')
            self.assertTrue(registered_voter_field.inspect(IsVisible()))
            self.assertFalse(school_field.inspect(IsVisible()))


# Run the test(s)
unittest.TextTestRunner().run(
    unittest.TestLoader().loadTestsFromTestCase(TestVisibleWhenDemo)
)
