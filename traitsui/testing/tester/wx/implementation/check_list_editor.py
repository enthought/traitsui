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

from traitsui.wx.check_list_editor import CustomEditor
from traitsui.testing.tester import command, locator
from traitsui.testing.tester.wx import helpers


class _IndexedCustomCheckListEditor:
    """ Wrapper for CheckListEditor + locator.Index """

    def __init__(self, target, index):
        """
        Parameters
        ----------
        target : CustomCheckListEditor
            The Custom Check List Editor
        index : int
            The index of interest.
        """
        self.target = target
        self.index = index

    @classmethod
    def from_location_index(cls, wrapper, location):
        """ Creates an instance of _IndexedCustomCheckListEditor from a
        wrapper wrapping a Custom CheckListEditor, and a locator.Index
        object.

        Parameters
        ----------
        wrapper : UIWrapper
            wrapper wrapping a Custom CheckListEditor
        location : Instance of locator.Index
        """
        # Conform to the call signature specified in the register
        return cls(
            target=wrapper.target,
            index=location.index,
        )

    @classmethod
    def register(cls, registry):
        """ Class method to register interactions on an
        _IndexedCustomCheckListEditor for the given registry.

        If there are any conflicts, an error will occur.

        Parameters
        ----------
        registry : TargetRegistry
            The registry being registered to.
        """
        registry.register_solver(
            target_class=CustomEditor,
            locator_class=locator.Index,
            solver=cls.from_location_index,
        )
        registry.register_handler(
            target_class=cls,
            interaction_class=command.MouseClick,
            handler=lambda wrapper, _:
                (helpers.mouse_click_checkbox_child_in_panel(
                    control=wrapper.target.target.control,
                    index=wrapper.target.index,
                    delay=wrapper.delay))
        )


def register(registry):
    """ Register interactions for the given registry.

    If there are any conflicts, an error will occur.

    Parameters
    ----------
    registry : TargetRegistry
        The registry being registered to.
    """
    _IndexedCustomCheckListEditor.register(registry)
