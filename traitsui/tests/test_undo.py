# (C) Copyright 2004-2023 Enthought, Inc., Austin, TX
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
from warnings import catch_warnings

from pyface.toolkit import toolkit_object
from pyface.undo.api import AbstractCommand
from traits.api import Any, HasTraits, Int, List, Str, Tuple
from traits.testing.api import UnittestTools

from traitsui.tests.test_editor import create_editor
from traitsui.undo import AbstractUndoItem, ListUndoItem, UndoHistory, UndoItem
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

    list_value = List()

    any_value = Any()


class DummyCommand(AbstractCommand):
    def do(self):
        self.data = "do"

    def undo(self):
        self.data = "undo"

    def redo(self):
        self.data = "redo"


class LegacyUndoItem(AbstractUndoItem):
    def undo(self):
        pass

    def redo(self):
        pass


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


class TestListUndoItem(UnittestTools, unittest.TestCase):
    def test_undo(self):
        example = SimpleExample(list_value=['foo', 'wombat', 'baz'])

        undo_item = ListUndoItem(
            object=example,
            name='list_value',
            index=1,
            added=['wombat', 'baz'],
            removed=['bar'],
        )

        with self.assertTraitChanges(example, 'list_value_items', count=1):
            undo_item.undo()

        self.assertEqual(example.list_value, ['foo', 'bar'])

    def test_redo(self):
        example = SimpleExample(list_value=['foo', 'bar'])

        undo_item = ListUndoItem(
            object=example,
            name='list_value',
            index=1,
            added=['wombat', 'baz'],
            removed=['bar'],
        )

        with self.assertTraitChanges(example, 'list_value_items', count=1):
            undo_item.redo()

        self.assertEqual(example.list_value, ['foo', 'wombat', 'baz'])

    def test_merge_identical(self):
        example = SimpleExample(list_value=['foo', 'wombat', 'baz'])
        added = [['wombat'], 'baz']
        removed = [['bar']]

        undo_item = ListUndoItem(
            object=example,
            name='list_value',
            index=1,
            added=added.copy(),
            removed=removed.copy(),
        )
        next_undo_item = ListUndoItem(
            object=example,
            name='list_value',
            index=1,
            added=added.copy(),
            removed=removed.copy(),
        )

        result = undo_item.merge(next_undo_item)

        self.assertTrue(result)

    def test_merge_equal(self):
        example = SimpleExample(list_value=['foo', 'wombat', 'baz'])
        removed = [['bar']]

        undo_item = ListUndoItem(
            object=example,
            name='list_value',
            index=1,
            added=[['wombat'], 'baz'],
            removed=removed.copy(),
        )
        next_undo_item = ListUndoItem(
            object=example,
            name='list_value',
            index=1,
            added=[['wombat'], 'baz'],
            removed=removed.copy(),
        )

        result = undo_item.merge(next_undo_item)

        self.assertFalse(result)

    def test_merge_equal_removed(self):
        example = SimpleExample(list_value=['foo', 'wombat', 'baz'])
        added = [['wombat'], 'baz']

        undo_item = ListUndoItem(
            object=example,
            name='list_value',
            index=1,
            added=added.copy(),
            removed=[['bar']],
        )
        next_undo_item = ListUndoItem(
            object=example,
            name='list_value',
            index=1,
            added=added.copy(),
            removed=[['bar']],
        )

        result = undo_item.merge(next_undo_item)

        self.assertFalse(result)

    def test_merge_different_objects(self):
        example_1 = SimpleExample()
        example_2 = SimpleExample()
        added = [['wombat'], 'baz']
        removed = [['bar']]

        undo_item = ListUndoItem(
            object=example_1,
            name='list_value',
            index=1,
            added=added.copy(),
            removed=removed.copy(),
        )
        next_undo_item = ListUndoItem(
            object=example_2,
            name='list_value',
            index=1,
            added=added.copy(),
            removed=removed.copy(),
        )

        result = undo_item.merge(next_undo_item)

        self.assertFalse(result)

    def test_merge_different_traits(self):
        example = SimpleExample()
        added = [['wombat'], 'baz']
        removed = [['bar']]

        undo_item = ListUndoItem(
            object=example,
            name='list_value',
            index=1,
            added=added.copy(),
            removed=removed.copy(),
        )
        next_undo_item = ListUndoItem(
            object=example,
            name='any_value',
            index=1,
            added=added.copy(),
            removed=removed.copy(),
        )

        result = undo_item.merge(next_undo_item)

        self.assertFalse(result)

    def test_merge_different_index(self):
        example = SimpleExample()
        added = [['wombat'], 'baz']
        removed = [['bar']]

        undo_item = ListUndoItem(
            object=example,
            name='list_value',
            index=1,
            added=added.copy(),
            removed=removed.copy(),
        )
        next_undo_item = ListUndoItem(
            object=example,
            name='any_value',
            index=0,
            added=added.copy(),
            removed=removed.copy(),
        )

        result = undo_item.merge(next_undo_item)

        self.assertFalse(result)


class TestUndoHistory(UnittestTools, unittest.TestCase):
    def _populate_history(self, history):
        """Add some simple hostory items."""
        self._example = SimpleExample()
        history.add(
            UndoItem(
                object=self._example,
                name='str_value',
                old_value='foo',
                new_value='bar',
            )
        )
        history.add(
            UndoItem(
                object=self._example,
                name='str_value',
                old_value='bar',
                new_value='wombat',
            ),
        )
        history.add(
            UndoItem(
                object=self._example,
                name='str_value',
                old_value='wombat',
                new_value='baz',
            ),
        )

    def test_defaults(self):
        history = UndoHistory()

        self.assertEqual(history.now, 0)
        self.assertFalse(history.can_undo)
        self.assertFalse(history.can_redo)

    def test_add_empty(self):
        history = UndoHistory()
        example = SimpleExample(str_value='foo')

        undo_item = UndoItem(
            object=example,
            name='str_value',
            old_value='foo',
            new_value='bar',
        )

        with self.assertTraitChanges(history, 'undoable', count=1):
            with self.assertTraitDoesNotChange(history, 'redoable'):
                history.add(undo_item)

        self.assertEqual(history.now, 1)
        self.assertTrue(history.can_undo)
        self.assertFalse(history.can_redo)

    def test_add_end(self):
        history = UndoHistory()
        example = SimpleExample(str_value='foo', value=10)
        undo_item = UndoItem(
            object=example,
            name='value',
            old_value=0,
            new_value=10,
        )

        history.add(
            UndoItem(
                object=example,
                name='str_value',
                old_value='foo',
                new_value='bar',
            )
        )

        with self.assertTraitDoesNotChange(history, 'undoable'):
            with self.assertTraitDoesNotChange(history, 'redoable'):
                history.add(undo_item)

        self.assertEqual(history.now, 2)
        self.assertTrue(history.can_undo)
        self.assertFalse(history.can_redo)

    def test_add_merge(self):
        history = UndoHistory()
        example = SimpleExample(str_value='foo', value=10)
        undo_item = UndoItem(
            object=example,
            name='str_value',
            old_value='foo',
            new_value='baz',
        )

        history.add(
            UndoItem(
                object=example,
                name='str_value',
                old_value='foo',
                new_value='bar',
            )
        )

        with self.assertTraitDoesNotChange(history, 'undoable'):
            with self.assertTraitDoesNotChange(history, 'redoable'):
                history.add(undo_item)

        self.assertEqual(history.now, 1)
        self.assertTrue(history.can_undo)
        self.assertFalse(history.can_redo)

    def test_add_end_extend(self):
        history = UndoHistory()
        example = SimpleExample(str_value='foo', value=10)
        undo_item = UndoItem(
            object=example,
            name='value',
            old_value=0,
            new_value=10,
        )

        history.add(
            UndoItem(
                object=example,
                name='str_value',
                old_value='foo',
                new_value='bar',
            )
        )

        with self.assertTraitDoesNotChange(history, 'undoable'):
            with self.assertTraitDoesNotChange(history, 'redoable'):
                history.add(undo_item, extend=True)

        self.assertEqual(history.now, 1)
        self.assertTrue(history.can_undo)
        self.assertFalse(history.can_redo)

    def test_add_end_extend_merge(self):
        history = UndoHistory()
        example = SimpleExample(str_value='foo', value=10)
        undo_item = UndoItem(
            object=example,
            name='str_value',
            old_value='foo',
            new_value='baz',
        )

        history.add(
            UndoItem(
                object=example,
                name='str_value',
                old_value='foo',
                new_value='bar',
            )
        )

        with self.assertTraitDoesNotChange(history, 'undoable'):
            with self.assertTraitDoesNotChange(history, 'redoable'):
                history.add(undo_item, extend=True)

        self.assertEqual(history.now, 1)
        self.assertTrue(history.can_undo)
        self.assertFalse(history.can_redo)
        # XXX this is testing private state to ensure merge happened
        self.assertEqual(len(history.stack._stack), 1)

    def test_add_middle(self):
        history = UndoHistory()
        example = SimpleExample(str_value='foo', value=10)
        undo_item = UndoItem(
            object=example,
            name='value',
            old_value=0,
            new_value=10,
        )

        history.add(
            UndoItem(
                object=example,
                name='str_value',
                old_value='foo',
                new_value='bar',
            )
        )
        history.add(
            UndoItem(
                object=example,
                name='str_value',
                old_value='bar',
                new_value='wombat',
            ),
        )
        history.undo()

        with self.assertTraitDoesNotChange(history, 'undoable'):
            with self.assertTraitChanges(history, 'redoable', count=1):
                history.add(undo_item)

        self.assertEqual(history.now, 2)
        self.assertTrue(history.can_undo)
        self.assertFalse(history.can_redo)

    def test_add_middle_mergeable(self):
        history = UndoHistory()
        example = SimpleExample(str_value='foo', value=10)
        undo_item = UndoItem(
            object=example,
            name='str_value',
            old_value='bar',
            new_value='baz',
        )

        history.add(
            UndoItem(
                object=example,
                name='str_value',
                old_value='foo',
                new_value='bar',
            )
        )
        history.add(
            UndoItem(
                object=example,
                name='str_value',
                old_value='bar',
                new_value='wombat',
            ),
        )
        history.undo()

        with self.assertTraitDoesNotChange(history, 'undoable'):
            with self.assertTraitChanges(history, 'redoable', count=1):
                history.add(undo_item)

        self.assertEqual(history.now, 1)
        self.assertTrue(history.can_undo)
        self.assertFalse(history.can_redo)

    def test_undo_last(self):
        history = UndoHistory()
        self._populate_history(history)

        with self.assertTraitDoesNotChange(history, 'undoable'):
            with self.assertTraitChanges(history, 'redoable', count=1):
                with self.assertTraitChanges(
                    self._example, 'anytrait', count=1
                ):  # noqa: E501
                    history.undo()

        self.assertEqual(history.now, 2)
        self.assertTrue(history.can_undo)
        self.assertTrue(history.can_redo)

    def test_undo_first(self):
        history = UndoHistory()
        self._populate_history(history)
        history.undo()
        history.undo()

        with self.assertTraitDoesNotChange(history, 'redoable'):
            with self.assertTraitChanges(history, 'undoable', count=1):
                with self.assertTraitChanges(
                    self._example, 'anytrait', count=1
                ):  # noqa: E501
                    history.undo()

        self.assertEqual(history.now, 0)
        self.assertFalse(history.can_undo)
        self.assertTrue(history.can_redo)

    def test_undo_middle(self):
        history = UndoHistory()
        self._populate_history(history)
        history.undo()

        with self.assertTraitDoesNotChange(history, 'redoable'):
            with self.assertTraitDoesNotChange(history, 'undoable'):
                with self.assertTraitChanges(
                    self._example, 'anytrait', count=1
                ):  # noqa: E501
                    history.undo()

        self.assertEqual(history.now, 1)
        self.assertTrue(history.can_undo)
        self.assertTrue(history.can_redo)

    def test_redo_last(self):
        history = UndoHistory()
        self._populate_history(history)
        history.undo()

        with self.assertTraitChanges(history, 'redoable', count=1):
            with self.assertTraitDoesNotChange(history, 'undoable'):
                with self.assertTraitChanges(
                    self._example, 'anytrait', count=1
                ):  # noqa: E501
                    history.redo()

        self.assertEqual(history.now, 3)
        self.assertTrue(history.can_undo)
        self.assertFalse(history.can_redo)

    def test_redo_middle(self):
        history = UndoHistory()
        self._populate_history(history)
        history.undo()
        history.undo()

        with self.assertTraitDoesNotChange(history, 'redoable'):
            with self.assertTraitDoesNotChange(history, 'undoable'):
                with self.assertTraitChanges(
                    self._example, 'anytrait', count=1
                ):  # noqa: E501
                    history.redo()

        self.assertEqual(history.now, 2)
        self.assertTrue(history.can_undo)
        self.assertTrue(history.can_redo)

    def test_redo_first(self):
        history = UndoHistory()
        self._populate_history(history)
        history.undo()
        history.undo()
        history.undo()

        with self.assertTraitDoesNotChange(history, 'redoable'):
            with self.assertTraitChanges(history, 'undoable', count=1):
                with self.assertTraitChanges(
                    self._example, 'anytrait', count=1
                ):  # noqa: E501
                    history.redo()

        self.assertEqual(history.now, 1)
        self.assertTrue(history.can_undo)
        self.assertTrue(history.can_redo)

    def test_revert_end(self):
        history = UndoHistory()
        self._populate_history(history)

        with self.assertTraitChanges(history, 'redoable', count=2):
            with self.assertTraitChanges(history, 'undoable', count=1):
                with self.assertTraitChanges(
                    self._example, 'anytrait', count=3
                ):  # noqa: E501
                    history.revert()

        self.assertEqual(history.now, 0)
        self.assertFalse(history.can_undo)
        self.assertFalse(history.can_redo)

    def test_revert_middle(self):
        history = UndoHistory()
        self._populate_history(history)
        history.undo()
        history.undo()

        with self.assertTraitChanges(history, 'redoable', count=1):
            with self.assertTraitChanges(history, 'undoable', count=1):
                with self.assertTraitChanges(
                    self._example, 'anytrait', count=1
                ):  # noqa: E501
                    history.revert()

        self.assertEqual(history.now, 0)
        self.assertFalse(history.can_undo)
        self.assertFalse(history.can_redo)

    def test_revert_start(self):
        history = UndoHistory()
        self._populate_history(history)
        history.undo()
        history.undo()
        history.undo()

        with self.assertTraitDoesNotChange(history, 'undoable'):
            with self.assertTraitChanges(history, 'redoable', count=1):
                with self.assertTraitDoesNotChange(self._example, 'anytrait'):
                    history.revert()

        self.assertEqual(history.now, 0)
        self.assertFalse(history.can_undo)
        self.assertFalse(history.can_redo)

    def test_clear_end(self):
        history = UndoHistory()
        self._populate_history(history)

        with self.assertTraitDoesNotChange(history, 'redoable'):
            with self.assertTraitChanges(history, 'undoable', count=1):
                with self.assertTraitDoesNotChange(self._example, 'anytrait'):
                    history.clear()

        self.assertEqual(history.now, 0)
        self.assertFalse(history.can_undo)
        self.assertFalse(history.can_redo)

    def test_clear_middle(self):
        history = UndoHistory()
        self._populate_history(history)
        history.undo()
        history.undo()

        with self.assertTraitChanges(history, 'redoable', count=1):
            with self.assertTraitChanges(history, 'undoable', count=1):
                with self.assertTraitDoesNotChange(self._example, 'anytrait'):
                    history.clear()

        self.assertEqual(history.now, 0)
        self.assertFalse(history.can_undo)
        self.assertFalse(history.can_redo)

    def test_clear_start(self):
        history = UndoHistory()
        self._populate_history(history)
        history.undo()
        history.undo()
        history.undo()

        with self.assertTraitDoesNotChange(history, 'undoable'):
            with self.assertTraitChanges(history, 'redoable', count=1):
                with self.assertTraitDoesNotChange(self._example, 'anytrait'):
                    history.clear()

        self.assertEqual(history.now, 0)
        self.assertFalse(history.can_undo)
        self.assertFalse(history.can_redo)

    def test_extend(self):
        history = UndoHistory()
        example = SimpleExample(str_value='foo', value=10)
        undo_item = UndoItem(
            object=example,
            name='value',
            old_value=0,
            new_value=10,
        )

        history.add(
            UndoItem(
                object=example,
                name='str_value',
                old_value='foo',
                new_value='bar',
            )
        )

        with self.assertTraitDoesNotChange(history, 'undoable'):
            with self.assertTraitDoesNotChange(history, 'redoable'):
                history.extend(undo_item)

        self.assertEqual(history.now, 1)
        self.assertTrue(history.can_undo)
        self.assertFalse(history.can_redo)

    def test_extend_merge(self):
        history = UndoHistory()
        example = SimpleExample(str_value='foo', value=10)
        undo_item = UndoItem(
            object=example,
            name='str_value',
            old_value='foo',
            new_value='baz',
        )

        history.add(
            UndoItem(
                object=example,
                name='str_value',
                old_value='foo',
                new_value='bar',
            )
        )

        with self.assertTraitDoesNotChange(history, 'undoable'):
            with self.assertTraitDoesNotChange(history, 'redoable'):
                history.extend(undo_item)

        self.assertEqual(history.now, 1)
        self.assertTrue(history.can_undo)
        self.assertFalse(history.can_redo)
        # XXX this is testing private state to ensure merge happened
        self.assertEqual(len(history.stack._stack), 1)

    def test_general_command_do(self):
        history = UndoHistory()
        command = DummyCommand()

        history.add(command)

        self.assertEqual(command.data, "do")


@unittest.skipIf(no_gui_test_assistant, "No GuiTestAssistant")
class TestEditorUndo(BaseTestMixin, GuiTestAssistant, unittest.TestCase):
    def setUp(self):
        BaseTestMixin.setUp(self)
        GuiTestAssistant.setUp(self)

    def tearDown(self):
        GuiTestAssistant.tearDown(self)
        BaseTestMixin.tearDown(self)

    def check_history(
        self, editor, expected_history_now, expected_history_length
    ):
        # XXX this is testing private state
        return (
            editor.ui.history.now == expected_history_now
            and len(editor.ui.history.stack._stack) == expected_history_length
        )

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
        self.assertEventuallyTrue(
            editor,
            "ui",
            functools.partial(
                self.check_history,
                expected_history_now=1,
                expected_history_length=2,
            ),
            timeout=5.0,
        )

        # Perform a REDO
        self.redo(editor)

        # Expect 2 items in history and pointer at second item
        self.assertEventuallyTrue(
            editor,
            "ui",
            functools.partial(
                self.check_history,
                expected_history_now=2,
                expected_history_length=2,
            ),
            timeout=5.0,
        )

        # Enter 'three'
        with editor.updating_value():
            self.gui.set_trait_later(editor.control, "control_value", "three")

        # Perform an UNDO
        self.undo(editor)

        # Expect 3 items in history and pointer at second item
        self.assertEventuallyTrue(
            editor,
            "ui",
            functools.partial(
                self.check_history,
                expected_history_now=2,
                expected_history_length=3,
            ),
            timeout=5.0,
        )

        # Enter 'four'
        with editor.updating_value():
            self.gui.set_trait_later(editor.control, "control_value", "four")
        self.event_loop_helper.event_loop_with_timeout()

        # Expect 3 items in history and pointer at second item
        # Note: Modifying the history after an UNDO, clears the future,
        # hence, we expect 3 items in the history, not 4
        self.assertEventuallyTrue(
            editor,
            "ui",
            functools.partial(
                self.check_history,
                expected_history_now=3,
                expected_history_length=3,
            ),
            timeout=5.0,
        )

        # The following sequence after modifying the history had caused
        # the application to hang, verify it.

        # Perform an UNDO
        self.undo(editor)
        self.undo(editor)
        self.redo(editor)

        # Expect 3 items in history and pointer at second item
        self.assertEventuallyTrue(
            editor,
            "ui",
            functools.partial(
                self.check_history,
                expected_history_now=2,
                expected_history_length=3,
            ),
            timeout=5.0,
        )
