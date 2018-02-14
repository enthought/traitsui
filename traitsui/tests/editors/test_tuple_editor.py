# -*- coding: utf-8 -*-
"""
Created on Fri Sep 20 13:17:20 2013

@author: yves
"""

from __future__ import division, print_function, unicode_literals, absolute_import

from contextlib import contextmanager

from traits.has_traits import HasTraits
from traits.trait_types import Int, Tuple
from traitsui.item import Item
from traitsui.view import View

from traitsui.tests._tools import *


class TupleEditor(HasTraits):
    """Dialog containing a Tuple of two Int's.
    """

    tup = Tuple(Int, Int)

    traits_view = View(
        Item(label="Enter 4 and 6, then press OK"),
        Item('tup'),
        buttons=['OK']
    )


@skip_if_not_qt4
def test_qt_tuple_editor():
    # Behavior: when editing the text of a tuple editor,
    # value get updated immediately.

    from pyface import qt

    with store_exceptions_on_all_threads():
        val = TupleEditor()
        ui = val.edit_traits()

        # the following is equivalent to clicking in the text control of the
        # range editor, enter a number, and clicking ok without defocusing

        # text element inside the spin control
        lineedits = ui.control.findChildren(qt.QtGui.QLineEdit)
        lineedits[0].setFocus()
        lineedits[0].clear()
        lineedits[0].insert('4')
        lineedits[1].setFocus()
        lineedits[1].clear()
        lineedits[1].insert('6')

        # if all went well, the tuple trait has been updated and its value is 4
        assert val.tup == (4, 6)

        # press the OK button and close the dialog
        press_ok_button(ui)


if __name__ == '__main__':
    # Executing the file opens the dialog for manual testing
    val = TupleEditor()
    val.configure_traits()
    print(val.tup)
