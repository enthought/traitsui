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
It also demonstarates the use of UI Tester, together with pyface's
ModalDialogTester.

The GUI being tested is written in the demo under the same name (minus the
preceding 'test') in the outer directory.
"""

import os
import runpy
import unittest

from pyface.toolkit import toolkit_object
from pyface.constant import OK

from traitsui.testing.api import MouseClick, UITester

ModalDialogTester = toolkit_object(
    "util.modal_dialog_tester:ModalDialogTester"
)
no_modal_dialog_tester = ModalDialogTester.__name__ == "Unimplemented"

#: Filename of the demo script
FILENAME = "ButtonEditor_demo.py"

#: Path of the demo script
DEMO_PATH = os.path.join(os.path.dirname(__file__), "..", FILENAME)


@unittest.skipIf(no_modal_dialog_tester, "ModalDialogTester unavailable")
class TestButtonEditorDemo(unittest.TestCase):
    def test_button_editor_demo_simple(self):
        demo = runpy.run_path(DEMO_PATH)["demo"]

        tester = UITester()
        with tester.create_ui(demo) as ui:

            simple_button = tester.find_by_id(ui, "simple")

            # funcion object for instantiating ModalDialogTester should be a
            # function that opens the dialog
            # we want clicking the buttons to do that
            def click_simple_button():
                simple_button.perform(MouseClick())

            mdtester_simple = ModalDialogTester(click_simple_button)
            mdtester_simple.open_and_run(lambda x: x.click_button(OK))
            self.assertTrue(mdtester_simple.dialog_was_opened)

    def test_button_editor_demo_custom(self):
        demo = runpy.run_path(DEMO_PATH)["demo"]

        tester = UITester()
        with tester.create_ui(demo) as ui:

            custom_button = tester.find_by_id(ui, "custom")

            # funcion object for instantiating ModalDialogTester should be a
            # function that opens the dialog
            # we want clicking the buttons to do that
            def click_custom_button():
                custom_button.perform(MouseClick())

            mdtester_custom = ModalDialogTester(click_custom_button)
            mdtester_custom.open_and_run(lambda x: x.click_button(OK))
            self.assertTrue(mdtester_custom.dialog_was_opened)


# Run the test(s)
unittest.TextTestRunner().run(
    unittest.TestLoader().loadTestsFromTestCase(TestButtonEditorDemo)
)
