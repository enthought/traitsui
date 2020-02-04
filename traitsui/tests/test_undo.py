#  Copyright (c) 2019-20, Enthought, Inc.
#  All rights reserved.
#
#  This software is provided without warranty under the terms of the BSD
#  license included in LICENSE.txt and may be redistributed only
#  under the conditions described in the aforementioned license.  The license
#  is also available online at http://www.enthought.com/licenses/BSD.txt
#
#  Thanks for using Enthought open source!
#
#  Author: Midhun PM
#  Date:   February 04, 2020

import functools
import unittest

from pyface.toolkit import toolkit_object

from traitsui.tests.test_editor import create_editor
from traitsui.undo import UndoHistory

GuiTestAssistant = toolkit_object("util.gui_test_assistant:GuiTestAssistant")
no_gui_test_assistant = GuiTestAssistant.__name__ == "Unimplemented"
if no_gui_test_assistant:

    # ensure null toolkit has an inheritable GuiTestAssistant
    class GuiTestAssistant(object):
        pass


@unittest.skipIf(no_gui_test_assistant, "No GuiTestAssistant")
class TestEditorUndo(GuiTestAssistant, unittest.TestCase):

    def check_history(self, editor, expected_history_now,
                      expected_history_length):
        return (editor.ui.history.now == expected_history_now and
                len(editor.ui.history.history) == expected_history_length)

    def test_undo(self):
        editor = create_editor()
        editor.prepare(None)
        editor.ui.history = UndoHistory()

        self.assertEqual(editor.old_value, "test")

        # Enter "ab"
        with editor.updating_value():
            self.gui.set_trait_later(editor.control, "control_value", "a")
            self.gui.set_trait_later(editor.control, "control_value", "ab")

        # Perform an UNDO
        self.gui.invoke_later(editor.ui.history.undo)
        self.event_loop_helper.event_loop_with_timeout()

        # Expect 2 items in history and pointer at first item
        self.assertEventuallyTrue(editor, "ui",
                                  functools.partial(self.check_history,
                                                    expected_history_now=1,
                                                    expected_history_length=2),
                                  timeout=5.0)

        # Perform a REDO
        self.gui.invoke_later(editor.ui.history.redo)
        self.event_loop_helper.event_loop_with_timeout()

        # Expect 2 items in history and pointer at second item
        self.assertEventuallyTrue(editor, "ui",
                                  functools.partial(self.check_history,
                                                    expected_history_now=2,
                                                    expected_history_length=2),
                                  timeout=5.0)

        # Enter a new character 'c' at the end
        with editor.updating_value():
            self.gui.set_trait_later(editor.control, "control_value", "abc")

        # Perform an UNDO
        self.gui.invoke_later(editor.ui.history.undo)
        self.event_loop_helper.event_loop_with_timeout()

        # Expect 3 items in history and pointer at second item
        self.assertEventuallyTrue(editor, "ui",
                                  functools.partial(self.check_history,
                                                    expected_history_now=2,
                                                    expected_history_length=3),
                                  timeout=5.0)

        # Enter a new character 'd' at the end
        with editor.updating_value():
            self.gui.set_trait_later(editor.control, "control_value", "abd")
        self.event_loop_helper.event_loop_with_timeout()

        # Expect 3 items in history and pointer at second item
        self.assertEventuallyTrue(editor, "ui",
                                  functools.partial(self.check_history,
                                                    expected_history_now=3,
                                                    expected_history_length=3),
                                  timeout=5.0)
