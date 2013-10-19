#------------------------------------------------------------------------------
#
#  Copyright (c) 2013, Enthought, Inc.
#  All rights reserved.
#
#  This software is provided without warranty under the terms of the BSD
#  license included in enthought/LICENSE.txt and may be redistributed only
#  under the conditions described in the aforementioned license.  The license
#  is also available online at http://www.enthought.com/licenses/BSD.txt
#
#  Author: Corran Webster
#  Date:   Oct 2013
#
#------------------------------------------------------------------------------

"""
Test case for bug (wx, Mac OS X)

A ListStrEditor was not checking for valid item indexes under Wx.  This was
most noticeable when the selected_index was set in the editor factory.
"""

from traits.has_traits import HasTraits
from traits.trait_types import List, Int, Str
from traitsui.item import Item
from traitsui.view import View
from traitsui.editors.list_str_editor import ListStrEditor

from traitsui.tests._tools import *


class ListStrEditorWithSelectedIndex(HasTraits):
    values = List(Str())
    selected_index = Int()
    selected_indices = List(Int())

single_select_view = View(
    Item('values',
        show_label=False,
        editor=ListStrEditor(
            selected_index='selected_index',
            editable=False),
    ),
    buttons=['OK'])
        
multi_select_view = View(
    Item('values',
        show_label=False,
        editor=ListStrEditor(
            multi_select=True,
            selected_index='selected_indices',
            editable=False),
    ),
    buttons=['OK'])
        
def get_selected(control):
    """ Returns a list of the indices of all currently selected list items.
    """
    import wx
    selected = []
    item     = -1
    while True:
        item = control.GetNextItem(item, wx.LIST_NEXT_ALL,
                                    wx.LIST_STATE_SELECTED)
        if item == -1:
            break;
        selected.append(item)
    return selected

@skip_if_not_wx
def test_wx_list_str_selected_index():
    # behavior: when starting up, the

    with store_exceptions_on_all_threads():
        obj = ListStrEditorWithSelectedIndex(
                values=['value1', 'value2'],
                selected_index=1)
        ui = obj.edit_traits(view=single_select_view)

        # the following is equivalent to setting the text in the text control,
        # then pressing OK

        liststrctrl = ui.control.FindWindowByName('listCtrl')
        selected_1 = get_selected(liststrctrl)
        
        obj.selected_index = 0
        selected_2 = get_selected(liststrctrl)

        # press the OK button and close the dialog
        press_ok_button(ui)

    # the number traits should be between 3 and 8
    assert selected_1 == [1]
    assert selected_2 == [0]

@skip_if_not_wx
def test_wx_list_str_multi_selected_index():
    # behavior: when starting up, the

    with store_exceptions_on_all_threads():
        obj = ListStrEditorWithSelectedIndex(
                values=['value1', 'value2'],
                selected_indices=[1])
        ui = obj.edit_traits(view=multi_select_view)

        # the following is equivalent to setting the text in the text control,
        # then pressing OK

        liststrctrl = ui.control.FindWindowByName('listCtrl')
        selected_1 = get_selected(liststrctrl)
        
        obj.selected_indices = [0]
        selected_2 = get_selected(liststrctrl)

        # press the OK button and close the dialog
        press_ok_button(ui)

    # the number traits should be between 3 and 8
    assert selected_1 == [1]
    assert selected_2 == [0]


if __name__ == '__main__':
    # Executing the file opens the dialog for manual testing
    editor = ListStrEditorWithSelectedIndex(
            values=['value1', 'value2'],
            selected_index=1)
    editor.configure_traits(view=single_select_view)
