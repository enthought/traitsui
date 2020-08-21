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

from traitsui.testing.tester import command, query
from traitsui.testing.tester.registry import TargetRegistry
from traitsui.testing.tester.qt4 import helpers
from traitsui.testing.tester.qt4.implementation import (
    button_editor,
    text_editor,
)

def get_default_registry():
    """ Creates a default registry for UITester that is qt specific.

    Returns
    -------
    registry : TargetRegistry
        The default registry containing implementations for TraitsUI editors
        that is qt specific.  
    """
    registry = get_qobject_registry()

    # ButtonEditor
    button_editor.register(registry)

    # TextEditor
    text_editor.register(registry)


    return registry


def get_qobject_registry():
    """ Creates a generic registry for handling/solving qt objects. (i.e.
    this registry is independent of TraitsUI)

    Returns
    -------
    registry : TargetRegistry
        Registry containing qt specific generic handlers and solvers.
    """
    registry = TargetRegistry()

    widget_classes = [
        QtGui.QTextEdit,
        QtGui.QPushButton,
    ]
    handlers = [
        (command.KeySequence, helpers.key_sequence_qwidget),
        (command.KeyClick, helpers.key_press_qwidget),
        (command.MouseClick, helpers.mouse_click_qwidget),
    ]
    for widget_class in widget_classes:
        for interaction_class, handler in handlers:
            registry.register_handler(
                target_class=widget_class,
                interaction_class=interaction_class,
                handler=handler,
            )

    registry.register_handler(
        target_class=QtGui.QTextEdit,
        interaction_class=query.DisplayedText,
        handler=lambda wrapper, _: wrapper.target.toPlainText(),
    )

    registry.register_handler(
        target_class=QtGui.QPushButton,
        interaction_class=query.DisplayedText,
        handler=lambda wrapper, _: wrapper.target.text(),
    )

    return registry

