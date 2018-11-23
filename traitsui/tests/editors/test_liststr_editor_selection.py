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

from __future__ import absolute_import
from traits.has_traits import HasTraits
from traits.trait_types import List, Int, Str
from traitsui.item import Item
from traitsui.view import View
from traitsui.editors.list_str_editor import ListStrEditor

from traitsui.tests._tools import (
    press_ok_button, skip_if_not_qt4, skip_if_not_wx,
    store_exceptions_on_all_threads)


class ListStrEditorWithSelectedIndex(HasTraits):
    values = List(Str())
    selected_index = Int()
    selected_indices = List(Int())
    selected = Str()

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

single_select_item_view = View(
    Item('values',
         show_label=False,
         editor=ListStrEditor(
             selected='selected',
             editable=False),
         ),
    buttons=['OK'])


def get_selected(control):
    """ Returns a list of the indices of all currently selected list items.
    """
    import wx
    selected = []
    item = -1
    while True:
        item = control.GetNextItem(item, wx.LIST_NEXT_ALL,
                                   wx.LIST_STATE_SELECTED)
        if item == -1:
            break
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


@skip_if_not_qt4
def test_selection_listener_disconnected():
    """ Check that selection listeners get correctly disconnected """
    from pyface.api import GUI
    from pyface.qt.QtGui import QApplication, QItemSelectionModel
    from pyface.ui.qt4.util.event_loop_helper import EventLoopHelper
    from pyface.ui.qt4.util.testing import event_loop

    obj = ListStrEditorWithSelectedIndex(values=['value1', 'value2'])

    with store_exceptions_on_all_threads():
        qt_app = QApplication.instance()
        if qt_app is None:
            qt_app = QApplication([])
        helper = EventLoopHelper(gui=GUI(), qt_app=qt_app)

        # open the UI and run until the dialog is closed
        ui = obj.edit_traits(view=single_select_item_view)
        with helper.delete_widget(ui.control):
            press_ok_button(ui)

        # now run again and change the selection
        ui = obj.edit_traits(view=single_select_item_view)
        with event_loop():
            editor = ui.get_editors('values')[0]

            list_view = editor.list_view
            mi = editor.model.index(1)
            list_view.selectionModel().select(mi, QItemSelectionModel.ClearAndSelect)

    obj.selected = 'value2'


if __name__ == '__main__':
    # Executing the file opens the dialog for manual testing
    editor = ListStrEditorWithSelectedIndex(
        values=['value1', 'value2'],
        selected_index=1)
    editor.configure_traits(view=single_select_view)
