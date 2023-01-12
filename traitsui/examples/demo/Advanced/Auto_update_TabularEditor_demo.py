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

Auto-update from a list to a TabularEditor

Demonstrates using a TabularEditor with the 'auto_update' feature enabled,
which allows the tabular editor to automatically update itself when the content
of any object in the list associated with the editor is modified.

To interact with the demo:

- Select an employee from the list.
- Adjust their salary increase.
- Click the **Give raise** button.
- Observe that the table automatically updates to reflect the employees new
  salary.

In order for auto-update to work correctly, the editor trait should be a list
of objects derived from HasTraits. Also, performance can be affected when very
long lists are used, since enabling this feature adds and removed Traits
listeners to each item in the list.

"""
# Issues related to the demo warning:
# enthought/traitsui#960

from traits.api import HasTraits, Str, Float, List, Instance, Button
from traitsui.api import (
    View,
    HGroup,
    Item,
    TabularAdapter,
    TabularEditor,
    spring,
)


# -- EmployeeAdapter Class ------------------------------------------------
class EmployeeAdapter(TabularAdapter):

    columns = [('Name', 'name'), ('Salary', 'salary')]

    def get_default_value(self, object, trait):
        return Employee(name="John", salary=30000)


# -- Employee Class -------------------------------------------------------
class Employee(HasTraits):

    name = Str()
    salary = Float()


# -- Company Class --------------------------------------------------------
class Company(HasTraits):

    employees = List(Employee)
    employee = Instance(Employee)
    increase = Float()
    give_raise = Button('Give raise')

    traits_view = View(
        Item(
            'employees',
            show_label=False,
            editor=TabularEditor(
                adapter=EmployeeAdapter(),
                selected='employee',
                auto_resize=True,
                auto_update=True,
            ),
        ),
        HGroup(
            spring,
            Item('increase'),
            Item(
                'give_raise',
                show_label=False,
                enabled_when='employee is not None',
            ),
        ),
        title='Auto Update Tabular Editor demo',
        height=0.25,
        width=0.30,
        resizable=True,
    )

    def _give_raise_changed(self):
        self.employee.salary += self.increase
        self.employee = None


# -- Set up the demo ------------------------------------------------------
demo = Company(
    increase=1000,
    employees=[
        Employee(name='Fred', salary=45000),
        Employee(name='Sally', salary=52000),
        Employee(name='Jim', salary=39000),
        Employee(name='Helen', salary=41000),
        Employee(name='George', salary=49000),
        Employee(name='Betty', salary=46000),
    ],
)

# Run the demo (if invoked from the command line):
if __name__ == '__main__':
    demo.configure_traits()
