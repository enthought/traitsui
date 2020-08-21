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
from pyface.qt.QtTest import QTest

from traitsui.testing.exceptions import Disabled
from traitsui.qt4.key_event_to_name import key_map as _KEY_MAP

def key_press(widget, key, delay=0):
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

## Generic Handlers ############################

def mouse_click_qwidget(wrapper, interaction):
    """ Performs a mouce click on a Qt widget.

    Parameters
    ----------
    wrapper : UIWrapper
        The wrapper object wrapping the Qt widget.
    interaction : instance of traitsui.testing.tester.command.MouseClick
        interaction is unused here, but it is included so that the function
        matches the expected format for a handler.  Note this handler is
        intended to be used with an interaction_class of a MouseClick.  
    """
    QTest.mouseClick(
        wrapper.target,
        QtCore.Qt.LeftButton,
        delay=wrapper.delay,
    )

def key_sequence_qwidget(wrapper, interaction):
    if not wrapper.target.isEnabled():
        raise Disabled("{!r} is disabled.".format(wrapper.target))
    QTest.keyClicks(wrapper.target, interaction.sequence, delay=wrapper.delay)


def key_press_qwidget(wrapper, interaction):
    if not wrapper.target.isEnabled():
        raise Disabled("{!r} is disabled.".format(wrapper.target))
    key_press(wrapper.target, interaction.key, delay=wrapper.delay)
