#  Copyright (c) 2005-2020, Enthought, Inc.
#  All rights reserved.
#
#  This software is provided without warranty under the terms of the BSD
#  license included in LICENSE.txt and may be redistributed only
#  under the conditions described in the aforementioned license.  The license
#  is also available online at http://www.enthought.com/licenses/BSD.txt
#
#  Thanks for using Enthought open source!
#
from traitsui.testing.tester import command, locator
from traitsui.testing.tester.registry_helper import register_nested_ui_solvers
from traitsui.testing.tester.qt4 import helpers
from traitsui.qt4.list_editor import (
    CustomEditor,
    NotebookEditor,
)


class _IndexedNotebookEditor:

    def __init__(self, target, index):
        self.target = target
        self.index = index

    @classmethod
    def from_location(cls, wrapper, location):
        # Raise IndexError early
        wrapper.target._uis[location.index]
        return cls(
            target=wrapper.target,
            index=location.index,
        )

    @classmethod
    def register(cls, registry):
        registry.register_solver(
            target_class=NotebookEditor,
            locator_class=locator.Index,
            solver=cls.from_location,
        )

        register_nested_ui_solvers(
            registry=registry,
            target_class=cls,
            nested_ui_getter=lambda target: target._get_nested_ui()
        )

        registry.register_handler(
            target_class=cls,
            interaction_class=command.MouseClick,
            handler=lambda wrapper, _: helpers.mouse_click_tab_index(
                tab_widget=wrapper.target.target.control,
                index=wrapper.target.index,
                delay=wrapper.delay),
        )

    def _get_nested_ui(self):
        return self.target._uis[self.index][1]


class _IndexedCustomEditor:
    """ Wrapper for a ListEditor (custom) with an index.
    """

    def __init__(self, target, index):
        """
        Parameters
        ----------
        target : CustomEditor
            The Custom List Editor
        index : int
            The index of interest.
        """
        self.target = target
        self.index = index

    @classmethod
    def register(cls, registry):
        """ Class method to register interactions on a _IndexedCustomEditor
        for the given registry.

        If there are any conflicts, an error will occur.

        Parameters
        ----------
        registry : TargetRegistry
            The registry being registered to.
        """
        registry.register_solver(
            target_class=CustomEditor,
            locator_class=locator.Index,
            solver=lambda wrapper, location:
                cls(target=wrapper.target, index=location.index)
        )
        register_nested_ui_solvers(
            registry=registry,
            target_class=cls,
            nested_ui_getter=lambda target: target._get_nested_ui()
        )

    def _get_nested_ui(self):
        """ Method to get the nested ui corresponding to the List element at
        the given index.
        """
        row, column = divmod(self.index, self.target.factory.columns)
        # there are two columns for each list item (one for the item itself,
        # and another for the list menu button)
        column = 2*column
        grid_layout = self.target._list_pane.layout()
        item = grid_layout.itemAtPosition(row, column)
        if item is None:
            raise IndexError(self.index)
        if self.target.scrollable:
            self.target.control.ensureWidgetVisible(item.widget())

        return item.widget()._editor._ui


def register(registry):
    """ Register interactions for the given registry.

    If there are any conflicts, an error will occur.

    Parameters
    ----------
    registry : TargetRegistry
        The registry being registered to.
    """
    # NotebookEditor
    _IndexedNotebookEditor.register(registry)
    # CustomEditor
    _IndexedCustomEditor.register(registry)
