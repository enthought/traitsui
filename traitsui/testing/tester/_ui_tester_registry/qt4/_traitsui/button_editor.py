# (C) Copyright 2004-2023 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

from traitsui.testing.tester.command import MouseClick
from traitsui.testing.tester.query import DisplayedText
from traitsui.testing.tester._ui_tester_registry.qt import (
    _interaction_helpers,
)
from traitsui.qt.button_editor import CustomEditor, SimpleEditor


def register(registry):
    """Register solvers/handlers specific to qt Button Editors
    for the given registry.

    If there are any conflicts, an error will occur.

    Parameters
    ----------
    registry : TargetRegistry
    """

    handlers = [
        (
            MouseClick,
            lambda wrapper, _: _interaction_helpers.mouse_click_qwidget(
                wrapper._target.control, wrapper.delay
            ),
        ),
        (DisplayedText, lambda wrapper, _: wrapper._target.control.text()),
    ]

    for target_class in [SimpleEditor, CustomEditor]:
        for interaction_class, handler in handlers:
            registry.register_interaction(
                target_class=target_class,
                interaction_class=interaction_class,
                handler=handler,
            )
