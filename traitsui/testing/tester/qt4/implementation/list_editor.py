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
from traitsui.testing.tester import command, locator, query
from traitsui.testing.tester.qt4 import helpers

from traitsui.qt4.list_editor import (
    CustomEditor,
)

def find_by_name_in_nested_ui(wrapper, location):
    new_interactor = wrapper.locate(locator.NestedUI())
    return new_interactor.find_by_name(location.name).target

class _IndexedCustomEditor:
    """ Wrapper for a ListEditor (custom) with an index.
    """

    def __init__(self, target, index):
        self.target = target
        self.index = index

    @classmethod
    def from_location(cls, wrapper, location):
        return cls(
            target=wrapper.target,
            index=location.index,
        )

    @classmethod
    def register(cls, registry):
        registry.register_solver(
            target_class=CustomEditor,
            locator_class=locator.Index,
            solver=cls.from_location,
        )
        registry.register_solver(
            target_class=cls,
            locator_class=locator.NestedUI,
            solver=lambda wrapper, _: wrapper.target._get_nested_ui(),
        )

        registry.register_solver(
            target_class=cls,
            locator_class=locator.TargetByName,
            solver=find_by_name_in_nested_ui,
        )

    def _get_nested_ui(self):
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

    # CustomEditor
    _IndexedCustomEditor.register(registry)
