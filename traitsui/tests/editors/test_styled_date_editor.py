
import datetime
import unittest

from traits.api import Dict, HasTraits, Instance, List, Str
from traitsui.api import Item, StyledDateEditor, View
from traitsui.editors.date_editor import CellFormat
from traitsui.tests._tools import (
    create_ui,
    skip_if_not_qt4,
    store_exceptions_on_all_threads,
)


class DateModel(HasTraits):

    selected_date = Instance(datetime.date)
    special_days = Dict(Str, List(Instance(datetime.date)))
    styles_mapping = Dict(Str, Instance(CellFormat))


def get_example_model():
    return DateModel(
        special_days={
            "public-holidays": [datetime.date(2020, 1, 1)],
            "weekends": [datetime.date(2020, 1, 12)],
        },
        styles_mapping={
            "public-holidays": CellFormat(bgcolor=(255, 0, 0)),
            "weekends": CellFormat(bold=True),
        },
    )



# StyledDateEditor is currently only implemented for Qt
@skip_if_not_qt4
class TestStyledDateEditor(unittest.TestCase):

    def test_init_and_dispose(self):
        # Smoke test to test init and dispose.
        instance = get_example_model()
        view = View(
            Item(
                "selected_date",
                editor=StyledDateEditor(
                    dates_trait="special_days",
                    styles_trait="styles_mapping",
                ),
                style="custom",
            )
        )
        with store_exceptions_on_all_threads(), \
                create_ui(instance, dict(view=view)):
            pass
