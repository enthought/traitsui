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
This is a modified version of the Standard_Editors/TreeEditor_demo.py in which
the `Employee` class is now a subclass of HasRequiredTraits.  Thus, to create a
new `TreeNode` for `Employee`, to create the associated `Employee` object we
can not simply do `Employee()`. Luckily the `TreeNode` API provides a means for
specifying a callable that returns a created instance when we want to add a new
node. To do so we can simply pass a tuple of the for (klass, prompt, factorry)
as an item the `add` list trait for a TreeNode. klass is the class of object we
want to be addable, prompt is a boolean indicating whether or not we want to
prompt the user to specify traits after we instantiate the object before it is
added to the tree, and factory is the previously described callable that must
return an instance of klass.
"""

from traits.api import HasRequiredTraits, HasTraits, Str, Regex, List, Instance

from traitsui.api import Item, View, TreeEditor, TreeNode


class Employee(HasRequiredTraits):
    """Defines a company employee."""

    name = Str('<unknown>')
    title = Str()
    phone = Regex(regex=r'\d\d\d-\d\d\d\d')

    def default_title(self):
        self.title = 'Senior Engineer'


def create_default_employee():
    return Employee(name="Dilbert", title="Engineer", phone="999-8212")


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
            add=[(Employee, True, create_default_employee)],
        ),
        TreeNode(
            node_for=[Department],
            auto_open=True,
            children='employees',
            label='name',  # label with Department name
            view=View(['name']),
            add=[(Employee, True, create_default_employee)],
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
