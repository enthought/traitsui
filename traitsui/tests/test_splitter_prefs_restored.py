# (C) Copyright 2004-2023 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

""" Test the storing/restoration of split group state.
"""

import unittest

from traits.api import Int
from traitsui.api import Action, Group, Handler, HSplit, Item, View
from traitsui.tests._tools import (
    BaseTestMixin,
    create_ui,
    requires_toolkit,
    ToolkitName,
)


class TmpClass(Handler):
    aa = Int(10)
    bb = Int(100)

    def init(self, ui_info):
        super().init(ui_info)
        self.save_prefs(ui_info)
        return True

    def reset_prefs(self, ui_info):
        """Reset the split to be equally wide."""
        control = getattr(ui_info, "h_split").control
        width = control.width()
        control.moveSplitter(width // 2, 1)

    def restore_prefs(self, ui_info):
        """Apply the last saved ui preferences."""
        ui_info.ui.set_prefs(self._prefs)

    def save_prefs(self, ui_info):
        """Save the current ui preferences."""
        self._prefs = ui_info.ui.get_prefs()

    def collapse_right(self, ui_info):
        """Collapse the split to the right."""
        control = getattr(ui_info, "h_split").control
        width = control.width()
        control.moveSplitter(width, 1)

    def collapse_left(self, ui_info):
        """Collapse the split to the left."""
        control = getattr(ui_info, "h_split").control
        control.moveSplitter(0, 1)

    view = View(
        HSplit(
            Group(Item("aa", resizable=True, width=50), show_border=True),
            Group(Item("bb", width=100), show_border=True),
            id="h_split",
        ),
        resizable=True,
        # add actions to test manually.
        buttons=[
            Action(name="collapse left", action="collapse_left"),
            Action(name="collapse right", action="collapse_right"),
            Action(name="reset_layout", action="reset_prefs"),
            Action(name="restore layout", action="restore_prefs"),
            Action(name="save layout", action="save_prefs"),
        ],
        height=300,
        id="test_view_for_splitter_pref_restore",
    )


class TestSplitterPrefsRestored(BaseTestMixin, unittest.TestCase):
    def setUp(self):
        BaseTestMixin.setUp(self)

    def tearDown(self):
        BaseTestMixin.tearDown(self)

    @requires_toolkit([ToolkitName.qt])
    def test_splitter_prefs_are_restored(self):
        # the keys for the splitter prefs (i.e. prefs['h_split']['structure'])
        splitter_keys = ("h_split", "structure")

        def _get_nattr(obj, attr_names=splitter_keys):
            """Utility function to get a value from a nested dict."""
            if obj is None or len(attr_names) == 0:
                return obj
            return _get_nattr(
                obj.get(attr_names[0], None), attr_names=attr_names[1:]
            )

        with create_ui(TmpClass()) as ui:

            handler = ui.handler

            # set the layout to a known state
            handler.reset_prefs(ui.info)

            # save the current layout and check (sanity test)
            handler.save_prefs(ui.info)
            self.assertEqual(
                _get_nattr(handler._prefs), _get_nattr(ui.get_prefs())
            )

            # collapse splitter to right and check prefs has been updated
            handler.collapse_right(ui.info)
            self.assertNotEqual(
                _get_nattr(handler._prefs), _get_nattr(ui.get_prefs())
            )

            # restore the original layout.
            handler.restore_prefs(ui.info)
            self.assertEqual(
                _get_nattr(handler._prefs), _get_nattr(ui.get_prefs())
            )

            # collapse to left and check
            handler.collapse_left(ui.info)
            self.assertNotEqual(
                _get_nattr(handler._prefs), _get_nattr(ui.get_prefs())
            )

            # save the collapsed layout
            handler.save_prefs(ui.info)
            collapsed_splitter_state = _get_nattr(handler._prefs)
            self.assertEqual(
                _get_nattr(handler._prefs), _get_nattr(ui.get_prefs())
            )

        # create a new ui and check that the splitter remembers the last state
        # (collapsed)
        with create_ui(TmpClass()) as ui2:
            self.assertEqual(
                collapsed_splitter_state, _get_nattr(ui2.get_prefs())
            )


if __name__ == "__main__":
    # Execute from command line for manual testing
    # start a session to modify the default layout.
    TmpClass().configure_traits()

    # check visually if the layout changes from the prev. session is
    # restored.
    TmpClass().configure_traits()
