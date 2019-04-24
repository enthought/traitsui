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

from __future__ import absolute_import, print_function

import nose

from traits.has_traits import HasTraits
from traits.trait_types import Float, List, Instance
from traitsui.handler import ModelView
from traitsui.view import View
from traitsui.item import Item
from traitsui.editors.csv_list_editor import CSVListEditor
import traitsui.editors.csv_list_editor as csv_list_editor

from traitsui.tests._tools import *


class ListOfFloats(HasTraits):
    data = List(Float)


class ListOfFloatsWithCSVEditor(ModelView):
    model = Instance(ListOfFloats)

    traits_view = View(
        Item(label="Close the window to append data"),
        Item('model.data', editor=CSVListEditor()),
        buttons=['OK']
    )


@skip_if_null
def test_csv_editor_disposal():
    # Bug: CSVListEditor does not un-hook the traits notifications after its
    # disposal, causing errors when the hooked data is accessed after
    # the window is closed (Issue #48)

    try:
        with store_exceptions_on_all_threads():
            list_of_floats = ListOfFloats(data=[1, 2, 3])
            csv_view = ListOfFloatsWithCSVEditor(model=list_of_floats)
            ui = csv_view.edit_traits()
            press_ok_button(ui)

            # raise an exception if still hooked
            list_of_floats.data.append(2)

    except AttributeError:
        # if all went well, we should not be here
        assert False, "AttributeError raised"


@skip_if_null
def test_csv_editor_external_append():
    # Behavior: CSV editor is notified when an element is appended to the
    # list externally

    def _wx_get_text_value(ui):
        txt_ctrl = ui.control.FindWindowByName('text')
        return txt_ctrl.GetValue()

    def _qt_get_text_value(ui):
        from pyface import qt
        txt_ctrl = ui.control.findChild(qt.QtGui.QLineEdit)
        return txt_ctrl.text()

    with store_exceptions_on_all_threads():
        list_of_floats = ListOfFloats(data=[1.0])
        csv_view = ListOfFloatsWithCSVEditor(model=list_of_floats)
        ui = csv_view.edit_traits()

        # add element to list, make sure that editor knows about it
        list_of_floats.data.append(3.14)

        # get current value from editor
        if is_current_backend_wx():
            value_str = _wx_get_text_value(ui)
        elif is_current_backend_qt4():
            value_str = _qt_get_text_value(ui)

        expected = csv_list_editor._format_list_str([1.0, 3.14])
        nose.tools.assert_equal(value_str, expected)

        press_ok_button(ui)


if __name__ == '__main__':
    # Executing the file opens the dialog for manual testing
    list_of_floats = ListOfFloats(data=[1, 2, 3])
    csv_view = ListOfFloatsWithCSVEditor(model=list_of_floats)
    csv_view.configure_traits()

    # this call will raise an AttributeError in commit
    # 4ecb2fa8f0ef385d55a2a4062d821b0415777973
    # This is because the editor does not un-hook the traits notifications
    # after its disposal
    list_of_floats.data.append(2)
    print(list_of_floats.data)
