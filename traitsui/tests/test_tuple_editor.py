#------------------------------------------------------------------------------
#
#  Copyright (c) 2014, Enthought, Inc.
#  All rights reserved.
#
#  This software is provided without warranty under the terms of the BSD
#  license included in enthought/LICENSE.txt and may be redistributed only
#  under the conditions described in the aforementioned license.  The license
#  is also available online at http://www.enthought.com/licenses/BSD.txt
#
#  Author: Ioannis Tziakos
#  Date:   Aug 2014
#
#------------------------------------------------------------------------------
"""
Test cases for the TupleEditor object.
"""

import unittest

from traits.api import Float, Int, HasStrictTraits, Str, Tuple, ValidatedTuple
from traits.testing.api import UnittestTools

from traitsui.tests._tools import dispose_ui, get_traitsui_editor


class DummyModel(HasStrictTraits):

    value_range = ValidatedTuple(
        Int(0), Int(1), validation=lambda x: x[0] < x[1])

    data = Tuple(Float, Float, Str)


class TestTupleEditor(UnittestTools, unittest.TestCase):

    def setUp(self):
        from traitsui.api import TupleEditor
        self.tuple_editor = TupleEditor

    def test_value_update(self):
        # Regression test for #179

        dummy_model = DummyModel()
        with dispose_ui(dummy_model.edit_traits):
            with self.assertTraitChanges(dummy_model, 'data', count=1):
                dummy_model.data = (3, 4.6, 'nono')

    def test_ui_creation(self):
        dummy_model = DummyModel()
        with dispose_ui(dummy_model.edit_traits) as ui:
            editor = get_traitsui_editor(ui, 'value_range')
            self.assertIsInstance(editor.factory, self.tuple_editor)
            self.assertEqual(editor.value, (0, 1))
            self.assertEqual(
                editor._ts.trait_get(['f0', 'f1', 'invalid0', 'invalid1']),
                {'f0': 0, 'f1': 1, 'invalid0': False, 'invalid1': False})

            editor = get_traitsui_editor(ui, 'data')
            self.assertIsInstance(editor.factory, self.tuple_editor)
            self.assertEqual(editor.value, (0.0, 0.0, ''))
            self.assertEqual(
                editor._ts.trait_get(
                    ['f0', 'f1', 'f2', 'invalid0', 'invalid1', 'invalid2']),
                {'f0': 0.0, 'f1': 0.0, 'f2': ''})

    def test_ui_invalid_due_to_failing_custom_validate(self):
        dummy_model = DummyModel()
        with dispose_ui(dummy_model.edit_traits) as ui:
            editor = get_traitsui_editor(ui, 'value_range')
            fields_ui = editor._ui
            f0_editor = get_traitsui_editor(fields_ui, 'f0')
            f1_editor = get_traitsui_editor(fields_ui, 'f1')

            f0_editor.value = 5  # 5 < 1 -> invalid
            self.assertTrue(f0_editor.invalid)
            self.assertFalse(f1_editor.invalid)
            self.assertEqual(editor.value, (0, 1))

            f0_editor.value = -3  # -3 < 1 -> valid
            self.assertFalse(f0_editor.invalid)
            self.assertFalse(f1_editor.invalid)
            self.assertEqual(editor.value, (-3, 1))

            f1_editor.value = -4  # -3 < -4 -> invalid
            self.assertFalse(f0_editor.invalid)
            self.assertTrue(f1_editor.invalid)
            self.assertEqual(editor.value, (-3, 1))

            f1_editor.value = 0  # -3 < 0 -> valid
            self.assertFalse(f0_editor.invalid)
            self.assertFalse(f1_editor.invalid)
            self.assertEqual(editor.value, (-3, 0))

    def test_when_editor_is_used_with_vertical_layout(self):

        class VSimple(HasStrictTraits):

            value_range = ValidatedTuple(
                Int(0), Int(1), cols=1, validation=lambda x: x[0] < x[1])

        dummy_model = VSimple()
        with dispose_ui(dummy_model.edit_traits) as ui:
            editor = get_traitsui_editor(ui, 'value_range')
            self.assertIsInstance(editor.factory, self.tuple_editor)
            self.assertEqual(editor.value, (0, 1))
            self.assertEqual(
                editor._ts.trait_get(['f0', 'f1', 'invalid0', 'invalid1']),
                {'f0': 0, 'f1': 1, 'invalid0': False, 'invalid1': False})

    def test_when_editor_is_used_with_horizontal_layout(self):

        class HSimple(HasStrictTraits):

            value_range = ValidatedTuple(
                Int(0), Int(1), cols=2, validation=lambda x: x[0] < x[1])

        dummy_model = HSimple()
        with dispose_ui(dummy_model.edit_traits) as ui:
            editor = get_traitsui_editor(ui, 'value_range')
            self.assertIsInstance(editor.factory, self.tuple_editor)
            self.assertEqual(editor.value, (0, 1))
            self.assertEqual(
                editor._ts.trait_get(['f0', 'f1', 'invalid0', 'invalid1']),
                {'f0': 0, 'f1': 1, 'invalid0': False, 'invalid1': False})

    def test_when_editor_is_used_in_the_view(self):
        from traitsui.api import Item, View

        class SimpleWithView(HasStrictTraits):

            value_range = ValidatedTuple(
                Int(0), Int(1), validation=lambda x: x[0] < x[1])

            view = View(
                Item('value_range', editor=self.tuple_editor())
            )

        dummy_model = SimpleWithView()
        with dispose_ui(dummy_model.edit_traits) as ui:
            editor = get_traitsui_editor(ui, 'value_range')
            self.assertIsInstance(editor.factory, self.tuple_editor)
            self.assertEqual(editor.value, (0, 1))
            self.assertEqual(
                editor._ts.trait_get(['f0', 'f1', 'invalid0', 'invalid1']),
                {'f0': 0, 'f1': 1, 'invalid0': False, 'invalid1': False})

            fields_ui = editor._ui
            f0_editor = get_traitsui_editor(fields_ui, 'f0')
            f1_editor = get_traitsui_editor(fields_ui, 'f1')

            f1_editor.value = -4  # 0 < -4 -> invalid
            self.assertFalse(f0_editor.invalid)
            self.assertTrue(f1_editor.invalid)
            self.assertEqual(editor.value, (0, 1))

    def test_invalid_state_reset_on_model_change(self):
        dummy_model = DummyModel()
        with dispose_ui(dummy_model.edit_traits) as ui:
            editor = get_traitsui_editor(ui, 'value_range')
            fields_ui = editor._ui
            f0_editor = get_traitsui_editor(fields_ui, 'f0')
            f1_editor = get_traitsui_editor(fields_ui, 'f1')

            # given
            f1_editor.value = -4  # 0 < -4 -> invalid
            self.assertFalse(f0_editor.invalid)
            self.assertTrue(f1_editor.invalid)
            self.assertEqual(editor.value, (0, 1))

            # when
            dummy_model.value_range = (2, 7)

            # then
            self.assertEqual(
                editor._ts.trait_get(['f0', 'f1', 'invalid0', 'invalid1']),
                {'f0': 2, 'f1': 7, 'invalid0': False, 'invalid1': False})
