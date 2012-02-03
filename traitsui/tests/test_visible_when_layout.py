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
Test the layout when element appear and disappear with visible_when.
"""

from traits.has_traits import HasTraits
from traits.trait_types import Enum, Bool, Str

from traitsui.group import HGroup, VGroup
from traitsui.include import Include
from traitsui.item import Item
from traitsui.view import View

from traitsui.tests._tools import *

_TEXT_WIDTH = 200
_TEXT_HEIGHT = 100

class VisibleWhenProblem(HasTraits):

    which = Enum('one', 'two')

    on  = Bool
    txt = Str

    onoff_group = HGroup(
        VGroup(
            Item('on', resizable=False, width=-100, height=-70),
            show_left = False,
            show_border = True, visible_when='which == "one"'
        ),
    )

    text_group = VGroup(
        Item('txt', width=-_TEXT_WIDTH, height=-_TEXT_HEIGHT),
        visible_when='which == "two"',
        show_border = True,
    )

    traits_view = View(
        Item('which'),
        VGroup(
            Include('onoff_group'),
            Include('text_group'),
            ),
        resizable = True,
        buttons = ['OK', 'Cancel']
    )


@skip_if_null
def test_visible_when_layout():
    # Bug: The size of a dialog that contains elements that are activated
    # by "visible_when" can end up being the *sum* of the sizes of the
    # elements, even though the elements are mutually exclusive (e.g.,
    # a typical case is a dropbox that lets you select different cases).
    # The expected behavior is that the size of the dialog should be at most
    # the size of the largest combination of elements.

    with store_exceptions_on_all_threads():
        dialog = VisibleWhenProblem()
        ui = dialog.edit_traits()

        # have the dialog switch from group one to two and back to one
        dialog.which = 'two'
        dialog.which = 'one'

        # the size of the window should not be larger than the largest
        # combination (in this case, the `text_group` plus the `which` item
        size = get_dialog_size(ui.control)
        # leave some margin for labels, dropbox, etc
        nose.tools.assert_less(size[0], _TEXT_WIDTH+100)
        nose.tools.assert_less(size[1], _TEXT_HEIGHT+150)


if __name__ == '__main__':
    # Execute from command line for manual testing
    vw = VisibleWhenProblem(txt='ciao')
    ui = vw.configure_traits()
