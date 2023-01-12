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
Test the layout when element appear and disappear with visible_when.
"""

import unittest

from traits.has_traits import HasTraits
from traits.trait_types import Enum, Bool, Str

from traitsui.group import HGroup, VGroup
from traitsui.include import Include
from traitsui.item import Item
from traitsui.view import View

from traitsui.tests._tools import (
    BaseTestMixin,
    create_ui,
    get_dialog_size,
    requires_toolkit,
    reraise_exceptions,
    ToolkitName,
)

_TEXT_WIDTH = 200
_TEXT_HEIGHT = 100


class VisibleWhenProblem(HasTraits):

    which = Enum("one", "two")

    on = Bool()
    txt = Str()

    onoff_group = HGroup(
        VGroup(
            Item("on", resizable=False, width=-100, height=-70),
            show_left=False,
            show_border=True,
            visible_when='which == "one"',
        )
    )

    text_group = VGroup(
        Item("txt", width=-_TEXT_WIDTH, height=-_TEXT_HEIGHT),
        visible_when='which == "two"',
        show_border=True,
    )

    traits_view = View(
        Item("which"),
        VGroup(Include("onoff_group"), Include("text_group")),
        resizable=True,
        buttons=["OK", "Cancel"],
    )


# XXX Not fixing on wx - CJW
# This layout issue was fixed for Qt, but not for Wx.
# See https://github.com/enthought/traitsui/pull/56
# This is cosmetic, not trivial to fix, and the Wx backend is currently low
# priority.  Patches which make this work on Wx will be gladly accepted, but
# there are no current plans to work on this.


class TestVisibleWhenLayout(BaseTestMixin, unittest.TestCase):
    def setUp(self):
        BaseTestMixin.setUp(self)

    def tearDown(self):
        BaseTestMixin.tearDown(self)

    @requires_toolkit([ToolkitName.qt])
    def test_visible_when_layout(self):
        # Bug: The size of a dialog that contains elements that are activated
        # by "visible_when" can end up being the *sum* of the sizes of the
        # elements, even though the elements are mutually exclusive (e.g.,
        # a typical case is a dropbox that lets you select different cases).
        # The expected behavior is that the size of the dialog should be at
        # most the size of the largest combination of elements.

        dialog = VisibleWhenProblem()
        with reraise_exceptions(), create_ui(dialog) as ui:

            # have the dialog switch from group one to two and back to one
            dialog.which = "two"
            dialog.which = "one"

            # the size of the window should not be larger than the largest
            # combination (in this case, the `text_group` plus the `which` item
            size = get_dialog_size(ui.control)
            # leave some margin for labels, dropbox, etc
            self.assertLess(size[0], _TEXT_WIDTH + 100)
            self.assertLess(size[1], _TEXT_HEIGHT + 150)


if __name__ == "__main__":
    # Execute from command line for manual testing
    vw = VisibleWhenProblem(txt="ciao")
    ui = vw.configure_traits()
