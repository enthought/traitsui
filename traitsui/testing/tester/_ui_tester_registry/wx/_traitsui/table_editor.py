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

from traitsui.wx.table_editor import SimpleEditor

from traitsui.testing.api import (
    Cell,
    DisplayedText,
    MouseClick,
    MouseDClick,
    KeyClick,
    KeySequence,
    Selected,
)
from traitsui.testing.tester._ui_tester_registry._common_ui_targets import (
    BaseSourceWithLocation
)
from traitsui.testing.tester._ui_tester_registry.wx import (
    _interaction_helpers,
    _registry_helper
)


class _SimpleEditorWithCell(BaseSourceWithLocation):
    source_class = SimpleEditor
    locator_class = Cell
    handlers = [
        (MouseClick,
            (lambda wrapper, interaction:
                _interaction_helpers.mouse_click_cell_in_grid(
                    control=wrapper._target.source.grid.control,
                    cell=wrapper._target.location,
                    delay=wrapper.delay))),
    ]


def register(registry):
    """ Register interactions for the given registry.

    If there are any conflicts, an error will occur.

    Parameters
    ----------
    registry : TargetRegistry
        The registry being registered to.
    """
    _SimpleEditorWithCell.register(registry)
