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
Displaying a statusbar in a Traits UI

A statusbar may contain one or more fields, of fixed or variable size.

Fixed width fields are specified in pixels, while variable width fields are
specified as fractional values relative to other variable width fields.

The content of a statusbar field is specified via the extended trait name of
the object attribute that will contain the statusbar information.

In this example, there are two statusbar fields:

- The current length of the text input data (variable width)
- The current time (fixed width, updated once per second).

Note the use of a timer thread to update the status bar once per second.

"""

from time import sleep, strftime
from threading import Thread
from traits.api import HasPrivateTraits, Str, Property
from traitsui.api import View, Item, StatusItem, Label

# -- The demo class -------------------------------------------------------


class TextEditor(HasPrivateTraits):

    # The text being edited:
    text = Str()

    # The current length of the text being edited:
    length = Property(observe='text')

    # The current time:
    time = Str()

    # The view definition:
    view = View(
        Label('Type into the text editor box:'),
        Item('text', style='custom', show_label=False),
        title='Text Editor',
        id='traitsui.demo.advanced.statusbar_demo',
        width=0.4,
        height=0.4,
        resizable=True,
        statusbar=[
            StatusItem(name='length', width=0.5),
            StatusItem(name='time', width=85),
        ],
    )

    # -- Property Implementations ---------------------------------------------

    def _get_length(self):
        return 'Length: %d characters' % len(self.text)

    # -- Default Trait Values -------------------------------------------------

    def _time_default(self):
        thread = Thread(target=self._clock)
        thread.daemon = True
        thread.start()

        return ''

    # -- Private Methods ------------------------------------------------------

    def _clock(self):
        """Update the statusbar time once every second."""
        while True:
            self.time = strftime('%I:%M:%S %p')
            sleep(1.0)


# Create the demo object:
popup = TextEditor()

# Run the demo (if invoked from the command line):
if __name__ == '__main__':
    popup.configure_traits()
