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
#  Date:   Jan 2012
#
#------------------------------------------------------------------------------

"""
Test case for bug (wx, Mac OS X)

A RangeEditor in mode 'text' for an Int allows values out of range.
"""

from __future__ import print_function

from traits.has_traits import HasTraits
from traits.trait_types import Int
from traitsui.item import Item
from traitsui.view import View
from traitsui.editors.range_editor import RangeEditor

from traitsui.tests._tools import *


class NumberWithTextEditor(HasTraits):
    """Dialog containing a RangeEditor in 'spinner' mode for an Int.
    """

    number = Int

    traits_view = View(
        Item(label="Range should be 3 to 8. Enter 1, then press OK"),
        Item('number', editor=RangeEditor(low=3, high=8, mode='text')),
        buttons = ['OK']
    )


@skip_if_not_wx
def test_wx_spin_control_editing():
    # behavior: when editing the text part of a spin control box, pressing
    # the OK button should update the value of the HasTraits class
    # (tests a bug where this fails with an AttributeError)

    with store_exceptions_on_all_threads():
        num = NumberWithTextEditor()
        ui = num.edit_traits()

        # the following is equivalent to setting the text in the text control,
        # then pressing OK

        textctrl = ui.control.FindWindowByName('text')
        textctrl.SetValue('1')

        # press the OK button and close the dialog
        press_ok_button(ui)

    # the number traits should be between 3 and 8
    assert num.number >= 3 and num.number <=8


if __name__ == '__main__':
    # Executing the file opens the dialog for manual testing
    num = NumberWithTextEditor()
    num.configure_traits()
    print(num.number)
