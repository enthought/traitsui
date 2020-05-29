# ------------------------------------------------------------------------------
#
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#
#  This software is provided without warranty under the terms of the BSD
#  license included in LICENSE.txt and may be redistributed only
#  under the conditions described in the aforementioned license.  The license
#  is also available online at http://www.enthought.com/licenses/BSD.txt
#
#  Author: Pietro Berkes
#  Date:   Feb 2012
#
# ------------------------------------------------------------------------------

"""
Test the creation and layout of labels.
"""
import unittest

from traits.has_traits import HasTraits
from traits.trait_types import Bool, Str
from traitsui.view import View
from traitsui.item import Item
from traitsui.group import VGroup, HGroup

from traitsui.tests._tools import (
    is_control_enabled,
    is_current_backend_qt4,
    skip_if_not_qt4,
    skip_if_null,
    store_exceptions_on_all_threads,
)


_DIALOG_WIDTH = 500


class ShowRightLabelsDialog(HasTraits):
    """ Dialog with labels on the left/right to test the label text.
    """

    bool_item = Bool(True)

    traits_view = View(
        VGroup(
            VGroup(Item("bool_item"), show_left=False),
            VGroup(Item("bool_item"), show_left=True),
        )
    )


class HResizeTestDialog(HasTraits):
    """ Dialog with checkbox and text elements and labels on the right.
    We test the separation between element and label in HGroups.
    """

    bool_item = Bool(True)
    txt_item = Str()

    traits_view = View(
        VGroup(
            HGroup(Item("bool_item", springy=True), show_left=False),
            VGroup(Item("txt_item", resizable=True), show_left=False),
        ),
        width=_DIALOG_WIDTH,
        height=100,
        resizable=True,
    )


class VResizeTestDialog(HasTraits):
    """ Dialog with checkbox and text elements and labels on the right.
    We test the separation between element and label in VGroups.
    """

    bool_item = Bool(True)
    txt_item = Str()

    traits_view = View(
        VGroup(
            VGroup(Item("bool_item", resizable=True), show_left=False),
            VGroup(Item("txt_item", resizable=True), show_left=False),
        ),
        width=_DIALOG_WIDTH,
        height=100,
        resizable=True,
    )


class NoLabelResizeTestDialog(HasTraits):
    """ Test the combination show_label=False, show_left=False.
    """

    bool_item = Bool(True)

    traits_view = View(
        VGroup(
            Item("bool_item", resizable=True, show_label=False),
            show_left=False,
        ),
        resizable=True,
    )


class EnableWhenDialog(HasTraits):
    """ Test labels for enable when. """

    bool_item = Bool(True)

    labelled_item = Str("test")

    unlabelled_item = Str("test")

    traits_view = View(
        VGroup(
            Item("bool_item"),
            Item("labelled_item", enabled_when="bool_item"),
            Item(
                "unlabelled_item", enabled_when="bool_item", show_label=False
            ),
        ),
        resizable=True,
    )


class TestLabels(unittest.TestCase):

    @skip_if_not_qt4
    def test_qt_show_labels_right_without_colon(self):
        # Behavior: traitsui should not append a colon ':' to labels
        # that are shown to the *right* of the corresponding elements

        from pyface import qt

        with store_exceptions_on_all_threads():
            dialog = ShowRightLabelsDialog()
            ui = dialog.edit_traits()

            # get reference to label objects
            labels = ui.control.findChildren(qt.QtGui.QLabel)

            # the first is shown to the right, so no colon
            self.assertFalse(labels[0].text().endswith(":"))

            # the second is shown to the right, it should have a colon
            self.assertTrue(labels[1].text().endswith(":"))

    def _test_qt_labels_right_resizing(self, dialog_class):
        # Bug: In the Qt backend, resizing a checkbox element with a label on
        # the right resizes the checkbox, even though it cannot be.
        # The final effect is that the label remains attached to the right
        # margin, with a big gap between it and the checkbox. In this case, the
        # label should be made resizable instead.
        # On the other hand, a text element should keep the current behavior
        # and resize.

        from pyface import qt

        with store_exceptions_on_all_threads():
            dialog = dialog_class()
            ui = dialog.edit_traits()

            # all labels
            labels = ui.control.findChildren(qt.QtGui.QLabel)

            # the checkbox and its label should be close to one another; the
            # size of the checkbox should be small
            checkbox_label = labels[0]
            checkbox = ui.control.findChild(qt.QtGui.QCheckBox)

            # horizontal space between checkbox and label should be small
            h_space = checkbox_label.x() - checkbox.x()
            self.assertLess(h_space, 100)
            # and the checkbox size should also be small
            self.assertLess(checkbox.width(), 100)

            # the text item and its label should be close to one another; the
            # size of the text item should be large
            text_label = labels[0]
            text = ui.control.findChild(qt.QtGui.QLineEdit)

            # horizontal space between text and label should be small
            h_space = text_label.x() - text.x()
            self.assertLess(h_space, 100)
            # and the text item size should be large
            self.assertGreater(text.width(), _DIALOG_WIDTH - 200)

            # the size of the window should still be 500
            self.assertEqual(ui.control.width(), _DIALOG_WIDTH)

    @skip_if_not_qt4
    def test_qt_labels_right_resizing_vertical(self):
        self._test_qt_labels_right_resizing(VResizeTestDialog)

    @skip_if_not_qt4
    def test_qt_labels_right_resizing_horizontal(self):
        self._test_qt_labels_right_resizing(HResizeTestDialog)

    @skip_if_not_qt4
    def test_qt_no_labels_on_the_right_bug(self):
        # Bug: If one set show_left=False, show_label=False on a non-resizable
        # item like a checkbox, the Qt backend tried to set the label's size
        # policy and failed because label=None.

        with store_exceptions_on_all_threads():
            dialog = NoLabelResizeTestDialog()
            ui = dialog.edit_traits()

    @skip_if_null
    def test_labels_enabled_when(self):
        # Behaviour: label should enable/disable along with editor

        with store_exceptions_on_all_threads():
            dialog = EnableWhenDialog()
            ui = dialog.edit_traits()

            labelled_editor = ui.get_editors("labelled_item")[0]

            if is_current_backend_qt4():
                unlabelled_editor = ui.get_editors("unlabelled_item")[0]
                self.assertIsNone(unlabelled_editor.label_control)

            self.assertTrue(is_control_enabled(labelled_editor.label_control))

            dialog.bool_item = False

            self.assertFalse(is_control_enabled(labelled_editor.label_control))

            dialog.bool_item = True

            ui.dispose()


if __name__ == "__main__":
    # Execute from command line for manual testing
    vw = HResizeTestDialog()
    vw.configure_traits()
