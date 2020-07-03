#  Copyright (c) 2007-2009, Enthought, Inc.
#  License: BSD Style.

"""
Implementation of a DateRangeEditor demo plugin for Traits UI demo program.

This demo shows a custom style DateRangeEditor. Note that this demo only works
with qt backend.
"""
# Issue related to the demo warning: enthought/traitsui#962

from traits.api import HasTraits, Date, Tuple
from traits.etsconfig.api import ETSConfig
from traitsui.api import View, Item, DateRangeEditor, Group


class DateRangeEditorDemo(HasTraits):
    """ Demo class to show DateRangeEditor. """
    date_range = Tuple(Date, Date)

    traits_view = View(
        Group(
            Item(
                'date_range',
                editor=DateRangeEditor(),
                style='custom',
                label='Date range'
            ),
            label='Date range'
        ),
        resizable=True
    )

    def _date_range_changed(self):
        print(self.date_range)


# -- Set Up The Demo ------------------------------------------------------


if __name__ == "__main__":
    if ETSConfig.toolkit == "qt4":
        # DateRangeEditor is currently only available for qt backend.
        demo = DateRangeEditorDemo()
        demo.configure_traits()
