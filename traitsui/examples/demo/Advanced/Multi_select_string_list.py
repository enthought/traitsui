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
**WARNING**

  This demo might not work as expected and some documented features might be
  missing.

-------------------------------------------------------------------------------

Creating a multi-select list box

How to use a TabularEditor to create a multi-select list box.

This demo uses two TabularEditors, side-by-side. Selections from the left table
are shown in the right table. Each table has only one column.

"""
# Issues related to the demo warning: enthought/traitsui#14,
# enthought/traitsui#15, enthought/traitsui#960

from traits.api import HasPrivateTraits, List, Str, Property
from traitsui.api import View, HGroup, UItem, TabularAdapter, TabularEditor


class MultiSelectAdapter(TabularAdapter):
    """This adapter is used by both the left and right tables"""

    # Titles and column names for each column of a table.
    # In this example, each table has only one column.
    columns = [('', 'myvalue')]

    # Magically named trait which gives the display text of the column named
    # 'myvalue'. This is done using a Traits Property and its getter:
    myvalue_text = Property()

    # The getter for Property 'myvalue_text' simply takes the value of the
    # corresponding item in the list being displayed in this table.
    # A more complicated example could format the item before displaying it.
    def _get_myvalue_text(self):
        return self.item


class MultiSelect(HasPrivateTraits):
    """This is the class used to view two tables"""

    # FIXME (TraitsUI defect #14): When multi-select is done by keyboard
    # (shift+arrow), the 'selected' trait list does not update.

    # FIXME (TraitsUI defect #15): In Windows wx, when show_titles is False,
    # left table does not draw until selection passes through all rows.
    # (Workaround here: set show_titles True and make column titles empty.)

    choices = List(Str)
    selected = List(Str)

    traits_view = View(
        HGroup(
            UItem(
                'choices',
                editor=TabularEditor(
                    show_titles=True,
                    selected='selected',
                    editable=False,
                    multi_select=True,
                    adapter=MultiSelectAdapter(),
                ),
            ),
            UItem(
                'selected',
                editor=TabularEditor(
                    show_titles=True,
                    editable=False,
                    adapter=MultiSelectAdapter(),
                ),
            ),
        ),
        resizable=True,
        width=200,
        height=300,
    )


# Create the demo:
demo = MultiSelect(
    choices=[
        'one',
        'two',
        'three',
        'four',
        'five',
        'six',
        'seven',
        'eight',
        'nine',
        'ten',
    ]
)

# Run the demo (if invoked from the command line):
if __name__ == '__main__':
    demo.configure_traits()
