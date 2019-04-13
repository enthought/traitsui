import datetime
import unittest

from traits.api import (
    Date, HasTraits, Tuple, pop_exception_handler, push_exception_handler)
from traitsui.api import DateRangeEditor, View, Item

from traitsui.tests._tools import skip_if_not_qt4


class Foo(HasTraits):

    date_range = Tuple(Date, Date)


def default_custom_view():
    """ Default view of DateRangeEditor """
    view = View(
        Item(
            name='date_range',
            style="custom",
            editor=DateRangeEditor(),
        )
    )
    return view


def custom_view_allow_no_range():
    """ DateRangeEditor with allow_no_range set to True."""
    view = View(
        Item(
            name='date_range',
            style="custom",
            editor=DateRangeEditor(allow_no_range=True),
        )
    )
    return view


@skip_if_not_qt4
class TestDateRangeEditorQt(unittest.TestCase):

    def setUp(self):
        push_exception_handler(reraise_exceptions=True)
        self.addCleanup(pop_exception_handler)

    def test_date_range_editor_default(self):
        self.get_custom_editor(default_custom_view)

    def test_set_date_range_on_model(self):
        # Test when the date range is set on the model
        foo, _, editor = self.get_custom_editor(default_custom_view)
        foo.date_range = (datetime.date(2010, 4, 3), datetime.date(2010, 4, 5))

        expected_selected = [
            datetime.date(2010, 4, 3),
            datetime.date(2010, 4, 4),
            datetime.date(2010, 4, 5)
        ]
        for date in expected_selected:
            self.check_select_status(editor=editor, date=date, selected=True)

        # Outside of the range
        self.check_select_status(
            editor=editor, date=datetime.date(2010, 4, 2), selected=False)
        self.check_select_status(
            editor=editor, date=datetime.date(2010, 4, 6), selected=False)

    def test_set_one_sided_range_error(self):
        _, _, editor = self.get_custom_editor(default_custom_view)

        with self.assertRaises(ValueError) as exception_context:
            editor.value = (datetime.date(2010, 10, 3), None)
            editor.update_editor()

        self.assertIn(
            "The start and end dates must be either both defined or both "
            "be None",
            str(exception_context.exception),
        )

    def test_set_reverse_range_on_model(self):
        foo, _, editor = self.get_custom_editor(default_custom_view)
        foo.date_range = (datetime.date(2010, 5, 3), datetime.date(2010, 5, 1))

        # None of these dates should be selected
        dates = [
            datetime.date(2010, 5, 1),
            datetime.date(2010, 5, 2),
            datetime.date(2010, 5, 3),
        ]
        for date in dates:
            self.check_select_status(editor=editor, date=date, selected=False)

    def test_set_date_range_on_editor(self):
        foo, _, editor = self.get_custom_editor(default_custom_view)

        self.click_date_on_editor(editor, datetime.date(2012, 3, 4))
        self.click_date_on_editor(editor, datetime.date(2012, 3, 6))

        expected_selected = [
            datetime.date(2012, 3, 4),
            datetime.date(2012, 3, 5),
            datetime.date(2012, 3, 6),
        ]
        for date in expected_selected:
            self.check_select_status(editor=editor, date=date, selected=True)

        self.assertEqual(
            foo.date_range,
            (datetime.date(2012, 3, 4), datetime.date(2012, 3, 6)))

    def test_set_date_range_reset_when_click_outside(self):
        foo, _, editor = self.get_custom_editor(default_custom_view)

        foo.date_range = (
            datetime.date(2012, 2, 10), datetime.date(2012, 2, 13),
        )
        self.click_date_on_editor(editor, datetime.date(2012, 2, 4))

        self.assertEqual(
            foo.date_range,
            (datetime.date(2012, 2, 4), datetime.date(2012, 2, 4)))

    def test_set_date_range_reverse_order(self):
        # Test setting end date first then start date.
        foo, _, editor = self.get_custom_editor(default_custom_view)

        self.click_date_on_editor(editor, datetime.date(2012, 3, 6))
        self.click_date_on_editor(editor, datetime.date(2012, 3, 4))

        expected_selected = [
            datetime.date(2012, 3, 4),
            datetime.date(2012, 3, 5),
            datetime.date(2012, 3, 6),
        ]
        for date in expected_selected:
            self.check_select_status(editor=editor, date=date, selected=True)

        self.assertEqual(
            foo.date_range,
            (datetime.date(2012, 3, 4), datetime.date(2012, 3, 6)))

    def test_allow_no_range(self):
        # Test clicking again will unset the range
        foo, _, editor = self.get_custom_editor(custom_view_allow_no_range)

        self.click_date_on_editor(editor, datetime.date(2012, 3, 6))
        self.click_date_on_editor(editor, datetime.date(2012, 3, 4))

        expected_selected = [
            datetime.date(2012, 3, 4),
            datetime.date(2012, 3, 5),
            datetime.date(2012, 3, 6),
        ]
        for date in expected_selected:
            self.check_select_status(editor=editor, date=date, selected=True)

        # Click again
        self.click_date_on_editor(editor, datetime.date(2012, 3, 1))

        for date in expected_selected:
            self.check_select_status(editor=editor, date=date, selected=False)

        self.assertEqual(foo.date_range, (None, None))

    # --------------------
    # Helper methods
    # --------------------

    def get_custom_editor(self, view_factory):
        foo = Foo()
        ui = foo.edit_traits(view=view_factory())
        editor, = ui._editors
        return foo, ui, editor

    def check_select_status(self, editor, date, selected):
        from pyface.qt import QtCore, QtGui
        qdate = QtCore.QDate(date.year, date.month, date.day)
        textformat = editor.control.dateTextFormat(qdate)
        if selected:
            self.assertEqual(
                textformat.fontWeight(),
                QtGui.QFont.Bold,
                "{!r} is not selected.".format(date))
        else:
            self.assertEqual(
                textformat.fontWeight(),
                QtGui.QFont.Normal,
                "{!r} is not unselected.".format(date),
            )

    def click_date_on_editor(self, editor, date):
        from pyface.qt import QtCore
        # QCalendarWidget.setSelectedDate modifies internal state
        # instead of triggering the click signal.
        # So we call update_object directly
        editor.update_object(
            QtCore.QDate(date.year, date.month, date.day))