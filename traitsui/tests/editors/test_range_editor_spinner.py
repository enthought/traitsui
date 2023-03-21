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
Test case for bug (wx, Mac OS X)

Editing the text part of a spin control box and pressing the OK button
without de-focusing raises an AttributeError::

    Traceback (most recent call last):
    File "ETS/traitsui/traitsui/wx/range_editor.py", line 783, in update_object
        self.value = self.control.GetValue()
    AttributeError: 'NoneType' object has no attribute 'GetValue'
"""
import unittest

from traits.has_traits import HasTraits
from traits.trait_types import Int
from traitsui.item import Item
from traitsui.view import View
from traitsui.editors.range_editor import RangeEditor

from traitsui.tests._tools import (
    BaseTestMixin,
    create_ui,
    requires_toolkit,
    reraise_exceptions,
    ToolkitName,
)


class NumberWithSpinnerEditor(HasTraits):
    """Dialog containing a RangeEditor in 'spinner' mode for an Int."""

    number = Int()

    traits_view = View(
        Item(label="Enter 4, then press OK without defocusing"),
        Item("number", editor=RangeEditor(low=3, high=8, mode="spinner")),
        buttons=["OK"],
    )


class TestRangeEditorSpinner(BaseTestMixin, unittest.TestCase):
    def setUp(self):
        BaseTestMixin.setUp(self)

    def tearDown(self):
        BaseTestMixin.tearDown(self)

    @requires_toolkit([ToolkitName.wx])
    def test_wx_spin_control_editing_should_not_crash(self):
        # Bug: when editing the text part of a spin control box, pressing
        # the OK button raises an AttributeError on Mac OS X

        num = NumberWithSpinnerEditor()
        try:
            with reraise_exceptions(), create_ui(num) as ui:

                # the following is equivalent to clicking in the text control
                # of the range editor, enter a number, and clicking ok without
                # defocusing

                # SpinCtrl object
                spin = ui.control.FindWindowByName("wxSpinCtrl", ui.control)
                spin.SetFocusFromKbd()

                # on Windows, a wxSpinCtrl does not have children, and we
                # cannot do the more fine-grained testing below
                if len(spin.GetChildren()) == 0:
                    spin.SetValue("4")
                else:
                    # TextCtrl object of the spin control
                    spintxt = spin.FindWindowByName("text", spin)
                    spintxt.SetValue("4")

        except AttributeError:
            # if all went well, we should not be here
            self.fail("AttributeError raised")

    @requires_toolkit([ToolkitName.qt])
    def test_qt_spin_control_editing(self):
        # Behavior: when editing the text part of a spin control box, pressing
        # the OK button updates the value of the HasTraits class

        from pyface import qt

        num = NumberWithSpinnerEditor()
        with reraise_exceptions(), create_ui(num) as ui:

            # the following is equivalent to clicking in the text control of
            # the range editor, enter a number, and clicking ok without
            # defocusing

            # text element inside the spin control
            lineedit = ui.control.findChild(qt.QtGui.QLineEdit)
            lineedit.setFocus()
            lineedit.setText("4")

        # if all went well, the number traits has been updated and its value is
        # 4
        self.assertEqual(num.number, 4)


if __name__ == "__main__":
    # Executing the file opens the dialog for manual testing
    num = NumberWithSpinnerEditor()
    num.configure_traits()
    print(num.number)
