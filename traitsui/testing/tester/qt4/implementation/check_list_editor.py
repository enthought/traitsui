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

from traitsui.qt4.check_list_editor import CustomEditor
from traitsui.testing.tester import command, locator
from traitsui.testing.tester.common_ui_targets import _BaseSourceWithLocation
from traitsui.testing.tester.editors.layout import column_major_to_row_major
from traitsui.testing.tester.qt4 import helpers


class _IndexedCustomCheckListEditor(_BaseSourceWithLocation):
    """ Wrapper for CheckListEditor + locator.Index """
    source_class = CustomEditor
    locator_class = locator.Index
    handlers = [
        (command.MouseClick, (lambda wrapper, _: helpers.mouse_click_qlayout(
            layout=wrapper.target.source.control.layout(),
            index=convert_index(
                layout=wrapper.target.source.control.layout(),
                index=wrapper.target.location.index,
            ),
            delay=wrapper.delay))),
    ]


def convert_index(layout, index):
    """ Helper function to convert an index for a QGridLayout so that the
    index counts over the grid in the correct direction.
    The grid is always populated in row major order, but it is done so in
    such a way that the entries appear in column major order.
    Qlayouts are indexed in the order they are populated, so to access
    the correct element we may need to convert a column-major based index
    into a row-major one.

    Parameters
    ----------
    layout : QGridLayout
        The layout of interest
    index : int
        the index of interest
    """
    n = layout.count()
    num_cols = layout.columnCount()
    num_rows = layout.rowCount()
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
