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

from functools import reduce

from pyface.qt import QtCore
from pyface.qt import QtGui
from pyface.qt.QtTest import QTest

from traitsui.testing.tester import command, query
from traitsui.testing.tester.exceptions import Disabled
from traitsui.testing.tester.registry import TargetRegistry
from traitsui.qt4.key_event_to_name import key_map as _KEY_MAP


def key_click(widget, key, delay=0):
    """ Performs a key click of the given key on the given widget after
    a delay.

    Parameters
    ----------
    widget : Qwidget
        The Qt widget to be key clicked.
    key : str
        Standardized (pyface) name for a keyboard event.
        e.g. "Enter", "Tab", "Space", "0", "1", "A", ...
    delay : int
        Time delay (in ms) in which the key click will be performed.
    """
    if "-" in key:
        *modifiers, key = key.split("-")
    else:
        modifiers = []

    modifier_to_qt = {
        "Ctrl": QtCore.Qt.ControlModifier,
        "Alt": QtCore.Qt.AltModifier,
        "Meta": QtCore.Qt.MetaModifier,
        "Shift": QtCore.Qt.ShiftModifier,
    }
    qt_modifiers = [modifier_to_qt[modifier] for modifier in modifiers]
    qt_modifier = reduce(
        lambda x, y: x | y, qt_modifiers, QtCore.Qt.NoModifier
    )

    mapping = {name: event for event, name in _KEY_MAP.items()}
    if key not in mapping:
        raise ValueError(
            "Unknown key {!r}. Expected one of these: {!r}".format(
                key, sorted(mapping)
            ))
    QTest.keyClick(
        widget,
        mapping[key],
        qt_modifier,
        delay=delay,
    )

# Generic Handlers ###########################################################


def mouse_click_qwidget(control, delay):
    """ Performs a mouce click on a Qt widget.

    Parameters
    ----------
    control : Qwidget
        The Qt widget to be clicked.
    delay : int
        Time delay (in ms) in which click will be performed.
    """
    QTest.mouseClick(
        control,
        QtCore.Qt.LeftButton,
        delay=delay,
    )


def key_sequence_qwidget(control, interaction, delay):
    """ Performs simulated typing of a sequence of keys on the given widget
    after a delay.

    Parameters
    ----------
    control : Qwidget
        The Qt widget to be acted on.
    interaction : instance of command.KeySequence
        The interaction object holding the sequence of key inputs
        to be simulated being typed
    delay : int
        Time delay (in ms) in which each key click in the sequence will be
        performed.
    """
    if not control.isEnabled():
        raise Disabled("{!r} is disabled.".format(control))
    QTest.keyClicks(control, interaction.sequence, delay=delay)


def key_click_qwidget(control, interaction, delay):
    """ Performs simulated typing of a key on the given widget after a delay.

    Parameters
    ----------
    control : Qwidget
        The Qt widget to be acted on.
    interaction : instance of command.KeyClick
        The interaction object holding the key input
        to be simulated being typed
    delay : int
        Time delay (in ms) in which the key click will be performed.
    """
    if not control.isEnabled():
        raise Disabled("{!r} is disabled.".format(control))
    key_click(control, interaction.key, delay=delay)


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
         QtGui.QLineEdit,
         QtGui.QTextEdit,
         QtGui.QPushButton,
     ]
     handlers = [
         (command.KeySequence, (lambda wrapper, interaction: key_sequence_qwidget(
                                wrapper.target, interaction.sequence, wrapper.delay))),
         (command.KeyClick, (lambda wrapper, interaction: key_click_qwidget(
                             wrapper.target, interaction.key, wrapper.delay))),
         (command.MouseClick, (lambda wrapper, _: mouse_click_qwidget(
             wrapper.target, wrapper.delay))),
     ]
     for widget_class in widget_classes:
         for interaction_class, handler in handlers:
             registry.register_handler(
                 target_class=widget_class,
                 interaction_class=interaction_class,
                 handler=handler,
             )

     registry.register_handler(
         target_class=QtGui.QLineEdit,
         interaction_class=query.DisplayedText,
         handler=lambda wrapper, _: wrapper.target.displayText(),
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