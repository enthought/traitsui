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

from traits.has_traits import HasTraits
from traits.trait_types import Float, List, Instance
from traitsui.handler import ModelView
from traitsui.view import View
from traitsui.item import Item
from traitsui.editors.csv_list_editor import CSVListEditor

from _tools import *


class ListOfFloats(HasTraits):
    data = List(Float)


class ListOfFloatsWithCSVEditor(ModelView):
    model = Instance(ListOfFloats)

    traits_view = View(
        Item(label="Close the window to append data"),
        Item('model.data', editor = CSVListEditor()),
        buttons = ['OK']
    )


def test_csv_editor_disposal():
    # Bug: CSVListEditor does not un-hook the traits notifications after its
    # disposal, causing errors when the hooked data is accessed after
    # the window is closed (Issue #48)

    try:
        with store_exceptions_on_all_threads():
            list_of_floats = ListOfFloats(data=[1,2,3])
            csv_view = ListOfFloatsWithCSVEditor(model=list_of_floats)
            ui = csv_view.edit_traits()
            press_ok_button(ui)

            # raise an exception if still hooked
            list_of_floats.data.append(2)

    except AttributeError:
        # if all went well, we should not be here
        assert False, "AttributeError raised"


if __name__ == '__main__':
    # Executing the file opens the dialog for manual testing
    list_of_floats = ListOfFloats(data=[1,2,3])
    csv_view = ListOfFloatsWithCSVEditor(model=list_of_floats)
    csv_view.configure_traits()

    # this call will raise an AttributeError in commit
    # 4ecb2fa8f0ef385d55a2a4062d821b0415777973
    # This is because the editor does not un-hook the traits notifications
    # after its disposal
    list_of_floats.data.append(2)
    print list_of_floats.data
