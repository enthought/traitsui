import datetime
import unittest

from traits.api import Date, HasTraits, List
from traitsui.api import DateEditor, View, Item

from traitsui.tests._tools import skip_if_not_qt4


class Foo(HasTraits):

    dates = List(Date)

    single_date = Date()


def single_select_custom_view():
    view = View(
        Item(
            name='single_date',
            style="custom",
            editor=DateEditor(multi_select=False),
        )
    )
    return view


def multi_select_custom_view():
    view = View(
        Item(
            name='dates',
            style="custom",
            editor=DateEditor(multi_select=True),
        )
    )
    return view


@skip_if_not_qt4
class TestDateEditorCustomQt(unittest.TestCase):

    def _get_custom_editor(self, view_factory):
        foo = Foo()
        ui = foo.edit_traits(view=view_factory())
        editor, = ui._editors
        return foo, ui, editor

    def test_multi_select_qt4(self):
        from pyface.qt import QtCore
        foo, ui, editor = self._get_custom_editor(multi_select_custom_view)
        editor.update_object(QtCore.QDate(2018, 2, 3))
        self.assertEqual(foo.dates, [datetime.date(2018, 2, 3)])

        editor.update_object(QtCore.QDate(2018, 2, 1))
        self.assertEqual(
            foo.dates,
            [datetime.date(2018, 2, 1), datetime.date(2018, 2, 3)]
        )
        ui.dispose()

    def test_single_select_qt4(self):
        from pyface.qt import QtCore
        foo, ui, editor = self._get_custom_editor(single_select_custom_view)
        editor.update_object(QtCore.QDate(2018, 2, 3))
        self.assertEqual(foo.single_date, datetime.date(2018, 2, 3))

        editor.update_object(QtCore.QDate(2018, 2, 5))
        self.assertEqual(foo.single_date, datetime.date(2018, 2, 5))
        ui.dispose()

    def test_multi_select_qt4_styles(self):
        from pyface.qt import QtCore, QtGui
        foo, ui, editor = self._get_custom_editor(multi_select_custom_view)
        qdates = [QtCore.QDate(2018, 2, 1), QtCore.QDate(2018, 2, 3)]
        for qdate in qdates:
            editor.update_object(qdate)

        for qdate in qdates:
            textformat = editor.control.dateTextFormat(qdate)
            self.assertEqual(textformat.fontWeight(), QtGui.QFont.Bold)
            self.assertEqual(textformat.background().color().green(), 128)

        textformat = editor.control.dateTextFormat(QtCore.QDate(2018, 2, 2))
        self.assertEqual(textformat.fontWeight(), QtGui.QFont.Normal)
        self.assertEqual(textformat.background().color().green(), 0)

    def test_multi_select_qt4_styles_reset(self):
        from pyface.qt import QtCore, QtGui
        foo, ui, editor = self._get_custom_editor(multi_select_custom_view)

        qdate = QtCore.QDate(2018, 2, 1)
        editor.update_object(qdate)
        textformat = editor.control.dateTextFormat(qdate)
        self.assertEqual(textformat.fontWeight(), QtGui.QFont.Bold)

        editor.update_object(qdate)
        textformat = editor.control.dateTextFormat(qdate)
        self.assertEqual(textformat.fontWeight(), QtGui.QFont.Normal)
        self.assertEqual(
            textformat.background().style(),
            0,   # Qt.BrushStyle.NoBrush,
        )

    def test_multi_select_qt4_set_model_dates(self):
        # Test setting the dates from the model object.
        from pyface.qt import QtCore, QtGui
        foo, ui, editor = self._get_custom_editor(multi_select_custom_view)
        foo.dates = [
            datetime.date(2010, 1, 2),
            datetime.date(2010, 2, 1),
        ]

        for date in foo.dates:
            qdate = QtCore.QDate(date.year, date.month, date.day)
            textformat = editor.control.dateTextFormat(qdate)
            self.assertEqual(textformat.fontWeight(), QtGui.QFont.Bold)
