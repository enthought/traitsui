# (C) Copyright 2004-2023 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

"""
Implementation of a SetEditor demo plugin for the Traits UI demo program.

The four tabs of this demo show variations on the interface as follows:

- Unord I:  Creates an alphabetized subset, has no "move all" options
- Unord II: Creates an alphabetized subset, has "move all" options
- Ord I:    Creates a set whose order is specified by the user, no "move all"
- Ord II:   Creates a set whose order is specifed by the user, has "move all"

Please refer to the `SetEditor API docs`_ for further information.

.. _SetEditor API docs: https://docs.enthought.com/traitsui/api/traitsui.editors.set_editor.html#traitsui.editors.set_editor.SetEditor
"""

from traits.api import HasTraits, List

from traitsui.api import Item, Group, View, SetEditor


# Define the main demo class:
class SetEditorDemo(HasTraits):
    """Defines the SetEditor demo class."""

    # Define a trait each for four SetEditor variants:
    unord_nma_set = List(
        editor=SetEditor(
            values=['kumquats', 'pomegranates', 'kiwi'],
            left_column_title='Available Fruit',
            right_column_title='Exotic Fruit Bowl',
            can_move_all=False,
        )
    )

    unord_ma_set = List(
        editor=SetEditor(
            values=['kumquats', 'pomegranates', 'kiwi'],
            left_column_title='Available Fruit',
            right_column_title='Exotic Fruit Bowl',
        )
    )

    ord_nma_set = List(
        editor=SetEditor(
            values=['apples', 'berries', 'cantaloupe'],
            left_column_title='Available Fruit',
            right_column_title='Fruit Bowl',
            ordered=True,
            can_move_all=False,
        )
    )

    ord_ma_set = List(
        editor=SetEditor(
            values=['apples', 'berries', 'cantaloupe'],
            left_column_title='Available Fruit',
            right_column_title='Fruit Bowl',
            ordered=True,
        )
    )

    # SetEditor display, unordered, no move-all buttons:
    no_nma_group = Group(
        Item('unord_nma_set', style='simple'),
        label='Unord I',
        show_labels=False,
    )

    # SetEditor display, unordered, move-all buttons:
    no_ma_group = Group(
        Item('unord_ma_set', style='simple'),
        label='Unord II',
        show_labels=False,
    )

    # SetEditor display, ordered, no move-all buttons:
    o_nma_group = Group(
        Item('ord_nma_set', style='simple'), label='Ord I', show_labels=False
    )

    # SetEditor display, ordered, move-all buttons:
    o_ma_group = Group(
        Item('ord_ma_set', style='simple'), label='Ord II', show_labels=False
    )

    # The view includes one group per data type. These will be displayed
    # on separate tabbed panels:
    traits_view = View(
        no_nma_group,
        no_ma_group,
        o_nma_group,
        o_ma_group,
        title='SetEditor',
        buttons=['OK'],
    )


# Create the demo:
demo = SetEditorDemo()

# Run the demo (if invoked from the command line):
if __name__ == '__main__':
    demo.configure_traits()
