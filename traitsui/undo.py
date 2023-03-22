# (C) Copyright 2004-2023 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

""" Defines the manager for Undo and Redo history for Traits user interface
    support.
"""

import collections.abc

from traits.api import (
    Bool,
    Event,
    HasPrivateTraits,
    HasStrictTraits,
    HasTraits,
    Instance,
    Int,
    List,
    Property,
    Str,
    Trait,
    cached_property,
    observe,
)
from pyface.undo.api import (
    AbstractCommand,
    CommandStack,
    ICommand,
    ICommandStack,
    IUndoManager,
    UndoManager,
)


NumericTypes = (int, float, complex)
SimpleTypes = (str, bytes) + NumericTypes


class AbstractUndoItem(AbstractCommand):
    """Abstract base class for undo items.

    This class is deprecated and will be removed in TraitsUI 8.  Any custom
    subclasses of this class should either subclass from AbstractCommand, or
    provide the ICommand interface.
    """

    #: A simple default name.
    name = "Edit"

    def do(self):
        """Does nothing.

        All undo items log events after they have happened, so by default
        they do not do anything when added to the history.
        """
        pass

    def undo(self):
        """Undoes the change."""
        raise NotImplementedError

    def redo(self):
        """Re-does the change."""
        raise NotImplementedError

    def merge(self, other):
        """Merges two undo items if possible."""
        return False


class UndoItem(AbstractUndoItem):
    """A change to an object trait, which can be undone."""

    # -------------------------------------------------------------------------
    #  Trait definitions:
    # -------------------------------------------------------------------------

    #: Object the change occurred on
    object = Instance(HasTraits)

    #: Name of the trait that changed
    name = Str()

    #: Old value of the changed trait
    old_value = Property()

    #: New value of the changed trait
    new_value = Property()

    def _get_old_value(self):
        return self._old_value

    def _set_old_value(self, value):
        if isinstance(value, list):
            value = value[:]
        self._old_value = value

    def _get_new_value(self):
        return self._new_value

    def _set_new_value(self, value):
        if isinstance(value, list):
            value = value[:]
        self._new_value = value

    def undo(self):
        """Undoes the change."""
        try:
            setattr(self.object, self.name, self.old_value)
        except Exception:
            from traitsui.api import raise_to_debug

            raise_to_debug()

    def redo(self):
        """Re-does the change."""
        try:
            setattr(self.object, self.name, self.new_value)
        except Exception:
            from traitsui.api import raise_to_debug

            raise_to_debug()

    def merge(self, undo_item):
        """Merges two undo items if possible."""
        # Undo items are potentially mergeable only if they are of the same
        # class and refer to the same object trait, so check that first:
        if (
            isinstance(undo_item, self.__class__)
            and (self.object is undo_item.object)
            and (self.name == undo_item.name)
        ):
            v1 = self.new_value
            v2 = undo_item.new_value
            t1 = type(v1)
            if isinstance(v2, t1):

                if isinstance(v1, str):
                    # Merge two undo items if they have new values which are
                    # strings which only differ by one character (corresponding
                    # to a single character insertion, deletion or replacement
                    # operation in a text editor):
                    n1 = len(v1)
                    n2 = len(v2)
                    if abs(n1 - n2) > 1:
                        return False
                    n = min(n1, n2)
                    i = 0
                    while (i < n) and (v1[i] == v2[i]):
                        i += 1
                    if v1[i + (n2 <= n1) :] == v2[i + (n2 >= n1) :]:
                        self.new_value = v2
                        return True

                elif isinstance(v1, collections.abc.Sequence):
                    # Merge sequence types only if a single element has changed
                    # from the 'original' value, and the element type is a
                    # simple Python type:
                    v1 = self.old_value
                    if isinstance(v1, collections.abc.Sequence):
                        # Note: wxColour says it's a sequence type, but it
                        # doesn't support 'len', so we handle the exception
                        # just in case other classes have similar behavior:
                        try:
                            if len(v1) == len(v2):
                                diffs = 0
                                for i, item in enumerate(v1):
                                    titem = type(item)
                                    item2 = v2[i]
                                    if (
                                        (titem not in SimpleTypes)
                                        or (not isinstance(item2, titem))
                                        or (item != item2)
                                    ):
                                        diffs += 1
                                        if diffs >= 2:
                                            return False
                                if diffs == 0:
                                    return False
                                self.new_value = v2
                                return True
                        except Exception:
                            pass

                elif t1 in NumericTypes:
                    # Always merge simple numeric trait changes:
                    self.new_value = v2
                    return True
        return False

    def __repr__(self):
        """Returns a "pretty print" form of the object."""
        n = self.name
        cn = self.object.__class__.__name__
        return "undo( %s.%s = %s )\nredo( %s.%s = %s )" % (
            cn,
            n,
            self.old_value,
            cn,
            n,
            self.new_value,
        )


class ListUndoItem(AbstractUndoItem):
    """A change to a list, which can be undone."""

    # -------------------------------------------------------------------------
    #  Trait definitions:
    # -------------------------------------------------------------------------

    #: Object that the change occurred on
    object = Instance(HasTraits)

    #: Name of the trait that changed
    name = Str()

    #: Starting index
    index = Int()

    #: Items added to the list
    added = List()

    #: Items removed from the list
    removed = List()

    def undo(self):
        """Undoes the change."""
        try:
            list = getattr(self.object, self.name)
            list[self.index : (self.index + len(self.added))] = self.removed
        except Exception:
            from traitsui.api import raise_to_debug

            raise_to_debug()

    def redo(self):
        """Re-does the change."""
        try:
            list = getattr(self.object, self.name)
            list[self.index : (self.index + len(self.removed))] = self.added
        except Exception:
            from traitsui.api import raise_to_debug

            raise_to_debug()

    def merge(self, undo_item):
        """Merges two undo items if possible."""
        # Discard undo items that are identical to us. This is to eliminate
        # the same undo item being created by multiple listeners monitoring the
        # same list for changes:
        if (
            isinstance(undo_item, self.__class__)
            and (self.object is undo_item.object)
            and (self.name == undo_item.name)
            and (self.index == undo_item.index)
        ):
            added = undo_item.added
            removed = undo_item.removed
            if (len(self.added) == len(added)) and (
                len(self.removed) == len(removed)
            ):
                for i, item in enumerate(self.added):
                    if item is not added[i]:
                        break
                else:
                    for i, item in enumerate(self.removed):
                        if item is not removed[i]:
                            break
                    else:
                        return True
        return False

    def __repr__(self):
        """Returns a 'pretty print' form of the object."""
        return "undo( %s.%s[%d:%d] = %s )" % (
            self.object.__class__.__name__,
            self.name,
            self.index,
            self.index + len(self.removed),
            self.added,
        )


class _MultiUndoItem(AbstractCommand):
    """The _MultiUndoItem class is an internal command that unifies commands."""

    name = "Edit"

    #: The commands that make up this undo item.
    commands = List(Instance(ICommand))

    def push(self, command):
        """Append a command, merging if possible."""
        if len(self.commands) > 0:
            merged = self.commands[-1].merge(command)
            if merged:
                return

        self.commands.append(command)

    def merge(self, other):
        """Try and merge a command."""
        return False

    def redo(self):
        """Redo the sub-commands."""

        for cmd in self.commands:
            cmd.redo()

    def undo(self):
        """Undo the sub-commands."""

        for cmd in self.commands:
            cmd.undo()


class UndoHistory(HasStrictTraits):
    """Manages a list of undoable changes."""

    # -------------------------------------------------------------------------
    #  Trait definitions:
    # -------------------------------------------------------------------------

    #: The undo manager for the history.
    manager = Instance(IUndoManager, allow_none=False)

    #: The command stack for the history.
    stack = Instance(ICommandStack, allow_none=False)

    #: The current position in the list
    now = Property(Int, observe='stack._index')

    #: Fired when state changes to undoable
    undoable = Event(False)

    #: Fired when state changes to redoable
    redoable = Event(False)

    #: Can an action be undone?
    can_undo = Property(Bool, observe='_can_undo')

    #: Can an action be redone?
    can_redo = Property(Bool, observe='_can_redo')

    _can_undo = Bool()

    _can_redo = Bool()

    def add(self, undo_item, extend=False):
        """Adds an UndoItem to the history."""
        if extend:
            self.extend(undo_item)
        else:
            self.manager.active_stack = self.stack
            self.stack.push(undo_item)

    def extend(self, undo_item):
        """Extends the undo history.

        If possible the method merges the new UndoItem with the last item in
        the history; otherwise, it appends the new item.
        """
        self.manager.active_stack = self.stack
        # get the last command in the stack
        # XXX this is using CommandStack internals that it should not
        # XXX this should be re-architected to use the macro interface
        # XXX it possibly should be removed altogether
        entries = self.stack._stack
        if len(entries) > 0:
            command = entries[-1].command
            if not isinstance(command, _MultiUndoItem):
                command = _MultiUndoItem(commands=[command])
                entries[-1].command = command
        else:
            command = _MultiUndoItem(commands=[])
        command.push(undo_item)

    def undo(self):
        """Undoes an operation."""
        if self.can_undo:
            self.manager.undo()

    def redo(self):
        """Redoes an operation."""
        if self.can_redo:
            self.manager.redo()

    def revert(self):
        """Reverts all changes made so far and clears the history."""
        # undo everything
        self.manager.active_stack = self.stack
        self.stack.undo(sequence_nr=-1)
        self.clear()

    def clear(self):
        """Clears the undo history."""
        self.manager.active_stack = self.stack
        self.stack.clear()

    @observe('manager.stack_updated')
    def _observe_stack_updated(self, event):
        """Update undo/redo state."""
        self._can_undo = self.manager and self.manager.undo_name != ""
        self._can_redo = self.manager and self.manager.redo_name != ""

    @observe('_can_undo')
    def _observe_can_undo(self, event):
        self.undoable = event.new

    @observe('_can_redo')
    def _observe_can_redo(self, event):
        self.redoable = event.new

    @cached_property
    def _get_now(self):
        return self.stack._index + 1

    def _get_can_undo(self):
        return self._can_undo

    def _get_can_redo(self):
        return self._can_redo

    def _manager_default(self):
        manager = UndoManager()
        return manager

    def _stack_default(self):
        stack = CommandStack(undo_manager=self.manager)
        return stack


class UndoHistoryUndoItem(AbstractUndoItem):
    """An undo item for the undo history."""

    # -------------------------------------------------------------------------
    #  Trait definitions:
    # -------------------------------------------------------------------------

    #: The undo history to undo or redo
    history = Instance(UndoHistory)

    def undo(self):
        """Undoes the change."""
        history = self.history
        for i in range(history.now - 1, -1, -1):
            items = history.history[i]
            for j in range(len(items) - 1, -1, -1):
                items[j].undo()

    def redo(self):
        """Re-does the change."""
        history = self.history
        for i in range(0, history.now):
            for item in history.history[i]:
                item.redo()
