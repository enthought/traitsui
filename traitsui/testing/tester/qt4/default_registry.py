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

from pyface.qt import QtGui

from traitsui.testing.tester import command
from traitsui.testing.tester.registry import TargetRegistry
from traitsui.testing.tester.qt4 import helpers
from traitsui.testing.tester.qt4.implementation import (
    button_editor,
)

def get_default_registry():
    """ Creates a default registry for UITester that is qt specific.

    Returns
    -------
    registry : TargetRegistry
        The default registry containing implementations for TraitsUI editors
        that is qt specific.  
    """
    registry = TargetRegistry()

    button_editor.register(registry)
    
    widget_classes = [
        QtGui.QPushButton,
    ]
    handlers = [
        (command.MouseClick, helpers.mouse_click_qwidget),
    ]
    for widget_class in widget_classes:
        for interaction_class, handler in handlers:
            registry.register_handler(
                target_class=widget_class,
                interaction_class=interaction_class,
                handler=handler,
            )

    return registry
