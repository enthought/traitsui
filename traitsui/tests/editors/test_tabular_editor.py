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

import contextlib
import unittest

from traits.api import HasTraits, Instance, Int, List, Unicode
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

    traits_view = View(
        Item(
            name='people',
            editor=TabularEditor(
                adapter=ReportAdapter(),
                selected='selected',
                selected_row='selected_row',
            ),
        ),
    )


class TestTabularEditor(unittest.TestCase):

    @skip_if_null
    def test_selected_reacts_to_model_changes(self):
        with self.report_and_ui() as (report, ui):
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

    @contextlib.contextmanager
    def report_and_ui(self):
        """
        Context manager to temporarily create and clean up
        a Report and corresponding traitsui.ui.UI object.
        """
        report = Report(
            people=[
                Person(name='Theresa', age=60),
                Person(name='Arlene', age=46),
            ],
        )
        ui = report.edit_traits()
        try:
            yield report, ui
        finally:
            ui.dispose()
