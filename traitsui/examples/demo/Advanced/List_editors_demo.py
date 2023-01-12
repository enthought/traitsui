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

This shows the three different types of editor that can be applied to a list
of objects:

- Table
- List
- Dockable notebook (a list variant)

Each editor style is editing the exact same list of objects. Note that any
changes made in one editor are automatically reflected in the others.
"""
# Issue related to the demo warning: enthought/traitsui#948

from traits.api import HasStrictTraits, Str, Int, Regex, List, Instance

from traitsui.api import (
    Item,
    ListEditor,
    ObjectColumn,
    RuleTableFilter,
    Tabbed,
    TableEditor,
    View,
)

from traitsui.table_filter import (
    RuleFilterTemplate,
    MenuFilterTemplate,
    EvalFilterTemplate,
)


# 'Person' class:
class Person(HasStrictTraits):

    # Trait definitions:
    name = Str()
    age = Int()
    phone = Regex(value='000-0000', regex=r'\d\d\d[-]\d\d\d\d')

    # Traits view definition:
    traits_view = View(
        'name', 'age', 'phone', width=0.18, buttons=['OK', 'Cancel']
    )


# Sample data:
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

# Table editor definition:
filters = [EvalFilterTemplate, MenuFilterTemplate, RuleFilterTemplate]

table_editor = TableEditor(
    columns=[
        ObjectColumn(name='name', width=0.4),
        ObjectColumn(name='age', width=0.2),
        ObjectColumn(name='phone', width=0.4),
    ],
    editable=True,
    deletable=True,
    sortable=True,
    sort_model=True,
    auto_size=False,
    filters=filters,
    search=RuleTableFilter(),
    row_factory=Person,
    show_toolbar=True,
)


# 'ListTraitTest' class:
class ListTraitTest(HasStrictTraits):

    # Trait definitions:
    people = List(Instance(Person, ()))

    # Traits view definitions:
    traits_view = View(
        Tabbed(
            Item('people', label='Table', id='table', editor=table_editor),
            Item(
                'people',
                label='List',
                id='list',
                style='custom',
                editor=ListEditor(style='custom', rows=5),
            ),
            Item(
                'people',
                label='Notebook',
                id='notebook',
                style='custom',
                editor=ListEditor(
                    use_notebook=True,
                    deletable=True,
                    export='DockShellWindow',
                    page_name='.name',
                ),
            ),
            id='splitter',
            show_labels=False,
        ),
        id='traitsui.demo.Traits UI Demo.Advanced.List_editors_demo',
        dock='horizontal',
        width=600,
    )


# Create the demo:
demo = ListTraitTest(people=people)

# Run the demo (if invoked from the command line):
if __name__ == '__main__':
    demo.configure_traits()
