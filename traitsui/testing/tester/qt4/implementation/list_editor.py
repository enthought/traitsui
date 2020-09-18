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
from traitsui.testing.tester.common_ui_targets import _BaseSourceWithLocation
from traitsui.testing.tester.registry_helper import (
    register_traitsui_ui_solvers,
)
from traitsui.testing.tester.qt4 import helpers
from traitsui.qt4.list_editor import (
    CustomEditor,
    NotebookEditor,
)


class _IndexedNotebookEditor(_BaseSourceWithLocation):
    """ Wrapper for a ListEditor (Notebook) with an index.
    """
    source_class = NotebookEditor
    locator_class = locator.Index
    handlers = [
        (command.MouseClick,
            (lambda wrapper, _: helpers.mouse_click_tab_index(
                tab_widget=wrapper.target.source.control,
                index=wrapper.target.location.index,
                delay=wrapper.delay))),
    ]

    @classmethod
    def register(cls, registry):
        """ Class method to register interactions on a _IndexedNotebookEditor
        for the given registry.

        If there are any conflicts, an error will occur.

        Parameters
        ----------
        registry : TargetRegistry
            The registry being registered to.
        """
        super().register(registry)
        register_traitsui_ui_solvers(
            registry=registry,
            target_class=cls,
            traitsui_ui_getter=lambda target: target._get_nested_ui()
        )

    def _get_nested_ui(self):
        """ Method to get the nested ui corresponding to the List element at
        the given index.
        """
        return self.source._uis[self.location.index][1]


class _IndexedCustomEditor(_BaseSourceWithLocation):
    """ Wrapper for a ListEditor (custom) with an index.
    """
    source_class = CustomEditor
    locator_class = locator.Index

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
        super().register(registry)
        register_traitsui_ui_solvers(
            registry=registry,
            target_class=cls,
            traitsui_ui_getter=lambda target: target._get_nested_ui()
        )

    def _get_nested_ui(self):
        """ Method to get the nested ui corresponding to the List element at
        the given index.
        """
        row, column = divmod(self.location.index, self.source.factory.columns)
        # there are two columns for each list item (one for the item itself,
        # and another for the list menu button)
        column = 2*column
        grid_layout = self.source._list_pane.layout()
        item = grid_layout.itemAtPosition(row, column)
        if item is None:
            raise IndexError(self.location.index)
        if self.source.scrollable:
            self.source.control.ensureWidgetVisible(item.widget())

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
