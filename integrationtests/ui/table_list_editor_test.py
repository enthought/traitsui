# (C) Copyright 2004-2022 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

""" TableEditor test case for Traits UI which tests editing of lists instead
of editing of objects."""

# -------------------------------------------------------------------------
#  Imports:
# -------------------------------------------------------------------------

from traits.api import HasStrictTraits, List

from traitsui.api import View, Item, TableEditor

from traitsui.table_column import ListColumn

from traitsui.table_filter import TableFilter

# -------------------------------------------------------------------------
#  Sample data:
# -------------------------------------------------------------------------

people = [
    ['Dave', 39, '555-1212'],
    ['Mike', 28, '555-3526'],
    ['Joe', 34, '555-6943'],
    ['Tom', 22, '555-7586'],
    ['Dick', 63, '555-3895'],
    ['Harry', 46, '555-3285'],
    ['Sally', 43, '555-8797'],
    ['Fields', 31, '555-3547'],
]

# -------------------------------------------------------------------------
#  Table editor definition:
# -------------------------------------------------------------------------

table_editor = TableEditor(
    columns=[
        ListColumn(index=0, label='Name'),
        ListColumn(index=1, label='Age'),
        ListColumn(index=2, label='Phone'),
    ],
    editable=False,
    show_column_labels=True,  #
)

# -------------------------------------------------------------------------
#  'TableTest' class:
# -------------------------------------------------------------------------


class TableTest(HasStrictTraits):

    # -------------------------------------------------------------------------
    #  Trait definitions:
    # -------------------------------------------------------------------------

    people = List()

    # -------------------------------------------------------------------------
    #  Traits view definitions:
    # -------------------------------------------------------------------------

    traits_view = View(
        [Item('people', editor=table_editor, resizable=True), '|[]<>'],
        title='Table Editor Test',
        width=0.17,
        height=0.23,
        buttons=['OK', 'Cancel'],
        kind='live',
    )


# -------------------------------------------------------------------------
#  Run the tests:
# -------------------------------------------------------------------------

if __name__ == '__main__':
    tt = TableTest(people=people)
    tt.configure_traits()
    for p in tt.people:
        print(p)
        print('--------------')
