#------------------------------------------------------------------------------
#
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#
#  This software is provided without warranty under the terms of the BSD
#  license included in enthought/LICENSE.txt and may be redistributed only
#  under the conditions described in the aforementioned license.  The license
#  is also available online at http://www.enthought.com/licenses/BSD.txt
#
#  Author: Pietro Berkes
#  Date:   Feb 2012
#
#------------------------------------------------------------------------------

"""
Test the layout of elements is consistent with the layout parameters.
"""

from traits.has_traits import HasTraits
from traits.trait_types import Str

from traitsui.item import Item
from traitsui.view import View
from traitsui.group import HGroup, VGroup

from traitsui.tests._tools import *


_DIALOG_WIDTH = 500
_DIALOG_HEIGHT = 500
_TXT_WIDTH = 100

class VResizeDialog(HasTraits):

    txt = Str('hallo')

    traits_view = View(
        VGroup(
            Item('txt', width=_TXT_WIDTH, resizable=True),
        ),
        width  = _DIALOG_WIDTH,
        height = _DIALOG_HEIGHT,
        resizable=True
    )


class HResizeDialog(HasTraits):

    txt = Str('hallo')

    traits_view = View(
        HGroup(
            Item('txt', width=_TXT_WIDTH, resizable=True),
        ),
        width  = _DIALOG_WIDTH,
        height = _DIALOG_HEIGHT,
        resizable=True
    )


@skip_if_not_qt4
def test_qt_resizable_in_vgroup():
    # Behavior: Item.resizable controls whether a component can resize along
    # the non-layout axis of its group. In a VGroup, resizing should work
    # only in the horizontal direction.

    from pyface import qt

    with store_exceptions_on_all_threads():
        dialog = VResizeDialog()
        ui = dialog.edit_traits()

        text = ui.control.findChild(qt.QtGui.QLineEdit)

        # horizontal size should be large
        nose.tools.assert_greater(text.width(), _DIALOG_WIDTH-100)

        # vertical size should be unchanged
        nose.tools.assert_less(text.height(), 100)


@skip_if_not_qt4
def test_qt_resizable_in_hgroup():
    # Behavior: Item.resizable controls whether a component can resize along
    # the non-layout axis of its group. In a HGroup, resizing should work
    # only in the vertical direction.

    from pyface import qt

    with store_exceptions_on_all_threads():
        dialog = HResizeDialog()
        ui = dialog.edit_traits()

        text = ui.control.findChild(qt.QtGui.QLineEdit)

        # vertical size should be large
        nose.tools.assert_greater(text.height(), _DIALOG_HEIGHT-100)

        # horizontal size should be unchanged
        # ??? maybe not: some elements (e.g., the text field) have
        # 'Expanding' as their default behavior
        #nose.tools.assert_less(text.width(), _TXT_WIDTH+100)


if __name__ == "__main__":
    # Execute from command line for manual testing
    vw = VResizeDialog()
    vw.configure_traits()
