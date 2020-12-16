#  Copyright (c) 2020, Enthought, Inc.
#  License: BSD Style.

"""
**WARNING**

  This demo might not work as expected and some documented features might be
  missing.

-------------------------------------------------------------------------------

A Traits UI editor that edits a datetime panel.

Please refer to the `DatetimeEditor API docs`_ for further information.

.. _DatetimeEditor API docs: https://docs.enthought.com/traitsui/api/traitsui.editors.datetime_editor.html#traitsui.editors.datetime_editor.DatetimeEditor
"""
# Issue related to the demo warning: enthought/traitsui#943


import datetime

from traits.api import HasTraits, Datetime, Str
from traitsui.api import View, Item, Group


class DateEditorDemo(HasTraits):
    """ Demo class to show Datetime editors. """
    datetime = Datetime()
    info_string = Str('The editors for Traits Datetime objects.')

    traits_view = View(
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


# -- Set Up The Demo ------------------------------------------------------

demo = DateEditorDemo(
    datetime=datetime.datetime.now()
)

if __name__ == "__main__":
    demo.configure_traits()
