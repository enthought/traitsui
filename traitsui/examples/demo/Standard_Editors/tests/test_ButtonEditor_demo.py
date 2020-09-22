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

# FIXME: Import from api instead
# enthought/traitsui#1173
from traitsui.testing.tester import command
from traitsui.testing.tester.ui_tester import UITester

from traitsui.tests._tools import (
    requires_toolkit,
    ToolkitName,
)

#: Filename of the demo script
FILENAME = "ButtonEditor_demo.py"

#: Path of the demo script
DEMO_PATH = os.path.join(os.path.dirname(__file__), "..", FILENAME)


class TestButtonEditorDemo(unittest.TestCase):

    @requires_toolkit([ToolkitName.qt])
    def test_button_editor_demo(self):
        from pyface.ui.qt4.util.modal_dialog_tester import ModalDialogTester
        from pyface.constant import OK

        # Test ButtonEditor_demo.py in examples/demo/Standard_Edtiors
        demo = runpy.run_path(DEMO_PATH)["demo"]

        tester = UITester()
        with tester.create_ui(demo) as ui:

            simple_button = tester.find_by_id(ui, "simple")
            custom_button = tester.find_by_id(ui, "custom")

            # funcion object for instantiating ModalDialogTester should be a
            # function that opens the dialog
            # we want clicking the buttons to do that
            def click_simple_button():
                simple_button.perform(command.MouseClick())

            def click_custom_button():
                custom_button.perform(command.MouseClick())

            mdtester_simple = ModalDialogTester(click_simple_button)
            mdtester_simple.open_and_run(lambda x: x.click_button(OK))
            self.assertTrue(mdtester_simple.dialog_was_opened)

            mdtester_custom = ModalDialogTester(click_custom_button)
            mdtester_custom.open_and_run(lambda x: x.click_button(OK))
            self.assertTrue(mdtester_custom.dialog_was_opened)


# Run the test(s)
unittest.TextTestRunner().run(
    unittest.TestLoader().loadTestsFromTestCase(TestButtonEditorDemo)
)
