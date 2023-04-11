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

from traits.api import Date, HasTraits, List
from traitsui.api import DateEditor, View, Item
from traitsui.editors.date_editor import CellFormat

from traitsui.tests._tools import (
    BaseTestMixin,
    create_ui,
    requires_toolkit,
    reraise_exceptions,
    ToolkitName,
)


class Foo(HasTraits):

    dates = List(Date)

    single_date = Date()


def single_select_custom_view():
    view = View(
        Item(
            name="single_date",
            style="custom",
            editor=DateEditor(multi_select=False),
        )
    )
    return view


def multi_select_custom_view():
    view = View(
        Item(
            name="dates", style="custom", editor=DateEditor(multi_select=True)
        )
    )
    return view


def multi_select_selected_color_view():
    view = View(
        Item(
            name="dates",
            style="custom",
            editor=DateEditor(
                multi_select=True,
                selected_style=CellFormat(bold=True, bgcolor=(128, 10, 0)),
            ),
        )
    )
    return view


@requires_toolkit([ToolkitName.qt])
class TestDateEditorCustomQt(BaseTestMixin, unittest.TestCase):
    def setUp(self):
        BaseTestMixin.setUp(self)

    def tearDown(self):
        BaseTestMixin.tearDown(self)

    def test_single_select_qt(self):
        with self.launch_editor(single_select_custom_view) as (foo, editor):
            date = datetime.date(2018, 2, 3)
            self.click_date_on_editor(editor, date)
            self.assertEqual(foo.single_date, date)

    def test_multi_select_dates_on_editor(self):
        with self.launch_editor(multi_select_custom_view) as (foo, editor):
            dates = [datetime.date(2018, 2, 3), datetime.date(2018, 2, 1)]
            for date in dates:
                self.click_date_on_editor(editor, date)

            for date in dates:
                self.check_select_status(
                    editor=editor, date=date, selected=True
                )

            self.assertEqual(foo.dates, sorted(dates))

    def test_multi_select_qt_styles_reset(self):
        with self.launch_editor(multi_select_custom_view) as (foo, editor):
            date = datetime.date(2018, 2, 1)
            self.click_date_on_editor(editor, date)
            self.check_select_status(editor=editor, date=date, selected=True)

            self.click_date_on_editor(editor, date)
            self.check_select_status(editor=editor, date=date, selected=False)

    def test_multi_select_qt_set_model_dates(self):
        # Test setting the dates from the model object.
        with self.launch_editor(multi_select_custom_view) as (foo, editor):
            foo.dates = [datetime.date(2010, 1, 2), datetime.date(2010, 2, 1)]

            for date in foo.dates:
                self.check_select_status(
                    editor=editor, date=date, selected=True
                )

    def test_custom_selected_color(self):
        view_factory = multi_select_selected_color_view
        with self.launch_editor(view_factory) as (foo, editor):
            date = datetime.date(2011, 3, 4)
            foo.dates = [date]

            self.check_date_bgcolor(editor, date, (128, 10, 0))

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
            self.check_date_bgcolor(editor, date, (0, 128, 0))
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
            self.check_date_bgcolor(editor, date, (0, 0, 0))

    def click_date_on_editor(self, editor, date):
        from pyface.qt import QtCore

        # QCalendarWidget.setSelectedDate modifies internal state
        # instead of triggering the click signal.
        # So we call update_object directly
        editor.update_object(QtCore.QDate(date.year, date.month, date.day))

    def check_date_bgcolor(self, editor, date, expected):
        from pyface.qt import QtCore

        qdate = QtCore.QDate(date.year, date.month, date.day)
        textformat = editor.control.dateTextFormat(qdate)

        color = textformat.background().color()
        actual = (color.red(), color.green(), color.blue())
        self.assertEqual(
            actual,
            expected,
            "Expected color: {!r}. Got color: {!r}".format(expected, actual),
        )


# Run this test case against wx too once enthought/traitsui#752 is fixed.
@requires_toolkit([ToolkitName.qt])
class TestDateEditorInitDispose(unittest.TestCase):
    """Test the init and dispose of date editor."""

    def check_init_and_dispose(self, view):
        with reraise_exceptions(), create_ui(Foo(), dict(view=view)):
            pass

    def test_simple_date_editor(self):
        view = View(
            Item(
                name="single_date",
                style="simple",
            )
        )
        self.check_init_and_dispose(view)

    def test_custom_date_editor(self):
        view = View(
            Item(
                name="single_date",
                style="custom",
            )
        )
        self.check_init_and_dispose(view)
