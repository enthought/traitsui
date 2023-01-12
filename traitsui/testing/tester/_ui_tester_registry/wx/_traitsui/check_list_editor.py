# (C) Copyright 2004-2023 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

import wx

from traitsui.wx.check_list_editor import CustomEditor
from traitsui.testing.tester.command import MouseClick
from traitsui.testing.tester.locator import Index
from traitsui.testing.tester._ui_tester_registry._common_ui_targets import (
    BaseSourceWithLocation,
)
from traitsui.testing.tester._ui_tester_registry._layout import (
    column_major_to_row_major,
)
from traitsui.testing.tester._ui_tester_registry.wx import _interaction_helpers


class _IndexedCustomCheckListEditor(BaseSourceWithLocation):
    """Wrapper for CheckListEditor + Index"""

    source_class = CustomEditor
    locator_class = Index
    handlers = [
        (
            MouseClick,
            (
                lambda wrapper, _: _interaction_helpers.mouse_click_checkbox_child_in_panel(
                    control=wrapper._target.source.control,
                    index=convert_index(
                        source=wrapper._target.source,
                        index=wrapper._target.location.index,
                    ),
                    delay=wrapper.delay,
                )
            ),
        ),
    ]


def convert_index(source, index):
    """Helper function to convert an index for a GridSizer so that the
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
    """Register interactions for the given registry.

    If there are any conflicts, an error will occur.

    Parameters
    ----------
    registry : TargetRegistry
        The registry being registered to.
    """
    _IndexedCustomCheckListEditor.register(registry)
