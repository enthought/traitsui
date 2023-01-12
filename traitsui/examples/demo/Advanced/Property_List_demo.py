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
This demo shows the proper way to create a **Property** whose value is a
list, especially when the value of the **Property** will be used in a user
interface, such as with the **TableEditor**.

Most of the demo is just the machinery to set up the example. The key thing to
note is the declaration of the *people* trait:

    people = Property( List, observe = 'ticker' )

In this case, by defining the **Property** as having a value of type
**List**, you are ensuring that the computed value of the property will be
validated using the **List** type, which in addition to verifying that the
value is indeed a list, also guarantees that it will be converted to a
**TraitListObject**, which is necessary for correct interaction with various
Traits UI editors in a user interface.

Note also the use of the *observe* metadata to trigger a trait property
change whenever the *ticker* trait changes (in this case, it is changed
every three seconds by a background thread).

Finally, the use of the *@cached_property* decorator simplifies the
implementation of the property by allowing the **_get_people** *getter*
method to perform the expensive generation of a new list of people only when
the *ticker* event fires, not every time it is accessed.
"""

from random import randint, choice

from threading import Thread

from time import sleep

from traits.api import (
    HasStrictTraits,
    HasPrivateTraits,
    Str,
    Int,
    Enum,
    List,
    Event,
    Property,
    cached_property,
)

from traitsui.api import ObjectColumn, Item, TableEditor, View


# -- Person Class ---------------------------------------------------------
class Person(HasStrictTraits):
    """Defines some sample data to display in the TableEditor."""

    name = Str()
    age = Int()
    gender = Enum('Male', 'Female')


# -- PropertyListDemo Class -----------------------------------------------
class PropertyListDemo(HasPrivateTraits):
    """Displays a random list of Person objects in a TableEditor that is
    refreshed every 3 seconds by a background thread.
    """

    # An event used to trigger a Property value update:
    ticker = Event()

    # The property being display in the TableEditor:
    people = Property(List, observe='ticker')

    # Tiny hack to allow starting the background thread easily:
    begin = Int()

    # -- Traits View Definitions ----------------------------------------------

    traits_view = View(
        Item(
            'people',
            show_label=False,
            editor=TableEditor(
                columns=[
                    ObjectColumn(name='name', editable=False, width=0.50),
                    ObjectColumn(name='age', editable=False, width=0.15),
                    ObjectColumn(name='gender', editable=False, width=0.35),
                ],
                auto_size=False,
                show_toolbar=False,
                sortable=False,
            ),
        ),
        title='Property List Demo',
        width=0.25,
        height=0.33,
        resizable=True,
    )

    # -- Property Implementations ---------------------------------------------
    @cached_property
    def _get_people(self):
        """Returns the value for the 'people' property."""
        return [
            Person(
                name='%s %s'
                % (
                    choice(['Tom', 'Dick', 'Harry', 'Alice', 'Lia', 'Vibha']),
                    choice(['Thomas', 'Jones', 'Smith', 'Adams', 'Johnson']),
                ),
                age=randint(21, 75),
                gender=choice(['Male', 'Female']),
            )
            for i in range(randint(10, 20))
        ]

    # -- Default Value Implementations ----------------------------------------
    def _begin_default(self):
        """Starts the background thread running."""
        thread = Thread(target=self._timer)
        thread.daemon = True
        thread.start()

        return 0

    # -- Private Methods ------------------------------------------------------

    def _timer(self):
        """Triggers a property update every 3 seconds for 30 seconds."""
        for i in range(10):
            sleep(3)
            self.ticker = True


# Create the demo:
demo = PropertyListDemo()
demo.begin

# Run the demo (if invoked from the command line):
if __name__ == '__main__':
    demo.configure_traits()
