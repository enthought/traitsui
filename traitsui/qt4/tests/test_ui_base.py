# Copyright (c) 2019, Enthought Inc.
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only
# under the conditions described in the aforementioned license.  The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
# Thanks for using Enthought open source!

import unittest

from traits.api import HasTraits, Int
from traitsui.api import Item, View
from traitsui.tests._tools import (
    create_ui,
    skip_if_not_qt4,
)


class ObjectWithNumber(HasTraits):
    number = Int()


@skip_if_not_qt4
class TestStickyDialog(unittest.TestCase):
    """ Test _StickyDialog used by the UI's Qt backend.
    """

    def test_sticky_dialog_with_parent(self):
        obj = ObjectWithNumber()
        obj2 = ObjectWithNumber()
        parent_view = View(Item("number"), title="Parent")
        nested = View(
            Item("number"),
            resizable=True,
            title="Nested"
        )
        with create_ui(obj, dict(view=parent_view)) as ui:
            with create_ui(obj2, dict(parent=ui.control, view=nested)) as ui2:
                from pyface.qt import QtCore
                self.assertTrue(ui2.control.windowFlags() & QtCore.Qt.Dialog)
