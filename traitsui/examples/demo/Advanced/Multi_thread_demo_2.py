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
Monitoring a dynamic number of threads

Shows a simple user interface being updated by a dynamic number of threads.

When the *Create Threads* button is pressed, the *count* method is
dispatched on a new thread. It then creates a new *Counter* object and
adds it to the *counters* list (which causes the *Counter* to appear
in the user interface. It then counts by incrementing the *Counter*
object's *count* trait (which again causes a user interface update each
time the counter is incremented). After it reaches its maximum count, it
removes the *Counter* from the *counter* list (causing the counter
to be removed from the user interface) and exits (terminating the thread).

Note that repeated clicking of the *Create Thread* button will create
additional threads.
"""

from time import sleep
from traits.api import HasTraits, Int, Button, List
from traitsui.api import View, Item, ListEditor

# -- The Counter objects used to keep track of the current count ----------


class Counter(HasTraits):

    # The current count:
    count = Int()

    view = View(Item('count', style='readonly'))


# -- The main 'ThreadDemo' class ------------------------------------------


class ThreadDemo(HasTraits):

    # The button used to start a new thread running:
    create = Button('Create Thread')

    # The set of counter objects currently running:
    counters = List(Counter)

    view = View(
        Item('create', show_label=False),
        '_',
        Item(
            'counters',
            style='custom',
            show_label=False,
            editor=ListEditor(use_notebook=True, dock_style='tab'),
        ),
        resizable=True,
        width=300,
        height=150,
        title='Dynamic threads',
    )

    def __init__(self, **traits):
        super().__init__(**traits)

        # Set up the notification handler for the 'Create Thread' button so
        # that it is run on a new thread:
        self.on_trait_change(self.count, 'create', dispatch='new')

    def count(self):
        """This method is dispatched on a new thread each time the
        'Create Thread' button is pressed.
        """
        counter = Counter()
        self.counters.append(counter)
        for i in range(1000):
            counter.count += 1
            sleep(0.030)
        self.counters.remove(counter)


# Create the demo:
demo = ThreadDemo()

# Run the demo (if invoked from the command line):
if __name__ == '__main__':
    demo.configure_traits()
