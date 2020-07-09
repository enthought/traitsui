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
Test the layout of elements is consistent with the layout parameters.
"""

import unittest

from traits.has_traits import HasTraits
from traits.trait_types import Str

from traitsui.item import Item
from traitsui.view import View
from traitsui.group import HGroup, VGroup

from traitsui.tests._tools import (
    create_ui,
    skip_if_not_qt4,
    skip_if_null,
    store_exceptions_on_all_threads,
)


_DIALOG_WIDTH = 500
_DIALOG_HEIGHT = 500
_TXT_WIDTH = 100


class MultipleTrait(HasTraits):
    """ An object with multiple traits to test layout and alignments."""

    txt1 = Str("text1")
    txt2 = Str("text2")


class VResizeDialog(HasTraits):

    txt = Str("hallo")

    traits_view = View(
        VGroup(Item("txt", width=_TXT_WIDTH, resizable=True)),
        width=_DIALOG_WIDTH,
        height=_DIALOG_HEIGHT,
        resizable=True,
    )


class HResizeDialog(HasTraits):

    txt = Str("hallo")

    traits_view = View(
        HGroup(Item("txt", width=_TXT_WIDTH, resizable=True)),
        width=_DIALOG_WIDTH,
        height=_DIALOG_HEIGHT,
        resizable=True,
    )


class TestLayout(unittest.TestCase):

    @skip_if_not_qt4
    def test_qt_resizable_in_vgroup(self):
        # Behavior: Item.resizable controls whether a component can resize
        # along the non-layout axis of its group. In a VGroup, resizing should
        # work only in the horizontal direction.

        from pyface import qt

        with store_exceptions_on_all_threads(), \
                create_ui(VResizeDialog()) as ui:
            editor, = ui.get_editors("txt")
            text = editor.control

            # horizontal size should be large
            self.assertGreater(text.width(), _DIALOG_WIDTH - 100)

            # vertical size should be unchanged
            self.assertLess(text.height(), 100)

    @skip_if_not_qt4
    def test_qt_resizable_in_hgroup(self):
        # Behavior: Item.resizable controls whether a component can resize
        # along the non-layout axis of its group. In a HGroup, resizing should
        # work only in the vertical direction.

        from pyface import qt

        with store_exceptions_on_all_threads(), \
                create_ui(HResizeDialog()) as ui:

            editor, = ui.get_editors("txt")
            text = editor.control

            # vertical size should be large
            self.assertGreater(text.height(), _DIALOG_HEIGHT - 100)

            # horizontal size should be unchanged
            # ??? maybe not: some elements (e.g., the text field) have
            # 'Expanding' as their default behavior
            # self.assertLess(text.width(), _TXT_WIDTH+100)


@skip_if_null
class TestOrientation(unittest.TestCase):
    """ Toolkit-agnostic tests on the layout orientations."""

    def test_vertical_layout(self):
        view = View(
            VGroup(
                Item("txt1"),
                Item("txt2"),
            )
        )
        with store_exceptions_on_all_threads(), \
                create_ui(MultipleTrait(), ui_kwargs=dict(view=view)):
            pass

    def test_horizontal_layout(self):
        # layout
        view = View(
            HGroup(
                Item("txt1"),
                Item("txt2"),
            )
        )
        with store_exceptions_on_all_threads(), \
                create_ui(MultipleTrait(), ui_kwargs=dict(view=view)):
            pass


if __name__ == "__main__":
    # Execute from command line for manual testing
    vw = VResizeDialog()
    vw.configure_traits()
