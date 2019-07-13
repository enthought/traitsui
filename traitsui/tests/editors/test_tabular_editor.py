#------------------------------------------------------------------------------
#
#  Copyright (c) 2017, Enthought, Inc.
#  All rights reserved.
#
#  This software is provided without warranty under the terms of the BSD
#  license included in enthought/LICENSE.txt and may be redistributed only
#  under the conditions described in the aforementioned license.  The license
#  is also available online at http://www.enthought.com/licenses/BSD.txt
#------------------------------------------------------------------------------

from __future__ import absolute_import
import contextlib
import unittest

from traits.api import Event, HasTraits, Instance, Int, List, Unicode
from traits.testing.api import UnittestTools

from traitsui.api import Item, TabularEditor, View
from traitsui.tabular_adapter import TabularAdapter
from traitsui.tests._tools import skip_if_null


class Person(HasTraits):
    name = Unicode
    age = Int

    def __repr__(self):
        return "Person(name={self.name!r}, age={self.age!r})".format(self=self)

class ReportAdapter(TabularAdapter):
    columns = [
        ('Name', 'name'),
        ('Age', 'age'),
    ]


class Report(HasTraits):
    people = List(Person)

    selected = Instance(Person)

    selected_row = Int(-1)

    # Event for triggering a UI repaint.
    refresh = Event

    # Event for triggering a UI table update.
    update = Event

    traits_view = View(
        Item(
            name='people',
            editor=TabularEditor(
                adapter=ReportAdapter(),
                selected='selected',
                selected_row='selected_row',
                refresh='refresh',
                update='update',
            ),
        ),
    )


class TestTabularEditor(UnittestTools, unittest.TestCase):

    @skip_if_null
    def test_selected_reacts_to_model_changes(self):
        with self.report_and_editor() as (report, editor):
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

    @skip_if_null
    def test_event_synchronization(self):
        with self.report_and_editor() as (report, editor):
            with self.assertTraitChanges(editor, 'refresh', count=1):
                report.refresh = True
            # Should happen every time.
            with self.assertTraitChanges(editor, 'refresh', count=1):
                report.refresh = True

            with self.assertTraitChanges(editor, 'update', count=1):
                report.update = True
            with self.assertTraitChanges(editor, 'update', count=1):
                report.update = True

    @contextlib.contextmanager
    def report_and_editor(self):
        """
        Context manager to temporarily create and clean up a Report model object
        and the corresponding TabularEditor.
        """
        report = Report(
            people=[
                Person(name='Theresa', age=60),
                Person(name='Arlene', age=46),
            ],
        )
        ui = report.edit_traits()
        try:
            editor, = ui.get_editors('people')
            yield report, editor
        finally:
            ui.dispose()
