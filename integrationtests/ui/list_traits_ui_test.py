# (C) Copyright 2004-2022 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

# -------------------------------------------------------------------------
#  Imports:
# -------------------------------------------------------------------------

from traits.api import HasStrictTraits, Str, Int, Regex, List, Instance

from traitsui.api import View, Item, VSplit, TableEditor, ListEditor

from traitsui.table_column import ObjectColumn

from traitsui.table_filter import (
    TableFilter,
    RuleTableFilter,
    RuleFilterTemplate,
    MenuFilterTemplate,
    EvalFilterTemplate,
)

# -------------------------------------------------------------------------
#  'Person' class:
# -------------------------------------------------------------------------


class Person(HasStrictTraits):

    # -------------------------------------------------------------------------
    #  Trait definitions:
    # -------------------------------------------------------------------------

    name = Str()
    age = Int()
    phone = Regex(value='000-0000', regex=r'\d\d\d[-]\d\d\d\d')

    # -------------------------------------------------------------------------
    #  Traits view definition:
    # -------------------------------------------------------------------------

    traits_view = View(
        'name', 'age', 'phone', width=0.18, buttons=['OK', 'Cancel']
    )


# -------------------------------------------------------------------------
#  Sample data:
# -------------------------------------------------------------------------

people = [
    Person(name='Dave', age=39, phone='555-1212'),
    Person(name='Mike', age=28, phone='555-3526'),
    Person(name='Joe', age=34, phone='555-6943'),
    Person(name='Tom', age=22, phone='555-7586'),
    Person(name='Dick', age=63, phone='555-3895'),
    Person(name='Harry', age=46, phone='555-3285'),
    Person(name='Sally', age=43, phone='555-8797'),
    Person(name='Fields', age=31, phone='555-3547'),
]

# -------------------------------------------------------------------------
#  Table editor definition:
# -------------------------------------------------------------------------

filters = [EvalFilterTemplate, MenuFilterTemplate, RuleFilterTemplate]

table_editor = TableEditor(
    columns=[
        ObjectColumn(name='name'),
        ObjectColumn(name='age'),
        ObjectColumn(name='phone'),
    ],
    editable=True,
    deletable=True,
    sortable=True,
    sort_model=True,
    filters=filters,
    search=RuleTableFilter(),
    row_factory=Person,
)

# -------------------------------------------------------------------------
#  'ListTraitTest' class:
# -------------------------------------------------------------------------


class ListTraitTest(HasStrictTraits):

    # -------------------------------------------------------------------------
    #  Trait definitions:
    # -------------------------------------------------------------------------

    people = List(Person)

    # -------------------------------------------------------------------------
    #  Traits view definitions:
    # -------------------------------------------------------------------------

    traits_view = View(
        VSplit(
            Item('people', id='table', editor=table_editor),
            Item(
                'people@', id='list', editor=ListEditor(style='custom', rows=5)
            ),
            Item(
                'people@',
                id='notebook',
                editor=ListEditor(
                    use_notebook=True,
                    deletable=True,
                    export='DockShellWindow',
                    dock_style='tab',
                    page_name='.name',
                ),
            ),
            id='splitter',
            show_labels=False,
        ),
        title='List Trait Editor Test',
        id='traitsui.tests.list_traits_ui_test',
        dock='horizontal',
        width=0.4,
        height=0.6,
        resizable=True,
        kind='live',
    )


# -------------------------------------------------------------------------
#  Run the tests:
# -------------------------------------------------------------------------

if __name__ == '__main__':
    ListTraitTest(people=people).configure_traits()
