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
import wx

from traitsui.wx.check_list_editor import CustomEditor
from traitsui.testing.tester import command, locator
from traitsui.testing.tester.editors.layout import column_major_to_row_major
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
                    index=convert_index(
                        wrapper.target.target,
                        wrapper.target.index,
                    ),
                    delay=wrapper.delay))
        )


def convert_index(source, index):
    """ Helper function to convert an index for a GridSizer so that the
    index counts over the grid in the correct direction.
    The grid is always populated in row major order, however, the elements
    are assigned to each entry in the grid so that when displayed they appear
    in column major order.
    Sizers are indexed in the order they are populated, so to access
    the correct element we may need to convert a column-major based index
    into a row-major one.

    Parameters
    ----------
    control : CustomEditor
        The Custom CheckList Editor of interest. Its control is the wx.Panel
        containing child objects organized with a wx.GridSizer
    index : int
        the index of interest
    """
    sizer = source.control.GetSizer()
    if isinstance(sizer, wx.BoxSizer):
        return index
    n = len(source.names)
    num_cols = sizer.GetCols()
    num_rows = sizer.GetEffectiveRowsCount()
    return column_major_to_row_major(index, n, num_rows, num_cols)


def register(registry):
    """ Register interactions for the given registry.

    If there are any conflicts, an error will occur.

    Parameters
    ----------
    registry : TargetRegistry
        The registry being registered to.
    """
    _IndexedCustomCheckListEditor.register(registry)
