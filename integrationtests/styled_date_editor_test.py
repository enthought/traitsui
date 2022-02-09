# (C) Copyright 2004-2022 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

from datetime import date

from traits.api import Date, Dict, HasTraits, List, observe
from traitsui.api import View, Item, StyledDateEditor
from traitsui.editors.styled_date_editor import CellFormat


class Foo(HasTraits):
    dates = Dict()
    styles = Dict()

    fast_dates = List()
    slow_dates = List()

    current_date = Date()

    traits_view = View(
        Item(
            "current_date",
            style="custom",
            show_label=False,
            editor=StyledDateEditor(
                dates_trait="dates", styles_trait="styles"
            ),
        )
    )

    def __init__(self, *args, **kw):
        HasTraits.__init__(self, *args, **kw)
        self.styles = {
            "fast": CellFormat(bold=True, fgcolor="darkGreen"),
            "slow": CellFormat(italics=True, fgcolor="lightGray"),
        }

        self.fast_dates = [
            date(2010, 7, 4),
            date(2010, 7, 3),
            date(2010, 7, 2),
        ]
        self.slow_dates = [
            date(2010, 6, 28),
            date(2010, 6, 27),
            date(2010, 6, 24),
        ]

    @observe("fast_dates,slow_dates")
    def _update_dates_dict(self, event):
        self.dates["fast"] = self.fast_dates
        self.dates["slow"] = self.slow_dates

    def _current_date_changed(self, old, new):
        print("Old:", old, "New:", new)


def main():
    foo = Foo()
    foo.configure_traits()


if __name__ == "__main__":
    main()
