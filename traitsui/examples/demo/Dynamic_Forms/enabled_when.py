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
Dynamic enabling parts of a user interface using 'enabled_when'

How to dynamically enable or disable components of a Traits UI view, depending
on the value of another trait.

The demo class "Person" has a set of attributes that apply to all instances
('first_name', 'last_name', 'age'), a set of attributes that apply only to
children (Persons whose age is under 18), and a set of attributes that apply
only to adults. As a Person's age changes, only the age-appropriate attributes
will be enabled (available for editing).

**Detail:** The optional *enabled_when* attribute of an Item or Group is a
string containing a boolean expression (logical condition) indicating when this
Item or Group will be enabled. The boolean expression is evaluated for the
object being viewed, so that in this example, 'age' refers to the 'age'
attribute of the Person being viewed.

Compare this to very similar demo of *visible_when*.
"""

from traits.api import HasTraits, Str, Range, Bool, Enum
from traitsui.api import Item, Group, View, Label


class Person(HasTraits):
    """Example of enabling/disabling components of a user interface."""

    # General traits:
    first_name = Str()
    last_name = Str()
    age = Range(0, 120)

    # Traits for children only:
    legal_guardian = Str()
    school = Str()
    grade = Range(1, 12)

    # Traits for adults only:
    marital_status = Enum('single', 'married', 'divorced', 'widowed')
    registered_voter = Bool(False)
    military_service = Bool(False)

    # Interface for attributes that are always visible in interface:
    gen_group = Group(
        Item(name='first_name'),
        Item(name='last_name'),
        Item(name='age'),
        label='General Info',
        show_border=True,
    )

    # Interface for attributes of Persons under 18:
    child_group = Group(
        Item(name='legal_guardian'),
        Item(name='school'),
        Item(name='grade'),
        label='Additional Info for minors',
        show_border=True,
        enabled_when='age < 18',
    )

    # Interface for attributes of Persons 18 and over:
    adult_group = Group(
        Item(name='marital_status'),
        Item(name='registered_voter'),
        Item(name='military_service'),
        '10',
        label='Additional Info for adults',
        show_border=True,
        enabled_when='age >= 18',
    )

    # A simple View is sufficient, since the Group definitions do all the work:
    view = View(
        Group(
            gen_group,
            '10',
            Label("Using 'enabled_when':"),
            '10',
            child_group,
            adult_group,
        ),
        title='Personal Information',
        resizable=True,
        buttons=['OK'],
    )


# Create the demo:
demo = Person(first_name="Samuel", last_name="Johnson", age=16)

# Run the demo (if invoked from the command line):
if __name__ == '__main__':
    demo.configure_traits()
