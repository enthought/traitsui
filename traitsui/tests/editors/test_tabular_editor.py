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
import unittest

from traits.api import Event, HasTraits, Instance, Int, List, Str
from traits.testing.api import UnittestTools

from traitsui.api import Item, TabularEditor, View
from traitsui.tabular_adapter import TabularAdapter
from traitsui.tests._tools import (
    BaseTestMixin,
    create_ui,
    is_wx,
    is_qt,
    process_cascade_events,
    requires_toolkit,
    reraise_exceptions,
    ToolkitName,
)


class Person(HasTraits):
    name = Str()
    age = Int()

    def __repr__(self):
        return "Person(name={self.name!r}, age={self.age!r})".format(self=self)


class ReportAdapter(TabularAdapter):
    columns = [("Name", "name"), ("Age", "age")]


class Report(HasTraits):
    people = List(Person)

    selected = Instance(Person)

    selected_row = Int(-1)

    multi_selected = List(Instance(Person))

    selected_rows = List(Int())

    # Event for triggering a UI repaint.
    refresh = Event()

    # Event for triggering a UI table update.
    update = Event()


def get_view(multi_select=False):
    if multi_select:
        return View(
            Item(
                name="people",
                editor=TabularEditor(
                    adapter=ReportAdapter(),
                    selected="multi_selected",
                    selected_row="selected_rows",
                    refresh="refresh",
                    update="update",
                    multi_select=True,
                ),
            )
        )
    else:
        return View(
            Item(
                name="people",
                editor=TabularEditor(
                    adapter=ReportAdapter(),
                    selected="selected",
                    selected_row="selected_row",
                    refresh="refresh",
                    update="update",
                ),
            )
        )


def get_selected_rows(editor):
    """Returns a list of all currently selected rows."""
    if is_wx():
        import wx

        # "item" in this context means "row number"
        item = -1
        selected = []
        while True:
            item = editor.control.GetNextItem(
                item, wx.LIST_NEXT_ALL, wx.LIST_STATE_SELECTED
            )
            if item == -1:
                break
            selected.append(item)
        return selected

    elif is_qt():
        rows = editor.control.selectionModel().selectedRows()
        return [r.row() for r in rows]

    else:
        raise unittest.SkipTest("Test not implemented for this toolkit")


def set_selected_single(editor, row):
    """Selects a specified row in an editor with multi_select=False."""
    if is_wx():
        editor.control.Select(row)

    elif is_qt():
        from pyface.qt.QtGui import QItemSelectionModel

        smodel = editor.control.selectionModel()
        mi = editor.model.index(row, 0)
        # Add `Rows` flag to select the whole row
        smodel.select(
            mi, QItemSelectionModel.SelectionFlag.ClearAndSelect | QItemSelectionModel.SelectionFlag.Rows
        )

    else:
        raise unittest.SkipTest("Test not implemented for this toolkit")


def set_selected_multiple(editor, rows):
    """Clears old selection and selects specified rows in an editor
    with multi_select=True.
    """
    if is_wx():
        clear_selection(editor)
        for row in rows:
            editor.control.Select(row)

    elif is_qt():
        from pyface.qt.QtGui import QItemSelectionModel

        clear_selection(editor)
        smodel = editor.control.selectionModel()
        for row in rows:
            mi = editor.model.index(row, 0)
            # Add `Rows` flag to select the whole row
            smodel.select(
                mi, QItemSelectionModel.SelectionFlag.Select | QItemSelectionModel.SelectionFlag.Rows
            )

    else:
        raise unittest.SkipTest("Test not implemented for this toolkit")


def clear_selection(editor):
    """Clears existing selection."""
    if is_wx():
        import wx

        currently_selected = get_selected_rows(editor)
        # Deselect all currently selected items
        for selected_row in currently_selected:
            editor.control.SetItemState(
                selected_row, 0, wx.LIST_STATE_SELECTED
            )

    elif is_qt():
        editor.control.selectionModel().clearSelection()

    else:
        raise unittest.SkipTest("Test not implemented for this toolkit")


@requires_toolkit([ToolkitName.qt, ToolkitName.wx])
class TestTabularEditor(BaseTestMixin, UnittestTools, unittest.TestCase):
    def setUp(self):
        BaseTestMixin.setUp(self)

    def tearDown(self):
        BaseTestMixin.tearDown(self)

    @unittest.skipIf(is_wx(), "Issue enthought/traitsui#752")
    def test_tabular_editor_single_selection(self):

        with reraise_exceptions(), self.report_and_editor(get_view()) as (
            report,
            editor,
        ):
            process_cascade_events()
            people = report.people

            self.assertEqual(report.selected_row, -1)
            self.assertIsNone(report.selected)

            set_selected_single(editor, 1)
            process_cascade_events()

            self.assertEqual(report.selected_row, 1)
            self.assertEqual(report.selected, people[1])

            set_selected_single(editor, 2)
            process_cascade_events()

            self.assertEqual(report.selected_row, 2)
            self.assertEqual(report.selected, people[2])

            # Can't clear selection via UI when multi_select=False

    @unittest.skipIf(is_wx(), "Issue enthought/traitsui#752")
    def test_tabular_editor_multi_selection(self):
        view = get_view(multi_select=True)

        with reraise_exceptions(), self.report_and_editor(view) as (
            report,
            editor,
        ):
            process_cascade_events()
            people = report.people

            self.assertEqual(report.selected_rows, [])
            self.assertEqual(report.multi_selected, [])

            set_selected_multiple(editor, [0, 1])
            process_cascade_events()

            self.assertEqual(report.selected_rows, [0, 1])
            self.assertEqual(report.multi_selected, people[:2])

            set_selected_multiple(editor, [2])
            process_cascade_events()

            self.assertEqual(report.selected_rows, [2])
            self.assertEqual(report.multi_selected, [people[2]])

            clear_selection(editor)
            process_cascade_events()

            self.assertEqual(report.selected_rows, [])
            self.assertEqual(report.multi_selected, [])

    @unittest.skipIf(is_wx(), "Issue enthought/traitsui#752")
    def test_tabular_editor_single_selection_changed(self):

        with reraise_exceptions(), self.report_and_editor(get_view()) as (
            report,
            editor,
        ):
            process_cascade_events()
            people = report.people

            self.assertEqual(get_selected_rows(editor), [])

            report.selected_row = 1
            process_cascade_events()

            self.assertEqual(get_selected_rows(editor), [1])
            self.assertEqual(report.selected, people[1])

            report.selected = people[2]
            process_cascade_events()

            self.assertEqual(get_selected_rows(editor), [2])
            self.assertEqual(report.selected_row, 2)

            # Selected set to invalid value doesn't change anything
            report.selected = Person(name="invalid", age=-1)
            process_cascade_events()

            self.assertEqual(get_selected_rows(editor), [2])
            self.assertEqual(report.selected_row, 2)

            # -1 clears selection
            report.selected_row = -1
            process_cascade_events()

            self.assertEqual(get_selected_rows(editor), [])
            self.assertEqual(report.selected, None)

    @unittest.skipIf(is_wx(), "Issue enthought/traitsui#752")
    def test_tabular_editor_multi_selection_changed(self):
        view = get_view(multi_select=True)

        with reraise_exceptions(), self.report_and_editor(view) as (
            report,
            editor,
        ):
            process_cascade_events()
            people = report.people

            self.assertEqual(get_selected_rows(editor), [])

            report.selected_rows = [0, 1]
            process_cascade_events()

            self.assertEqual(get_selected_rows(editor), [0, 1])
            self.assertEqual(report.multi_selected, people[:2])

            report.multi_selected = [people[2], people[0]]
            process_cascade_events()

            self.assertEqual(sorted(get_selected_rows(editor)), [0, 2])
            self.assertEqual(sorted(report.selected_rows), [0, 2])

            # If there's a single invalid value, nothing is updated
            invalid_person = Person(name="invalid", age=-1)
            report.multi_selected = [people[2], invalid_person]
            process_cascade_events()

            self.assertEqual(sorted(get_selected_rows(editor)), [0, 2])
            self.assertEqual(sorted(report.selected_rows), [0, 2])

            # Empty list clears selection
            report.selected_rows = []
            process_cascade_events()

            self.assertEqual(get_selected_rows(editor), [])
            self.assertEqual(report.multi_selected, [])

    @unittest.skipIf(is_wx(), "Issue enthought/traitsui#752")
    def test_tabular_editor_multi_selection_items_changed(self):
        view = get_view(multi_select=True)

        with reraise_exceptions(), self.report_and_editor(view) as (
            report,
            editor,
        ):
            process_cascade_events()
            people = report.people

            self.assertEqual(get_selected_rows(editor), [])

            report.selected_rows.extend([0, 1])
            process_cascade_events()

            self.assertEqual(get_selected_rows(editor), [0, 1])
            self.assertEqual(report.multi_selected, people[:2])

            report.selected_rows[1] = 2
            process_cascade_events()

            self.assertEqual(get_selected_rows(editor), [0, 2])
            self.assertEqual(report.multi_selected, people[0:3:2])

            report.multi_selected[0] = people[1]
            process_cascade_events()

            self.assertEqual(sorted(get_selected_rows(editor)), [1, 2])
            self.assertEqual(sorted(report.selected_rows), [1, 2])

            # If there's a single invalid value, nothing is updated
            report.multi_selected[0] = Person(name="invalid", age=-1)
            process_cascade_events()

            self.assertEqual(sorted(get_selected_rows(editor)), [1, 2])
            self.assertEqual(sorted(report.selected_rows), [1, 2])

    @unittest.skipIf(is_wx(), "Issue enthought/traitsui#752")
    def test_selected_reacts_to_model_changes(self):
        with self.report_and_editor(get_view()) as (report, editor):
            people = report.people

            self.assertIsNone(report.selected)
            self.assertEqual(report.selected_row, -1)

            report.selected = people[1]
            self.assertEqual(report.selected, people[1])
            self.assertEqual(report.selected_row, 1)

            report.selected = None
            self.assertIsNone(report.selected)
            self.assertEqual(report.selected_row, -1)

            report.selected_row = 0
            self.assertEqual(report.selected, people[0])
            self.assertEqual(report.selected_row, 0)

            report.selected_row = -1
            self.assertIsNone(report.selected)
            self.assertEqual(report.selected_row, -1)

    @unittest.skipIf(is_wx(), "Issue enthought/traitsui#752")
    def test_event_synchronization(self):
        with self.report_and_editor(get_view()) as (report, editor):
            with self.assertTraitChanges(editor, "refresh", count=1):
                report.refresh = True
            # Should happen every time.
            with self.assertTraitChanges(editor, "refresh", count=1):
                report.refresh = True

            with self.assertTraitChanges(editor, "update", count=1):
                report.update = True
            with self.assertTraitChanges(editor, "update", count=1):
                report.update = True

    @unittest.skipIf(is_wx(), "Issue enthought/traitsui#752")
    def test_adapter_columns_changes(self):
        # Regression test for enthought/traitsui#894
        with reraise_exceptions(), self.report_and_editor(get_view()) as (
            report,
            editor,
        ):

            # Reproduce the scenario when the column count is reduced.
            editor.adapter.columns = [
                ("Name", "name"),
                ("Age", "age"),
            ]
            # Recalculating column widths take into account the user defined
            # widths, cached in the view. The cache should be invalidated
            # when the columns is updated such that recalculation does not
            # fail.
            editor.adapter.columns = [("Name", "name")]
            process_cascade_events()

    @unittest.skipIf(is_wx(), "Issue enthought/traitsui#752")
    def test_view_column_resized_attribute_error_workaround(self):
        # This tests the workaround which checks if `factory` is None before
        # using it while resizing the columns.
        # The resize event is processed after UI.dispose is called.
        # Maybe related to enthought/traits#431
        with reraise_exceptions(), self.report_and_editor(get_view()) as (
            _,
            editor,
        ):
            editor.adapter.columns = [("Name", "name")]

    @contextlib.contextmanager
    def report_and_editor(self, view):
        """
        Context manager to temporarily create and clean up a Report model
        object and the corresponding TabularEditor.
        """
        report = Report(
            people=[
                Person(name="Theresa", age=60),
                Person(name="Arlene", age=46),
                Person(name="Karen", age=40),
            ]
        )
        with create_ui(report, dict(view=view)) as ui:
            (editor,) = ui.get_editors("people")
            yield report, editor
