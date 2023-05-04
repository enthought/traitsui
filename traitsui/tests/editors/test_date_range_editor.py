# (C) Copyright 2004-2023 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

import contextlib
import datetime
import unittest

from traits.api import (
    Date,
    HasTraits,
    TraitError,
    Tuple,
)
from traitsui.api import DateRangeEditor, View, Item

from traitsui.tests._tools import (
    BaseTestMixin,
    create_ui,
    requires_toolkit,
    ToolkitName,
)


class Foo(HasTraits):

    date_range = Tuple(Date(allow_none=True), Date(allow_none=True))


def default_custom_view():
    """Default view of DateRangeEditor"""
    view = View(
        Item(name="date_range", style="custom", editor=DateRangeEditor())
    )
    return view


def custom_view_allow_no_range():
    """DateRangeEditor with allow_no_selection set to True."""
    view = View(
        Item(
            name="date_range",
            style="custom",
            editor=DateRangeEditor(allow_no_selection=True),
        )
    )
    return view


class TestDateRangeEditorGeneric(BaseTestMixin, unittest.TestCase):
    """Tests that are not GUI backend specific."""

    def setUp(self):
        BaseTestMixin.setUp(self)

    def tearDown(self):
        BaseTestMixin.tearDown(self)

    def test_date_range_multi_select_is_constant(self):
        with self.assertRaises(TraitError):
            DateRangeEditor(multi_select=False)


@requires_toolkit([ToolkitName.qt])
class TestDateRangeEditorQt(BaseTestMixin, unittest.TestCase):
    def setUp(self):
        BaseTestMixin.setUp(self)

    def tearDown(self):
        BaseTestMixin.tearDown(self)

    def test_set_date_range_on_model(self):
        # Test when the date range is set on the model
        with self.launch_editor(default_custom_view) as (foo, editor):
            foo.date_range = (
                datetime.date(2010, 4, 3),
                datetime.date(2010, 4, 5),
            )

            expected_selected = [
                datetime.date(2010, 4, 3),
                datetime.date(2010, 4, 4),
                datetime.date(2010, 4, 5),
            ]
            for date in expected_selected:
                self.check_select_status(
                    editor=editor, date=date, selected=True
                )

            # Outside of the range
            self.check_select_status(
                editor=editor, date=datetime.date(2010, 4, 2), selected=False
            )
            self.check_select_status(
                editor=editor, date=datetime.date(2010, 4, 6), selected=False
            )

    def test_set_one_sided_range_error(self):

        with self.launch_editor(default_custom_view) as (_, editor):

            with self.assertRaises(ValueError) as exception_context:
                editor.value = (datetime.date(2010, 10, 3), None)
                editor.update_editor()

            self.assertIn(
                "The start and end dates must be either both defined or both "
                "be None",
                str(exception_context.exception),
            )

    def test_set_reverse_range_on_model(self):

        with self.launch_editor(default_custom_view) as (foo, editor):
            foo.date_range = (
                datetime.date(2010, 5, 3),
                datetime.date(2010, 5, 1),
            )

            # None of these dates should be selected
            dates = [
                datetime.date(2010, 5, 1),
                datetime.date(2010, 5, 2),
                datetime.date(2010, 5, 3),
            ]
            for date in dates:
                self.check_select_status(
                    editor=editor, date=date, selected=False
                )

    def test_set_date_range_on_editor(self):
        with self.launch_editor(default_custom_view) as (foo, editor):

            self.click_date_on_editor(editor, datetime.date(2012, 3, 4))
            self.click_date_on_editor(editor, datetime.date(2012, 3, 6))

            expected_selected = [
                datetime.date(2012, 3, 4),
                datetime.date(2012, 3, 5),
                datetime.date(2012, 3, 6),
            ]
            for date in expected_selected:
                self.check_select_status(
                    editor=editor, date=date, selected=True
                )

            self.assertEqual(
                foo.date_range,
                (datetime.date(2012, 3, 4), datetime.date(2012, 3, 6)),
            )

    def test_set_date_range_reset_when_click_outside(self):
        with self.launch_editor(default_custom_view) as (foo, editor):

            foo.date_range = (
                datetime.date(2012, 2, 10),
                datetime.date(2012, 2, 13),
            )
            self.click_date_on_editor(editor, datetime.date(2012, 2, 4))

            self.assertEqual(
                foo.date_range,
                (datetime.date(2012, 2, 4), datetime.date(2012, 2, 4)),
            )

    def test_set_date_range_reverse_order(self):
        # Test setting end date first then start date.
        with self.launch_editor(default_custom_view) as (foo, editor):

            self.click_date_on_editor(editor, datetime.date(2012, 3, 6))
            self.click_date_on_editor(editor, datetime.date(2012, 3, 4))

            expected_selected = [
                datetime.date(2012, 3, 4),
                datetime.date(2012, 3, 5),
                datetime.date(2012, 3, 6),
            ]
            for date in expected_selected:
                self.check_select_status(
                    editor=editor, date=date, selected=True
                )

            self.assertEqual(
                foo.date_range,
                (datetime.date(2012, 3, 4), datetime.date(2012, 3, 6)),
            )

    def test_allow_no_range(self):
        # Test clicking again will unset the range if allow_no_range is True

        with self.launch_editor(custom_view_allow_no_range) as (foo, editor):

            self.click_date_on_editor(editor, datetime.date(2012, 3, 6))
            self.click_date_on_editor(editor, datetime.date(2012, 3, 4))

            expected_selected = [
                datetime.date(2012, 3, 4),
                datetime.date(2012, 3, 5),
                datetime.date(2012, 3, 6),
            ]
            for date in expected_selected:
                self.check_select_status(
                    editor=editor, date=date, selected=True
                )

            # Click again
            self.click_date_on_editor(editor, datetime.date(2012, 3, 1))

            for date in expected_selected:
                self.check_select_status(
                    editor=editor, date=date, selected=False
                )

            self.assertEqual(foo.date_range, (None, None))

    # --------------------
    # Helper methods
    # --------------------

    @contextlib.contextmanager
    def launch_editor(self, view_factory):
        foo = Foo()
        with create_ui(foo, dict(view=view_factory())) as ui:
            (editor,) = ui._editors
            yield foo, editor

    def check_select_status(self, editor, date, selected):
        from pyface.qt import QtCore, QtGui

        qdate = QtCore.QDate(date.year, date.month, date.day)
        textformat = editor.control.dateTextFormat(qdate)
        if selected:
            self.assertEqual(
                textformat.fontWeight(),
                QtGui.QFont.Weight.Bold,
                "{!r} is not selected.".format(date),
            )

            self.assertEqual(
                textformat.background().color().green(),
                128,
                "Expected non-zero green color value.",
            )
        else:
            self.assertEqual(
                textformat.fontWeight(),
                QtGui.QFont.Weight.Normal,
                "{!r} is not unselected.".format(date),
            )
            self.assertEqual(
                textformat.background().style(),
                QtCore.Qt.BrushStyle.NoBrush,
                "Expected brush to have been reset.",
            )
            self.assertEqual(
                textformat.background().color().green(),
                0,
                "Expected color to have been reset.",
            )

    def click_date_on_editor(self, editor, date):
        from pyface.qt import QtCore

        # QCalendarWidget.setSelectedDate modifies internal state
        # instead of triggering the click signal.
        # So we call update_object directly
        editor.update_object(QtCore.QDate(date.year, date.month, date.day))
