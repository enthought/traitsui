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
Test the creation and layout of labels.
"""

from traits.has_traits import HasTraits
from traits.trait_types import Bool
from traitsui.view import View
from traitsui.item import Item
from traitsui.group import VGroup

from traitsui.tests._tools import *


class ShowRightLabelsDialog(HasTraits):

    bool_item = Bool(True)

    traits_view = View(
        VGroup(
            VGroup(
                Item('bool_item', resizable=True),
                show_left=False
            ),
            VGroup(
                Item('bool_item', resizable=True),
                show_left=True
            ),
        ),
        width=300,
        height=100,
        resizable=True
    )


@skip_if_not_qt4
def test_qt_show_labels_right_without_colon():
    # Behavior: traitsui should not append a colon ':' to labels
    # that are shown to the *right* of the corresponding elements

    from pyface import qt

    with store_exceptions_on_all_threads():
        dialog = ShowRightLabelsDialog()
        ui = dialog.edit_traits()

        # get reference to label objects
        labels = ui.control.findChildren(qt.QtGui.QLabel)

        # the first is shown to the right, so no colon
        nose.tools.assert_false(labels[0].text().endswith(':'))

        # the second is shown to the right, it should have a colon
        nose.tools.assert_true(labels[1].text().endswith(':'))



if __name__ == "__main__":
    # Execute from command line for manual testing
    vw = ShowRightLabelsDialog()
    vw.configure_traits()
