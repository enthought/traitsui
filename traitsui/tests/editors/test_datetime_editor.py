import contextlib
import datetime
import unittest

from traits.api import HasTraits, Datetime
from traitsui.api import DatetimeEditor, Item, View
from traitsui.tests._tools import (
    GuiTestAssistant,
    skip_if_not_qt4,
    no_gui_test_assistant,
)

class InstanceWithDatetime(HasTraits):
    """ Demo class to show Datetime editors. """
    date_time = Datetime()


def to_datetime(q_datetime):
    try:
        return q_datetime.toPyDateTime()
    except AttributeError:
        return q_datetime.toPython()


def get_date_time_simple_view(editor_factory):
    view = View(
        Item(
            name="date_time",
            style="simple",
            editor=editor_factory,
        )
    )
    return view


@skip_if_not_qt4
@unittest.skipIf(no_gui_test_assistant, "No GuiTestAssistant")
class TestDatetimeEditorQt(GuiTestAssistant, unittest.TestCase):
    """ Tests for DatetimeEditor using Qt. """

    def test_datetime_editor_simple(self):
        view = get_date_time_simple_view(DatetimeEditor())
        instance = InstanceWithDatetime(date_time=datetime.datetime.now())
        with self.launch_editor(instance, view):
            pass

    def test_datetime_editor_simple_with_minimum_datetime(self):
        # Test the editor uses the minimum datetime as expected
        minimum_datetime = datetime.datetime(2000, 1, 1)
        editor_factory = DatetimeEditor(
            minimum_datetime=minimum_datetime,
        )
        view = get_date_time_simple_view(editor_factory)
        instance = InstanceWithDatetime()
        with self.launch_editor(instance, view) as editor:
            q_minimum_datetime = editor.control.minimumDateTime()
            actual_minimum_datetime = to_datetime(q_minimum_datetime)

        self.assertEqual(actual_minimum_datetime, minimum_datetime)

    def test_datetime_editor_simple_with_minimum_datetime_out_of_bound(self):
        # Test when out-of-bound value is given, it is reset to the bounded
        # value.
        minimum_datetime = datetime.datetime(2000, 1, 1)
        editor_factory = DatetimeEditor(
            minimum_datetime=minimum_datetime,
        )
        view = get_date_time_simple_view(editor_factory)
        instance = InstanceWithDatetime()
        with self.launch_editor(instance, view) as editor:
            instance.date_time = datetime.datetime(1980, 1, 1)

            # does not seem needed to flush the event loop, but just in case.
            self.gui.process_events()

            displayed_value = to_datetime(editor.control.dateTime())

        self.assertEqual(displayed_value, minimum_datetime)
        self.assertEqual(instance.date_time, minimum_datetime)

    def test_datetime_editor_mutate_minimum_datetime_after_init(self):
        # Test if the minimum_datetime on the editor is mutated after init,
        # the values on the edited object and the view are synchronized.
        editor_factory = DatetimeEditor(
            minimum_datetime=datetime.datetime(2000, 1, 1),
        )
        view = get_date_time_simple_view(editor_factory)
        instance = InstanceWithDatetime()
        with self.launch_editor(instance, view) as editor:

            # This value is in-range
            instance.date_time = datetime.datetime(2001, 1, 1)

            # Now change the editor's minimum datetime such that the original
            # value is out-of-range
            new_minimum_datetime = datetime.datetime(2010, 1, 1)
            editor.minimum_datetime = new_minimum_datetime

            # does not seem needed to flush the event loop, but just in case.
            self.gui.process_events()

            displayed_value = to_datetime(editor.control.dateTime())

        self.assertEqual(instance.date_time, displayed_value)
        self.assertEqual(displayed_value, new_minimum_datetime)

    def test_datetime_editor_mutate_minimum_datetime_bad_order(self):
        # Test if the minimum_datetime on the editor is mutated after init,
        # the values on the edited object and the view are synchronized.
        editor_factory = DatetimeEditor(
            minimum_datetime=datetime.datetime(2000, 1, 1),
            maximum_datetime=datetime.datetime(2010, 1, 1),
        )
        view = get_date_time_simple_view(editor_factory)
        instance = InstanceWithDatetime()
        with self.launch_editor(instance, view) as editor:

            # This value is in-range
            instance.date_time = datetime.datetime(2001, 1, 1)

            # Now change the editor's minimum datetime such that the original
            # value is out-of-range and the minimum is greater than maximum
            new_minimum_datetime = datetime.datetime(2020, 1, 1)
            editor.minimum_datetime = new_minimum_datetime

            # does not seem needed to flush the event loop, but just in case.
            self.gui.process_events()

            displayed_value = to_datetime(editor.control.dateTime())

        self.assertEqual(instance.date_time, displayed_value)
        self.assertEqual(displayed_value, new_minimum_datetime)
        self.assertEqual(editor.maximum_datetime, new_minimum_datetime)

    def test_datetime_editor_simple_with_maximum_datetime(self):
        # Test the editor uses the maximum datetime as expected
        maximum_datetime = datetime.datetime(2000, 1, 1)
        editor_factory = DatetimeEditor(
            maximum_datetime=maximum_datetime,
        )
        view = get_date_time_simple_view(editor_factory)
        instance = InstanceWithDatetime()
        with self.launch_editor(instance, view) as editor:
            q_maximum_datetime = editor.control.maximumDateTime()

            # does not seem needed to flush the event loop, but just in case.
            self.gui.process_events()

            actual_maximum_datetime = to_datetime(q_maximum_datetime)

        self.assertEqual(actual_maximum_datetime, maximum_datetime)

    def test_datetime_editor_simple_with_maximum_datetime_out_of_bound(self):
        maximum_datetime = datetime.datetime(2000, 1, 1)
        editor_factory = DatetimeEditor(
            maximum_datetime=maximum_datetime,
        )
        view = get_date_time_simple_view(editor_factory)
        instance = InstanceWithDatetime()
        with self.launch_editor(instance, view) as editor:
            # out-of-bound
            instance.date_time = datetime.datetime(2020, 1, 1)

            # does not seem needed to flush the event loop, but just in case.
            self.gui.process_events()

            displayed_value = to_datetime(editor.control.dateTime())

        self.assertEqual(displayed_value, maximum_datetime)
        self.assertEqual(instance.date_time, maximum_datetime)

    def test_datetime_editor_mutate_maximum_datetime_after_init(self):
        # Test if the maximum_datetime on the editor is mutated after init,
        # the values on the edited object and the view are synchronized.
        editor_factory = DatetimeEditor(
            maximum_datetime=datetime.datetime(2000, 1, 1),
        )
        view = get_date_time_simple_view(editor_factory)
        instance = InstanceWithDatetime()
        with self.launch_editor(instance, view) as editor:

            # This value is in-range
            instance.date_time = datetime.datetime(1999, 1, 1)

            # Now change the editor's maximum datetime such that the original
            # value is out-of-range
            new_maximum_datetime = datetime.datetime(1900, 1, 1)
            editor.maximum_datetime = new_maximum_datetime

            # does not seem needed to flush the event loop, but just in case.
            self.gui.process_events()

            displayed_value = to_datetime(editor.control.dateTime())

        self.assertEqual(instance.date_time, displayed_value)
        self.assertEqual(displayed_value, new_maximum_datetime)

    def test_datetime_editor_python_datetime_out_of_bound(self):
        # The minimum datetime supported by Qt is larger than the minimum
        # datetime supported by Python.
        editor_factory = DatetimeEditor()
        view = get_date_time_simple_view(editor_factory)
        init_datetime = datetime.datetime(1900, 1, 1)
        instance = InstanceWithDatetime(date_time=init_datetime)
        with self.launch_editor(instance, view) as editor:
            # This value is too early and is not supported by Qt
            # But the editor should not crash
            new_value = datetime.datetime(1, 1, 1)
            instance.date_time = new_value

            # does not seem needed to flush the event loop, but just in case.
            self.gui.process_events()

            displayed_value = to_datetime(editor.control.dateTime())

        # The value has changed to a filled value
        self.assertNotEqual(instance.date_time, new_value)
        self.assertEqual(displayed_value, instance.date_time)

    def test_datetime_editor_qt_datetime_out_of_bound(self):
        # The maximum datetime supported by Qt is larger than the maximum
        # datetime supported by Python
        editor_factory = DatetimeEditor()
        view = get_date_time_simple_view(editor_factory)
        init_datetime = datetime.datetime(1900, 1, 1)
        instance = InstanceWithDatetime(date_time=init_datetime)
        with self.launch_editor(instance, view) as editor:
            # the user set the datetime on the Qt widget to a value
            # too large for Python
            from pyface.qt.QtCore import QDateTime, QDate
            q_datetime = QDateTime(QDate(datetime.MAXYEAR + 1, 1, 1))
            editor.control.setDateTime(q_datetime)

            # Get the displayed value back.
            displayed_value = to_datetime(editor.control.dateTime())

        self.assertEqual(instance.date_time, displayed_value)

    @contextlib.contextmanager
    def launch_editor(self, object, view):
        ui = object.edit_traits(view=view)
        try:
            editor, = ui._editors
            yield editor
        finally:
            ui.dispose()