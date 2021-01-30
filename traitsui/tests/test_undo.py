# (C) Copyright 2004-2021 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

import functools
import unittest

from pyface.toolkit import toolkit_object
from traits.api import Any, HasTraits, Int, Str, Tuple
from traits.testing.api import UnittestTools

from traitsui.tests.test_editor import create_editor
from traitsui.undo import ListUndoItem, UndoHistory, UndoItem
from traitsui.tests._tools import BaseTestMixin

GuiTestAssistant = toolkit_object("util.gui_test_assistant:GuiTestAssistant")
no_gui_test_assistant = GuiTestAssistant.__name__ == "Unimplemented"
if no_gui_test_assistant:
    # ensure null toolkit has an inheritable GuiTestAssistant
    class GuiTestAssistant(object):
        pass


class SimpleExample(HasTraits):

    value = Int()

    str_value = Str()

    tuple_value = Tuple()

    any_value = Any()


class TestUndoItem(UnittestTools, unittest.TestCase):

    def test_undo(self):
        example = SimpleExample(value=11)

        undo_item = UndoItem(
            object=example,
            name='value',
            old_value=10,
            new_value=11,
        )

        with self.assertTraitChanges(example, 'value', count=1):
            undo_item.undo()

        self.assertEqual(example.value, 10)

    def test_redo(self):
        example = SimpleExample(value=10)

        undo_item = UndoItem(
            object=example,
            name='value',
            old_value=10,
            new_value=11,
        )

        with self.assertTraitChanges(example, 'value', count=1):
            undo_item.redo()

        self.assertEqual(example.value, 11)

    def test_merge_different_undo_item_type(self):
        example_1 = SimpleExample()
        example_2 = SimpleExample()

        undo_item = UndoItem(
            object=example_1,
            name='any_value',
        )
        next_undo_item = ListUndoItem(
            object=example_2,
            name='any_value',
        )

        result = undo_item.merge(next_undo_item)

        self.assertFalse(result)

    def test_merge_different_objects(self):
        example_1 = SimpleExample()
        example_2 = SimpleExample()

        undo_item = UndoItem(
            object=example_1,
            name='value',
            old_value=10,
            new_value=11,
        )
        next_undo_item = UndoItem(
            object=example_2,
            name='value',
            old_value=10,
            new_value=11,
        )

        result = undo_item.merge(next_undo_item)

        self.assertFalse(result)

    def test_merge_different_traits(self):
        example = SimpleExample()

        undo_item = UndoItem(
            object=example,
            name='value',
            old_value=10,
            new_value=11,
        )
        next_undo_item = UndoItem(
            object=example,
            name='str_value',
            old_value='foo',
            new_value='bar',
        )

        result = undo_item.merge(next_undo_item)

        self.assertFalse(result)

    def test_merge_different_value_types(self):
        example = SimpleExample()

        undo_item = UndoItem(
            object=example,
            name='any_value',
            old_value=10,
            new_value=11,
        )
        next_undo_item = UndoItem(
            object=example,
            name='any_value',
            old_value=11,
            new_value='foo',
        )

        result = undo_item.merge(next_undo_item)

        self.assertFalse(result)

    def test_merge_numbers(self):
        example = SimpleExample()

        undo_item = UndoItem(
            object=example,
            name='value',
            old_value=10,
            new_value=11,
        )
        next_undo_item = UndoItem(
            object=example,
            name='value',
            old_value=11,
            new_value=12,
        )

        result = undo_item.merge(next_undo_item)

        self.assertTrue(result)
        self.assertEqual(undo_item.old_value, 10)
        self.assertEqual(undo_item.new_value, 12)

    def test_merge_str_insert(self):
        example = SimpleExample()

        undo_item = UndoItem(
            object=example,
            name='str_value',
            old_value='foo',
            new_value='bar',
        )
        next_undo_item = UndoItem(
            object=example,
            name='str_value',
            old_value='bar',
            new_value='bear',
        )

        result = undo_item.merge(next_undo_item)

        self.assertTrue(result)
        self.assertEqual(undo_item.old_value, 'foo')
        self.assertEqual(undo_item.new_value, 'bear')

    def test_merge_str_delete(self):
        example = SimpleExample()

        undo_item = UndoItem(
            object=example,
            name='str_value',
            old_value='foo',
            new_value='bear',
        )
        next_undo_item = UndoItem(
            object=example,
            name='str_value',
            old_value='bear',
            new_value='bar',
        )

        result = undo_item.merge(next_undo_item)

        self.assertTrue(result)
        self.assertEqual(undo_item.old_value, 'foo')
        self.assertEqual(undo_item.new_value, 'bar')

    def test_merge_str_change(self):
        example = SimpleExample()

        undo_item = UndoItem(
            object=example,
            name='str_value',
            old_value='foo',
            new_value='bar',
        )
        next_undo_item = UndoItem(
            object=example,
            name='str_value',
            old_value='bar',
            new_value='baz',
        )

        result = undo_item.merge(next_undo_item)

        self.assertTrue(result)
        self.assertEqual(undo_item.old_value, 'foo')
        self.assertEqual(undo_item.new_value, 'baz')

    def test_merge_str_same(self):
        example = SimpleExample()

        undo_item = UndoItem(
            object=example,
            name='str_value',
            old_value='foo',
            new_value='bar',
        )
        next_undo_item = UndoItem(
            object=example,
            name='str_value',
            old_value='bar',
            new_value='bar',
        )

        result = undo_item.merge(next_undo_item)

        self.assertTrue(result)
        self.assertEqual(undo_item.old_value, 'foo')
        self.assertEqual(undo_item.new_value, 'bar')

    def test_merge_str_different(self):
        example = SimpleExample()

        undo_item = UndoItem(
            object=example,
            name='str_value',
            old_value='foo',
            new_value='bar',
        )
        next_undo_item = UndoItem(
            object=example,
            name='str_value',
            old_value='bar',
            new_value='wombat',
        )

        result = undo_item.merge(next_undo_item)

        self.assertFalse(result)

    def test_merge_sequence_change(self):
        example = SimpleExample()

        undo_item = UndoItem(
            object=example,
            name='tuple_value',
            old_value=('foo', 'bar', 'baz'),
            new_value=('foo', 'wombat', 'baz'),
        )
        next_undo_item = UndoItem(
            object=example,
            name='tuple_value',
            old_value=('foo', 'wombat', 'baz'),
            new_value=('foo', 'fizz', 'baz'),
        )

        result = undo_item.merge(next_undo_item)

        self.assertTrue(result)
        self.assertEqual(undo_item.old_value, ('foo', 'bar', 'baz'))
        self.assertEqual(undo_item.new_value, ('foo', 'fizz', 'baz'))

    def test_merge_sequence_change_different_types(self):
        example = SimpleExample()

        undo_item = UndoItem(
            object=example,
            name='tuple_value',
            old_value=('foo', 'bar', 'baz'),
            new_value=('foo', 'wombat', 'baz'),
        )
        next_undo_item = UndoItem(
            object=example,
            name='tuple_value',
            old_value=('foo', 'wombat', 'baz'),
            new_value=('foo', 12, 'baz'),
        )

        result = undo_item.merge(next_undo_item)

        self.assertTrue(result)
        self.assertEqual(undo_item.old_value, ('foo', 'bar', 'baz'))
        self.assertEqual(undo_item.new_value, ('foo', 12, 'baz'))

    def test_merge_sequence_change_not_simple_types(self):
        example = SimpleExample()

        undo_item = UndoItem(
            object=example,
            name='tuple_value',
            old_value=('foo', ['bar'], 'baz'),
            new_value=('foo', ['wombat'], 'baz'),
        )
        next_undo_item = UndoItem(
            object=example,
            name='tuple_value',
            old_value=('foo', ['wombat'], 'baz'),
            new_value=('foo', ['fizz'], 'baz'),
        )

        result = undo_item.merge(next_undo_item)

        self.assertTrue(result)
        self.assertEqual(undo_item.old_value, ('foo', ['bar'], 'baz'))
        self.assertEqual(undo_item.new_value, ('foo', ['fizz'], 'baz'))

    def test_merge_sequence_change_multiple_not_simple_types(self):
        example = SimpleExample()

        undo_item = UndoItem(
            object=example,
            name='tuple_value',
            old_value=(['foo'], 'bar', 'baz'),
            new_value=(['foo'], 'wombat', 'baz'),
        )
        next_undo_item = UndoItem(
            object=example,
            name='tuple_value',
            old_value=(['foo'], 'wombat', 'baz'),
            new_value=(['foo'], 'fizz', 'baz'),
        )

        result = undo_item.merge(next_undo_item)

        # XXX This is perhaps unexpected. See GitHub issue #1507.
        self.assertFalse(result)

    def test_merge_sequence_change_back(self):
        example = SimpleExample()

        undo_item = UndoItem(
            object=example,
            name='tuple_value',
            old_value=('foo', 'bar', 'baz'),
            new_value=('foo', 'wombat', 'baz'),
        )
        next_undo_item = UndoItem(
            object=example,
            name='tuple_value',
            old_value=('foo', 'wombat', 'baz'),
            new_value=('foo', 'bar', 'baz'),
        )

        result = undo_item.merge(next_undo_item)

        self.assertFalse(result)

    def test_merge_sequence_two_changes(self):
        example = SimpleExample()

        undo_item = UndoItem(
            object=example,
            name='tuple_value',
            old_value=('foo', 'bar', 'baz'),
            new_value=('foo', 'wombat', 'baz'),
        )
        next_undo_item = UndoItem(
            object=example,
            name='tuple_value',
            old_value=('foo', 'wombat', 'baz'),
            new_value=('foo', 'wombat', 'fizz'),
        )

        result = undo_item.merge(next_undo_item)

        self.assertFalse(result)

    def test_merge_sequence_change_length(self):
        example = SimpleExample()

        undo_item = UndoItem(
            object=example,
            name='tuple_value',
            old_value=('foo', 'bar', 'baz'),
            new_value=('foo', 'wombat', 'baz'),
        )
        next_undo_item = UndoItem(
            object=example,
            name='tuple_value',
            old_value=('foo', 'wombat', 'baz'),
            new_value=('foo', 'wombat', 'baz', 'fizz'),
        )

        result = undo_item.merge(next_undo_item)

        self.assertFalse(result)

    def test_merge_unhandled_type(self):
        example = SimpleExample()

        undo_item = UndoItem(
            object=example,
            name='any_value',
            old_value={'foo', 'bar', 'baz'},
            new_value={'foo', 'wombat', 'baz'},
        )
        next_undo_item = UndoItem(
            object=example,
            name='any_value',
            old_value={'foo', 'wombat', 'baz'},
            new_value={'foo', 'fizz', 'baz'},
        )

        result = undo_item.merge(next_undo_item)

        self.assertFalse(result)


@unittest.skipIf(no_gui_test_assistant, "No GuiTestAssistant")
class TestEditorUndo(BaseTestMixin, GuiTestAssistant, unittest.TestCase):

    def setUp(self):
        BaseTestMixin.setUp(self)
        GuiTestAssistant.setUp(self)

    def tearDown(self):
        GuiTestAssistant.tearDown(self)
        BaseTestMixin.tearDown(self)

    def check_history(self, editor, expected_history_now,
                      expected_history_length):
        if (editor.ui.history.now == expected_history_now and
                len(editor.ui.history.history) == expected_history_length):

            # Ensure that there is exactly 1 entry in each history item since
            # no entries can be merged in this test.
            for itm in editor.ui.history.history:
                if len(itm) != 1:
                    return False

            return True

    def undo(self, editor):
        self.gui.invoke_later(editor.ui.history.undo)
        self.event_loop_helper.event_loop_with_timeout()

    def redo(self, editor):
        self.gui.invoke_later(editor.ui.history.redo)
        self.event_loop_helper.event_loop_with_timeout()

    def test_undo(self):
        editor = create_editor()
        editor.prepare(None)
        editor.ui.history = UndoHistory()

        self.assertEqual(editor.old_value, "test")

        # Enter 'one' followed by 'two'
        with editor.updating_value():
            self.gui.set_trait_later(editor.control, "control_value", "one")
            self.gui.set_trait_later(editor.control, "control_value", "two")

        # Perform an UNDO
        self.undo(editor)

        # Expect 2 items in history and pointer at first item
        self.assertEventuallyTrue(editor, "ui",
                                  functools.partial(self.check_history,
                                                    expected_history_now=1,
                                                    expected_history_length=2),
                                  timeout=5.0)

        # Perform a REDO
        self.redo(editor)

        # Expect 2 items in history and pointer at second item
        self.assertEventuallyTrue(editor, "ui",
                                  functools.partial(self.check_history,
                                                    expected_history_now=2,
                                                    expected_history_length=2),
                                  timeout=5.0)

        # Enter 'three'
        with editor.updating_value():
            self.gui.set_trait_later(editor.control, "control_value", "three")

        # Perform an UNDO
        self.undo(editor)

        # Expect 3 items in history and pointer at second item
        self.assertEventuallyTrue(editor, "ui",
                                  functools.partial(self.check_history,
                                                    expected_history_now=2,
                                                    expected_history_length=3),
                                  timeout=5.0)

        # Enter 'four'
        with editor.updating_value():
            self.gui.set_trait_later(editor.control, "control_value", "four")
        self.event_loop_helper.event_loop_with_timeout()

        # Expect 3 items in history and pointer at second item
        # Note: Modifying the history after an UNDO, clears the future,
        # hence, we expect 3 items in the history, not 4
        self.assertEventuallyTrue(editor, "ui",
                                  functools.partial(self.check_history,
                                                    expected_history_now=3,
                                                    expected_history_length=3),
                                  timeout=5.0)

        # The following sequence after modifying the history had caused
        # the application to hang, verify it.

        # Perform an UNDO
        self.undo(editor)
        self.undo(editor)
        self.redo(editor)

        # Expect 3 items in history and pointer at second item
        self.assertEventuallyTrue(editor, "ui",
                                  functools.partial(self.check_history,
                                                    expected_history_now=2,
                                                    expected_history_length=3),
                                  timeout=5.0)
