#  Copyright (c) 2007-2009, Enthought, Inc.
#  License: BSD Style.

"""
A Traits UI editor that wraps a Qt calendar panel.
"""
from __future__ import absolute_import, print_function

from traits.api import HasTraits, Date, Tuple
from traitsui.api import View, Item, DateRangeEditor, Group


class DateRangeEditorDemo(HasTraits):
    """ Demo class to show DateRangeEditor. """
    date_range = Tuple(Date, Date)

    view = View(
                Group(Item('date_range',
                           editor=DateRangeEditor(),
                           style='custom',
                           label='Date range'),
                      label='Date range'),
                resizable=True)

    def _date_range_changed(self):
        print(self.date_range)


#-- Set Up The Demo ------------------------------------------------------

demo = DateRangeEditorDemo()

if __name__ == "__main__":
    demo.configure_traits()

#-- eof -----------------------------------------------------------------------
