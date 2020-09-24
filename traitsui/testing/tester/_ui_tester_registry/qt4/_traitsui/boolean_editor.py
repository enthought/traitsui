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
from traitsui.testing.api import DisplayedText, MouseClick
from traitsui.testing.tester._ui_tester_registry.qt4 import (
    _interaction_helpers
)
from traitsui.qt4.boolean_editor import ReadonlyEditor, SimpleEditor


def register(registry):
    """ Register solvers/handlers specific to qt Boolean Editors
    for the given registry.

    If there are any conflicts, an error will occur.

    Parameters
    ----------
    registry : TargetRegistry
    """
    registry.register_interaction(
        target_class=SimpleEditor,
        interaction_class=MouseClick,
        handler=lambda wrapper, _: _interaction_helpers.mouse_click_qwidget(
            control=wrapper._target.control, delay=wrapper.delay
        )
    )

    registry.register_interaction(
        target_class=ReadonlyEditor,
        interaction_class=DisplayedText,
        handler=lambda wrapper, _: wrapper._target.control.text()
    )
