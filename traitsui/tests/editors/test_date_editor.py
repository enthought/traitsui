import datetime
import unittest

from traits.api import Date, HasTraits, List
from traitsui.api import DateEditor, View, Item

from traitsui.tests._tools import skip_if_not_qt4, skip_if_not_wx


class Foo(HasTraits):

    dates = List(Date)


def multi_select_custom_view():
    view = View(
        Item(
            name='dates',
            style="custom",
            editor=DateEditor(multi_select=True),
        )
    )
    return view


class TestDateEditor(unittest.TestCase):

    def _get_custom_editor(self, view_factory):
        foo = Foo()
        ui = foo.edit_traits(view=view_factory())
        editor, = ui._editors
        return foo, ui, editor

    @skip_if_not_qt4
    def test_multi_select_qt4(self):
        from pyface.qt import QtCore
        foo, ui, editor = self._get_custom_editor(multi_select_custom_view)
        editor.update_object(QtCore.QDate(2018, 2, 3))
        self.assertEqual(foo.dates, [datetime.date(2018, 2, 3)])

        editor.update_object(QtCore.QDate(2018, 2, 5))
        self.assertEqual(
            foo.dates,
            [datetime.date(2018, 2, 3), datetime.date(2018, 2, 5)]
        )
        ui.dispose()
