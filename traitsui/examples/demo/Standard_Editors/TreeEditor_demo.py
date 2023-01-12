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
Tree editor for hierarchal data

Demonstrates using the TreeEditor to display a hierarchically organized data
structure.

In this case, the tree has the following hierarchy:

- Partner
    - Company
        - Department
            - Employee

The TreeEditor generates a hierarchical tree control, consisting of nodes. It
is useful for cases where objects contain lists of other objects.

The tree control is displayed in one pane of the editor, and a user interface
for the selected object is displayed in the other pane. The layout orientation
of the tree and the object editor is determined by the *orientation* parameter
of TreeEditor(), which can be 'horizontal' or 'vertical'.

You must specify the types of nodes that can appear in the tree using the
*nodes* parameter, which must be a list of instances of TreeNode (or of
subclasses of TreeNode).

You must specify the classes whose instances the node type applies to. Use the
**node_for** attribute of TreeNode to specify a list of classes; often, this
list contains only one class. You can have more than one node type that applies
to a particular class; in this case, each object of that class is represented
by multiple nodes, one for each applicable node type.

See the Traits User Manual for more details.

Please refer to the `TreeEditor API docs`_ for further information.

.. _TreeEditor API docs: https://docs.enthought.com/traitsui/api/traitsui.editors.tree_editor.html#traitsui.editors.tree_editor.TreeEditor
"""

from traits.api import HasTraits, Str, Regex, List, Instance

from traitsui.api import Item, View, TreeEditor, TreeNode


class Employee(HasTraits):
    """Defines a company employee."""

    name = Str('<unknown>')
    title = Str()
    phone = Regex(regex=r'\d\d\d-\d\d\d\d')

    def default_title(self):
        self.title = 'Senior Engineer'


class Department(HasTraits):
    """Defines a department with employees."""

    name = Str('<unknown>')
    employees = List(Employee)


class Company(HasTraits):
    """Defines a company with departments and employees."""

    name = Str('<unknown>')
    departments = List(Department)
    employees = List(Employee)


# Create an empty view for objects that have no data to display:
no_view = View()

# Define the TreeEditor used to display the hierarchy:
tree_editor = TreeEditor(
    nodes=[
        # The first node specified is the top level one
        TreeNode(
            node_for=[Company],
            auto_open=True,
            # child nodes are
            children='',
            label='name',  # label with Company name
            view=View(['name']),
        ),
        TreeNode(
            node_for=[Company],
            auto_open=True,
            children='departments',
            label='=Departments',  # constant label
            view=no_view,
            add=[Department],
        ),
        TreeNode(
            node_for=[Company],
            auto_open=True,
            children='employees',
            label='=Employees',  # constant label
            view=no_view,
            add=[Employee],
        ),
        TreeNode(
            node_for=[Department],
            auto_open=True,
            children='employees',
            label='name',  # label with Department name
            view=View(['name']),
            add=[Employee],
        ),
        TreeNode(
            node_for=[Employee],
            auto_open=True,
            label='name',  # label with Employee name
            view=View(['name', 'title', 'phone']),
        ),
    ]
)


class Partner(HasTraits):
    """Defines a business partner."""

    name = Str('<unknown>')
    company = Instance(Company)

    traits_view = View(
        Item(name='company', editor=tree_editor, show_label=False),
        title='Company Structure',
        buttons=['OK'],
        resizable=True,
        style='custom',
        width=0.3,
        height=500,
    )


# Create an example data structure:
jason = Employee(name='Jason', title='Senior Engineer', phone='536-1057')
mike = Employee(name='Mike', title='Senior Engineer', phone='536-1057')
dave = Employee(name='Dave', title='Senior Developer', phone='536-1057')
martin = Employee(name='Martin', title='Senior Engineer', phone='536-1057')
duncan = Employee(name='Duncan', title='Consultant', phone='526-1057')

# Create the demo:
demo = Partner(
    name='Enthought, Inc.',
    company=Company(
        name='Enthought',
        employees=[dave, martin, duncan, jason, mike],
        departments=[
            Department(name='Business', employees=[jason, mike]),
            Department(name='Scientific', employees=[dave, martin, duncan]),
        ],
    ),
)

# Run the demo (if invoked from the command line):
if __name__ == '__main__':
    demo.configure_traits()
