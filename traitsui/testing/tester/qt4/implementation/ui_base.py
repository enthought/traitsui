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
from traitsui.qt4.ui_base import ButtonEditor
from traitsui.testing.tester import command, query
from traitsui.testing.tester.qt4 import helpers


def register(registry):
    """ Register solvers/handlers specific to qt ui_base Editors
    for the given registry.

    If there are any conflicts, an error will occur.

    Parameters
    ----------
    registry : TargetRegistry
    """
    handlers = [
        (command.MouseClick, (lambda wrapper, _:  helpers.mouse_click_qwidget(
                              wrapper.target.control, wrapper.delay))),
        (query.DisplayedText, lambda wrapper, _: wrapper.target.control.text())
    ]
    for interaction_class, handler in handlers:
        registry.register_handler(
            target_class=ButtonEditor,
            interaction_class=interaction_class,
            handler=handler
        )
