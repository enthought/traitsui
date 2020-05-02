#  Copyright (c) 2020, Enthought, Inc.
#  License: BSD Style.

"""
A Traits UI editor that edits a datetime panel.
"""
import datetime

from traits.api import HasTraits, Datetime, Str
from traitsui.api import View, Item, Group, DatetimeEditor


class DateEditorDemo(HasTraits):
    """ Demo class to show Date editors. """
    datetime = Datetime()
    info_string = Str('The editors for Traits Datetime objects.')

    view = View(
        Item(
            'info_string',
            show_label=False,
            style='readonly',
        ),
        Group(
            Item(
                'datetime',
                label='Simple date editor',
            ),
            Item(
                'datetime',
                style='readonly',
                label='ReadOnly editor',
            ),
            label='Default settings for editors',
        ),
        resizable=True,
    )

    def _datetime_changed(self):
        """ Print each time the date value is changed in the editor. """
        print(self.datetime)


#-- Set Up The Demo ------------------------------------------------------

demo = DateEditorDemo(
    datetime=datetime.datetime.now()
)

if __name__ == "__main__":
    demo.configure_traits()
