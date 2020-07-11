# -----------------------------------------------------------------------------
#
#  Copyright (c) 2020, Enthought, Inc.
#  All rights reserved.
#
#  This software is provided without warranty under the terms of the BSD
#  license included in LICENSE.txt and may be redistributed only
#  under the conditions described in the aforementioned license.  The license
#  is also available online at http://www.enthought.com/licenses/BSD.txt
#
# -----------------------------------------------------------------------------

import unittest

from traits.api import HasTraits, Int, Str, Tuple
from traitsui.api import Item, View
from traits.testing.api import UnittestTools

from traitsui.tests._tools import (
    create_ui,
    press_ok_button,
    skip_if_not_qt4,
    skip_if_null,
    store_exceptions_on_all_threads,
)


class TupleEditor(HasTraits):
    """Dialog containing a Tuple of two Int's.
    """

    tup = Tuple(Int, Int, Str)

    traits_view = View(
        Item(label="Enter 4 and 6, then press OK"), Item("tup"), buttons=["OK"]
    )


class TestTupleEditor(unittest.TestCase, UnittestTools):

    @skip_if_null
    def test_value_update(self):
        # Regression test for #179
        model = TupleEditor()
        with create_ui(model) as ui:
            with self.assertTraitChanges(model, "tup", count=1):
                model.tup = (3, 4, "nono")

    @skip_if_not_qt4
    def test_qt_tuple_editor(self):
        # Behavior: when editing the text of a tuple editor,
        # value get updated immediately.

        from pyface import qt

        val = TupleEditor()
        with store_exceptions_on_all_threads(), create_ui(val) as ui:

            # the following is equivalent to clicking in the text control of
            # the range editor, enter a number, and clicking ok without
            # defocusing

            # text element inside the spin control
            lineedits = ui.control.findChildren(qt.QtGui.QLineEdit)
            lineedits[0].setFocus()
            lineedits[0].clear()
            lineedits[0].insert("4")
            lineedits[1].setFocus()
            lineedits[1].clear()
            lineedits[1].insert("6")
            lineedits[2].setFocus()
            lineedits[2].clear()
            lineedits[2].insert("fun")

            # if all went well, the tuple trait has been updated and its value
            # is 4
            self.assertEqual(val.tup, (4, 6, "fun"))


if __name__ == "__main__":
    # Executing the file opens the dialog for manual testing
    val = TupleEditor()
    val.configure_traits()
    print(val.tup)
