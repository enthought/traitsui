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
**WARNING**

  This demo might not work as expected and some documented features might be
  missing.

-------------------------------------------------------------------------------

Implementation of a DateEditor demo plugin for Traits UI demo program.

This demo shows a few different styles of the DateEditor and how it can be
customized.
"""
# Issue related to the demo warning: enthought/traitsui#962

from traits.api import HasTraits, Date, List, Str
from traitsui.api import View, Item, DateEditor, Group


class DateEditorDemo(HasTraits):
    """Demo class to show Date editors."""

    single_date = Date()
    multi_date = List(Date)
    info_string = Str(
        'The editors for Traits Date objects.  Showing both '
        'the defaults, and one with alternate options.'
    )

    multi_select_editor = DateEditor(
        allow_future=False,
        multi_select=True,
        shift_to_select=False,
        on_mixed_select='max_change',
        # Qt ignores these setting and always shows only 1 month:
        months=2,
        padding=30,
    )

    traits_view = View(
        Item('info_string', show_label=False, style='readonly'),
        Group(
            Item('single_date', label='Simple date editor'),
            Item('single_date', style='custom', label='Default custom editor'),
            Item(
                'single_date',
                style='readonly',
                editor=DateEditor(
                    strftime='You picked %B %d %Y',
                    message='Click a date above.',
                ),
                label='ReadOnly editor',
            ),
            label='Default settings for editors',
        ),
        Group(
            Item(
                'multi_date',
                editor=multi_select_editor,
                style='custom',
                label='Multi-select custom editor',
            ),
            label='More customized editor: multi-select; disallow '
            'future; selection style; etc.',
        ),
        resizable=True,
    )

    def _multi_date_changed(self):
        """Print each time the date value is changed in the editor."""
        print(self.multi_date)

    def _simple_date_changed(self):
        """Print each time the date value is changed in the editor."""
        print(self.simple_date, self.single_date)

    def _single_date_changed(self):
        """Print each time the date value is changed in the editor."""
        print(self.single_date)


# -- Set Up The Demo ------------------------------------------------------

demo = DateEditorDemo()

if __name__ == "__main__":
    demo.configure_traits()
