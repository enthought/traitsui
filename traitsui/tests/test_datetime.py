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
Test the initialization of a Datetime when given minimum and maximum
dates in the DatetimeEditor
"""
from datetime import datetime, timedelta
import unittest

from traits.has_traits import HasTraits
from traits.trait_types import Datetime
from traitsui.editors.datetime_editor import DatetimeEditor
from traitsui.item import Item
from traitsui.view import View


from traitsui.tests._tools import (
    BaseTestMixin,
    create_ui,
    requires_toolkit,
    reraise_exceptions,
    ToolkitName,
)

MAX_DATE = datetime.now()
MIN_DATE = MAX_DATE - timedelta(days=10)
DATE = MAX_DATE - timedelta(days=5)


class DatetimeInitDailog(HasTraits):

    date = Datetime(allow_none=True)

    def _date_default(self):
        return DATE

    traits_view = View(Item('date',
                            editor=DatetimeEditor(
                                maximum_datetime=MAX_DATE,
                                minimum_datetime=MIN_DATE)))


class TestDatetimeEditor(BaseTestMixin, unittest.TestCase):

    def setUp(self):
        BaseTestMixin.setUp(self)

    def tearDown(self):
        BaseTestMixin.tearDown(self)

    @requires_toolkit([ToolkitName.qt])
    def test_date_initialization(self):
        # Behavior: for a date initialized between maximum and minimum dates in
        # DatetimeEditor, that date should be unmodified

        dialog = DatetimeInitDailog()

        # verify that the date is correctly initialized
        self.assertEqual(dialog.date, DATE)

        with reraise_exceptions(), create_ui(dialog) as ui:
            # verify that the date hasn't changed after creating the ui
            self.assertEqual(dialog.date, DATE)
