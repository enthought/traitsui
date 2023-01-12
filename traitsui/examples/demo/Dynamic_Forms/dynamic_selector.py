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
Dynamic changing a selection list, using Handler

One way to dynamically change the list of values shown by an EnumEditor.

This example demonstrates several useful Traits UI concepts. It dynamically
changes the values which an EnumEditor presents to the user for selection. It
does this with a custom *Handler* which is assigned to the view, listens for
changes in a viewed trait, and changes the selection list accordingly.

Various implementations of dynamic data retrieval are possible. This example
shows how a Handler can interact with the traits in a view, separating model
logic from the view implementation.

Demo class *Address* has a simple set of attributes: *street_address*, *state*
and *city*. The values of *state* and *city* are to be chosen from enumerated
lists; however, the user does not want to see every city in the USA, but only
those for the chosen state.

Note that *city* is simply defined as a trait of type Str. By default, a Str
would be displayed using a simple TextEditor, but in this view we explicitly
specify that *city* should be displayed with an EnumEditor. The values that
appear in the GUI's enumerated list are determined by the *cities* attribute of
the view's handler, as specified in the EnumEditor's *name* parameter.
"""

from traits.api import HasTraits, Str, Enum, List
from traitsui.api import View, Item, Handler, EnumEditor

# Dictionary of defined states and cities.
cities = {
    'GA': ['Athens', 'Atlanta', 'Macon', 'Marietta', 'Savannah'],
    'TX': ['Austin', 'Amarillo', 'Dallas', 'Houston', 'San Antonio', 'Waco'],
    'OR': ['Albany', 'Eugene', 'Portland'],
}


class AddressHandler(Handler):
    """
    Handler class to redefine the possible values of 'city' based on 'state'.
    This handler will be assigned to a view of an Address, and can listen and
    respond to changes in the viewed Address.
    """

    # Current list of available cities:
    cities = List(Str)

    def object_state_changed(self, info):
        """
        This method listens for a change in the *state* attribute of the
        object (Address) being viewed.

        When this listener method is called, *info.object* is a reference to
        the viewed object (Address).

        """
        # Change the list of available cities
        self.cities = cities[info.object.state]

        # As default value, use the first city in the list:
        info.object.city = self.cities[0]


class Address(HasTraits):
    """Demo class for demonstrating dynamic redefinition of valid trait values."""

    street_address = Str()
    state = Enum(list(cities.keys())[0], list(cities.keys()))
    city = Str()

    view = View(
        Item(name='street_address'),
        Item(name='state'),
        Item(
            name='city',
            editor=EnumEditor(name='handler.cities'),
        ),
        title='Address Information',
        buttons=['OK'],
        resizable=True,
        handler=AddressHandler,
    )


# Create the demo:
demo = Address(street_address="4743 Dudley Lane")

# Run the demo (if invoked from the command line):
if __name__ == '__main__':
    demo.configure_traits()
