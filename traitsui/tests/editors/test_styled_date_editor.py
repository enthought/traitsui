# (C) Copyright 2004-2023 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

import datetime
import unittest

from traits.api import Dict, HasTraits, Instance, List, Str
from traitsui.api import Item, StyledDateEditor, View
from traitsui.editors.date_editor import CellFormat
from traitsui.tests._tools import (
    BaseTestMixin,
    create_ui,
    requires_toolkit,
    reraise_exceptions,
    ToolkitName,
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
@requires_toolkit([ToolkitName.qt])
class TestStyledDateEditor(BaseTestMixin, unittest.TestCase):
    def setUp(self):
        BaseTestMixin.setUp(self)

    def tearDown(self):
        BaseTestMixin.tearDown(self)

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
        with reraise_exceptions(), create_ui(instance, dict(view=view)):
            pass
