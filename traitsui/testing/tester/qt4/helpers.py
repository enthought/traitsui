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
from pyface.qt import QtCore, QtGui
from pyface.qt.QtTest import QTest

from traitsui.testing.tester.compat import check_key_compat
from traitsui.testing.tester.exceptions import Disabled
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
        Note: modifiers (e.g. Shift, Alt, etc. are not currently supported)
    delay : int
        Time delay (in ms) in which the key click will be performed.
    """

    mapping = {name: event for event, name in _KEY_MAP.items()}
    if key not in mapping:
        raise ValueError(
            "Unknown key {!r}. Expected one of these: {!r}".format(
                key, sorted(mapping)
            ))
    QTest.keyClick(
        widget,
        mapping[key],
        QtCore.Qt.NoModifier,
        delay=delay,
    )


def check_q_model_index_valid(index):
    """ Checks if a given QModelIndex is valid.

    Parameters
    ----------
    index : QModelIndex

    Raises
    ------
    LookupError
        If the index is not valid.
    """
    if not index.isValid():
        row = index.row()
        column = index.column()
        raise LookupError(
            "Unabled to locate item with row {!r} and column {!r}.".format(
                row, column,
            )
        )


# Generic Handlers ###########################################################


def displayed_text_qobject(widget):
    ''' Helper function to define handlers for various Qwidgets to handle
    query.DisplayedText interactions.

    Parameters
    ----------
    widget : Qwidget
        The Qwidget object with text to be displayed.  Should be one of the
        following QWidgets: 1) QtGui.QLineEdit 2) QtGui.QTextEdit or
        3) QtGui.QLabel

    Notes
    -----
    Qt SimpleEditors occassionally use QtGui.QTextEdit as their control, and
    other times use QtGui.QLineEdit
    '''
    if isinstance(widget, QtGui.QLineEdit):
        return widget.displayText()
    elif isinstance(widget, QtGui.QTextEdit):
        return widget.toPlainText()
    else:
        return widget.text()


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


def mouse_click_tab_index(tab_widget, index, delay):
    """ Performs a mouse click on a tab at an index in a QtGui.QTabWidget.

    Parameters
    ----------
    tab_widget : QtGui.QTabWidget
        The tab widget containing the tab to be clicked.
    index : int
        The index of the tab to be clicked.
    delay : int
        Time delay (in ms) in which click will be performed.
    """
    tabbar = tab_widget.tabBar()
    rect = tabbar.tabRect(index)
    QTest.mouseClick(
        tabbar,
        QtCore.Qt.LeftButton,
        QtCore.Qt.NoModifier,
        rect.center(),
        delay=delay,
    )


def mouse_click_qlayout(layout, index, delay):
    """ Performs a mouse click on a widget at an index in a QLayout.

    Parameters
    ----------
    layout : Qlayout
        The layout containing the widget to be clicked
    index : int
        The index of the widget in the layout to be clicked
    """
    if not 0 <= index < layout.count():
        raise IndexError(index)
    widget = layout.itemAt(index).widget()
    QTest.mouseClick(
        widget,
        QtCore.Qt.LeftButton,
        delay=delay,
    )


def mouse_click_item_view(model, view, index, delay):
    """ Perform mouse click on the given QAbstractItemModel (model) and
    QAbstractItemView (view) with the given row and column.

    Parameters
    ----------
    model : QAbstractItemModel
        Model from which QModelIndex will be obtained
    view : QAbstractItemView
        View from which the widget identified by the index will be
        found and key sequence be performed.
    index : QModelIndex

    Raises
    ------
    LookupError
        If the index cannot be located.
        Note that the index error provides more
    """
    check_q_model_index_valid(index)
    rect = view.visualRect(index)
    QTest.mouseClick(
        view.viewport(),
        QtCore.Qt.LeftButton,
        QtCore.Qt.NoModifier,
        rect.center(),
        delay=delay,
    )


def mouse_click_combobox(combobox, index, delay):
    """ Perform a mouse click on a QComboBox at a given index.

    Paramters
    ---------
    combobox : QtGui.ComboBox
        The combobox to be clicked.
    index : int
        The index of the item in the combobox to be clicked.
    delay : int
        Time delay (in ms) in which each key click in the sequence will be
        performed.
    """
    q_model_index = combobox.model().index(index, 0)
    check_q_model_index_valid(q_model_index)
    mouse_click_item_view(
        model=combobox.model(),
        view=combobox.view(),
        index=q_model_index,
        delay=delay,
    )
    # Otherwise the click won't get registered.
    key_click(
        combobox.view().viewport(), key="Enter",
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


def key_sequence_textbox(control, interaction, delay):
    """ Performs simulated typing of a sequence of keys on a widget that is
    a textbox. The keys are restricted to values also supported for testing
    wx.TextCtrl.

    Parameters
    ----------
    control : QWidget
        The Qt widget intended to hold text for editing.
        e.g. QLineEdit and QTextEdit
    interaction : instance of command.KeySequence
        The interaction object holding the sequence of key inputs
        to be simulated being typed
    delay : int
        Time delay (in ms) in which each key click in the sequence will be
        performed.
    """
    for key in interaction.sequence:
        check_key_compat(key)
    if not control.hasFocus():
        key_click(widget=control, key="End", delay=0)
    key_sequence_qwidget(control=control, interaction=interaction, delay=delay)


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


def key_click_qslider(control, interaction, delay):
    valid_keys = {"Left", "Right", "Up", "Down", "Page Up", "Page Down"}
    if interaction.key not in valid_keys:
        raise ValueError("Unexpected Key.")
    else:
        key_click(control, interaction.key, delay)
