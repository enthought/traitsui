"""
A timer editor

Display or edit a time.

You can edit the time directly, or by using only the arrow keys (left & right
to navigate, up & down to change).

"""
from __future__ import print_function
import datetime

from traits.api import HasTraits, Time
from traitsui.api import View, Item, TimeEditor


class TimeEditorDemo(HasTraits):
    """ Demo class. """
    time = Time(datetime.time(12, 0, 0))
    view = View(Item('time', label='Simple Editor'),
                Item('time', label='Readonly Editor',
                     style='readonly',
                     # Show 24-hour mode instead of default 12 hour.
                     editor=TimeEditor(strftime='%H:%M:%S')
                     ),
                resizable=True)

    def _time_changed(self):
        """ Print each time the time value is changed in the editor. """
        print(self.time)


#-- Set Up The Demo ------------------------------------------------------------

demo = TimeEditorDemo()

if __name__ == "__main__":
    demo.configure_traits()
