from __future__ import absolute_import, print_function

from datetime import date

from traits.etsconfig.api import ETSConfig
ETSConfig.toolkit = 'qt4'

from traits.api import Date, Dict, HasTraits, List, on_trait_change
from traitsui.api import View, Item, StyledDateEditor
from traitsui.editors.styled_date_editor import CellFormat


class Foo(HasTraits):
    dates = Dict()
    styles = Dict()

    fast_dates = List
    slow_dates = List

    current_date = Date()

    traits_view = View(
        Item(
            "current_date",
            style="custom",
            show_label=False,
            editor=StyledDateEditor(
                dates_trait="dates",
                styles_trait="styles")))

    def __init__(self, *args, **kw):
        HasTraits.__init__(self, *args, **kw)
        self.styles = {
            "fast": CellFormat(bold=True, fgcolor="darkGreen"),
            "slow": CellFormat(italics=True, fgcolor="lightGray"),
        }

        self.fast_dates = [
            date(
                2010, 7, 4), date(
                2010, 7, 3), date(
                2010, 7, 2)]
        self.slow_dates = [
            date(
                2010, 6, 28), date(
                2010, 6, 27), date(
                2010, 6, 24)]

    @on_trait_change("fast_dates,slow_dates")
    def _update_dates_dict(self):
        self.dates["fast"] = self.fast_dates
        self.dates["slow"] = self.slow_dates

    def _current_date_changed(self, old, new):
        print("Old:", old, "New:", new)


def main():
    foo = Foo()
    foo.configure_traits()


if __name__ == "__main__":
    main()
