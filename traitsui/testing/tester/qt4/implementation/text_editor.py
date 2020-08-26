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
from traitsui.testing.tester.qt4 import helpers
from traitsui.qt4.text_editor import CustomEditor, ReadonlyEditor, SimpleEditor


def simple_DisplayedText_handler(wrapper, interaction):
    ''' Handler for SimpleEditor to handle query.DisplayedText interactions.

    Parameters
    ----------
    wrapper : UIWrapper
        the UIWrapper object wrapping the SimpleEditor
    interaction : Instance of query.DisplayedText
        This arguiment is not used by this function. It is included so that
        the function matches the standard format for a handler.  The intended
        interaction should always be query.DisplayedText

    Notes
    -----
    Qt SimpleEditors occassionally use QtGui.QTextEdit as their control, and
    other times use QtGui.QLineEdit
    '''
    if isinstance(wrapper.target.control, QtGui.QLineEdit):
        return wrapper.target.control.displayText()
    elif isinstance(wrapper.target.control, QtGui.QTextEdit):
        return wrapper.target.control.toPlainText()


def register(registry):
    """ Register actions for the given registry.

    If there are any conflicts, an error will occur.
    """

    handlers = [
        (command.KeySequence, (lambda wrapper, interaction: helpers.key_sequence_qwidget(
                            wrapper.target.control, interaction, wrapper.delay))),
        (command.KeyClick, (lambda wrapper, interaction: helpers.key_click_qwidget(
                            wrapper.target.control, interaction, wrapper.delay))),
        (command.MouseClick, (lambda wrapper, _: helpers.mouse_click_qwidget(
                            wrapper.target.control, wrapper.delay))),
    ]
    for target_class in [CustomEditor, ReadonlyEditor, SimpleEditor]:
        for interaction_class, handler in handlers:
            registry.register_handler(
                target_class=target_class,
                interaction_class=interaction_class,
                handler=handler,
            )

    registry.register_handler(
        target_class=CustomEditor,
        interaction_class=query.DisplayedText,
        handler=lambda wrapper, _: wrapper.target.control.toPlainText(),
    )
    registry.register_handler(
        target_class=SimpleEditor,
        interaction_class=query.DisplayedText,
        handler=simple_DisplayedText_handler,
    )
    registry.register_handler(
        target_class=ReadonlyEditor,
        interaction_class=query.DisplayedText,
        handler=lambda wrapper, _: wrapper.target.control.text(),
    )
