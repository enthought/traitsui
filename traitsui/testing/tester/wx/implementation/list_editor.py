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
from traitsui.testing.tester import locator
from traitsui.testing.tester.registry_helper import register_nested_ui_solvers

from traitsui.wx.list_editor import (
    CustomEditor,
)


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
        # each list item gets a corresponding ImageControl item (allows one to
        # add items to the list before, after, delete, etc.) along with the
        # item itself.  Thus, index is actually an index over the odd elements
        # of the list of children corresponding to items in the list we would
        # want to interact with
        new_index = 2*self.index + 1
        WindowList = self.target.control.GetChildren()
        item = WindowList[new_index]
        return item._editor._ui


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
