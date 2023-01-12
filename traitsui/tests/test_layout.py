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
Test the layout of elements is consistent with the layout parameters.
"""

import unittest

from traits.api import Enum, HasTraits, Str

from traitsui.item import Item, UItem
from traitsui.view import View
from traitsui.group import HGroup, VGroup
from traitsui.testing.api import UITester
from traitsui.tests._tools import (
    BaseTestMixin,
    create_ui,
    requires_toolkit,
    reraise_exceptions,
    ToolkitName,
)


_DIALOG_WIDTH = 500
_DIALOG_HEIGHT = 500
_TXT_WIDTH = 100


class MultipleTrait(HasTraits):
    """An object with multiple traits to test layout and alignments."""

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


class ObjectWithResizeReadonlyItem(HasTraits):
    resizable_readonly_item = Enum("first", "second")

    def default_traits_view(self):
        return View(
            VGroup(
                UItem(
                    "resizable_readonly_item",
                    resizable=True,
                    style="readonly",
                ),
            ),
            height=_DIALOG_HEIGHT,
            width=_DIALOG_WIDTH,
        )


class TestLayout(BaseTestMixin, unittest.TestCase):
    def setUp(self):
        BaseTestMixin.setUp(self)

    def tearDown(self):
        BaseTestMixin.tearDown(self)

    @requires_toolkit([ToolkitName.qt])
    def test_qt_resizable_in_vgroup(self):
        # Behavior: Item.resizable controls whether a component can resize
        # along the non-layout axis of its group. In a VGroup, resizing should
        # work only in the horizontal direction.

        with reraise_exceptions(), create_ui(VResizeDialog()) as ui:
            (editor,) = ui.get_editors("txt")
            text = editor.control

            # horizontal size should be large
            self.assertGreater(text.width(), _DIALOG_WIDTH - 100)

            # vertical size should be unchanged
            self.assertLess(text.height(), 100)

    @requires_toolkit([ToolkitName.qt])
    def test_qt_resizable_in_hgroup(self):
        # Behavior: Item.resizable controls whether a component can resize
        # along the non-layout axis of its group. In a HGroup, resizing should
        # work only in the vertical direction.

        with reraise_exceptions(), create_ui(HResizeDialog()) as ui:

            (editor,) = ui.get_editors("txt")
            text = editor.control

            # vertical size should be large
            self.assertGreater(text.height(), _DIALOG_HEIGHT - 100)

            # horizontal size should be unchanged
            # ??? maybe not: some elements (e.g., the text field) have
            # 'Expanding' as their default behavior
            # self.assertLess(text.width(), _TXT_WIDTH+100)

    # regression test for enthought/traitsui#1528
    @requires_toolkit([ToolkitName.qt])
    def test_qt_resizable_readonly_item(self):
        tester = UITester()
        with tester.create_ui(ObjectWithResizeReadonlyItem()) as ui:
            resizable_readonly_item = tester.find_by_name(
                ui, "resizable_readonly_item"
            )
            # for resizable item expansion should occur in horizontal but not
            # vertical direction
            self.assertLess(
                resizable_readonly_item._target.control.height(),
                _DIALOG_HEIGHT,
            )
            self.assertEqual(
                resizable_readonly_item._target.control.width(), _DIALOG_WIDTH
            )


@requires_toolkit([ToolkitName.qt, ToolkitName.wx])
class TestOrientation(BaseTestMixin, unittest.TestCase):
    """Toolkit-agnostic tests on the layout orientations."""

    def setUp(self):
        BaseTestMixin.setUp(self)

    def tearDown(self):
        BaseTestMixin.tearDown(self)

    def test_vertical_layout(self):
        view = View(
            VGroup(
                Item("txt1"),
                Item("txt2"),
            )
        )
        with reraise_exceptions(), create_ui(
            MultipleTrait(), ui_kwargs=dict(view=view)
        ):
            pass

    def test_horizontal_layout(self):
        # layout
        view = View(
            HGroup(
                Item("txt1"),
                Item("txt2"),
            )
        )
        with reraise_exceptions(), create_ui(
            MultipleTrait(), ui_kwargs=dict(view=view)
        ):
            pass


if __name__ == "__main__":
    # Execute from command line for manual testing
    vw = VResizeDialog()
    vw.configure_traits()
