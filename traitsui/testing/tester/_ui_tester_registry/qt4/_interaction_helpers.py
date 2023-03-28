# (C) Copyright 2004-2023 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!
import warnings

from pyface.qt import QtCore, QtGui
from pyface.qt.QtTest import QTest

from traitsui.testing.tester._ui_tester_registry._compat import (
    check_key_compat,
)
from traitsui.testing.tester.exceptions import Disabled
from traitsui.qt.key_event_to_name import key_map as _KEY_MAP


def key_click(widget, key, delay):
    """Performs a key click of the given key on the given widget after
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
            )
        )
    QTest.keyClick(
        widget,
        mapping[key],
        QtCore.Qt.KeyboardModifier.NoModifier,
        delay=delay,
    )


def check_q_model_index_valid(index):
    """Checks if a given QModelIndex is valid.

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
                row,
                column,
            )
        )


# Generic Handlers ###########################################################


def displayed_text_qobject(widget):
    '''Helper function to define handlers for various Qwidgets to handle
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
    """Performs a mouse click on a Qt widget.

    Parameters
    ----------
    control : Qwidget
        The Qt widget to be clicked.
    delay : int
        Time delay (in ms) in which click will be performed.
    """

    # for QAbstractButtons we do not use QTest.mouseClick as it assumes the
    # center of the widget as the location to be clicked, which may be
    # incorrect. For QAbstractButtons we can simply call their click method.
    if isinstance(control, QtGui.QAbstractButton):
        if delay > 0:
            QTest.qSleep(delay)
        control.click()
    elif control is not None:
        QTest.mouseClick(
            control,
            QtCore.Qt.MouseButton.LeftButton,
            delay=delay,
        )
    else:
        raise ValueError("control is None")


def mouse_click_tab_index(tab_widget, index, delay):
    """Performs a mouse click on a tab at an index in a QtGui.QTabWidget.

    Parameters
    ----------
    tab_widget : QtGui.QTabWidget
        The tab widget containing the tab to be clicked.
    index : int
        The index of the tab to be clicked.
    delay : int
        Time delay (in ms) in which click will be performed.

    Raises
    ------
    IndexError
        If the index is out of range.
    """
    if not 0 <= index < tab_widget.count():
        raise IndexError(index)
    tabbar = tab_widget.tabBar()
    rect = tabbar.tabRect(index)
    QTest.mouseClick(
        tabbar,
        QtCore.Qt.MouseButton.LeftButton,
        QtCore.Qt.KeyboardModifier.NoModifier,
        rect.center(),
        delay=delay,
    )


def mouse_click_qlayout(layout, index, delay):
    """Performs a mouse click on a widget at an index in a QLayout.

    Parameters
    ----------
    layout : Qlayout
        The layout containing the widget to be clicked
    index : int
        The index of the widget in the layout to be clicked

    Raises
    ------
    IndexError
        If the index is out of range.
    """
    if not 0 <= index < layout.count():
        raise IndexError(index)
    widget = layout.itemAt(index).widget()
    mouse_click_qwidget(widget, delay)


def mouse_click_item_view(model, view, index, delay):
    """Perform mouse click on the given QAbstractItemModel (model) and
    QAbstractItemView (view) with the given row and column.

    Parameters
    ----------
    model : QAbstractItemModel
        Model from which QModelIndex will be obtained
    view : QAbstractItemView
        View from which the widget identified by the index will be
        found and mouse click be performed.
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
        QtCore.Qt.MouseButton.LeftButton,
        QtCore.Qt.KeyboardModifier.NoModifier,
        rect.center(),
        delay=delay,
    )


def mouse_dclick_item_view(model, view, index, delay):
    """ Perform mouse double click on the given QAbstractItemModel (model) and
    QAbstractItemView (view) with the given row and column.

    Parameters
    ----------
    model : QAbstractItemModel
        Model from which QModelIndex will be obtained
    view : QAbstractItemView
        View from which the widget identified by the index will be
        found and mouse double click be performed.
    index : QModelIndex

    Raises
    ------
    LookupError
        If the index cannot be located.
        Note that the index error provides more
    """
    check_q_model_index_valid(index)
    rect = view.visualRect(index)
    QTest.mouseDClick(
        view.viewport(),
        QtCore.Qt.LeftButton,
        QtCore.Qt.NoModifier,
        rect.center(),
        delay=delay,
    )


def key_sequence_item_view(model, view, index, sequence, delay=0):
    """ Perform Key Sequence on the given QAbstractItemModel (model) and
    QAbstractItemView (view) with the given row and column.

    Parameters
    ----------
    model : QAbstractItemModel
        Model from which QModelIndex will be obtained
    view : QAbstractItemView
        View from which the widget identified by the index will be
        found and key sequence be performed.
    index : QModelIndex
    sequence : str
        Sequence of characters to be inserted to the widget identifed
        by the row and column.

    Raises
    ------
    Disabled
        If the widget cannot be edited.
    LookupError
        If the index cannot be located.
        Note that the index error provides more
    """
    check_q_model_index_valid(index)
    widget = view.indexWidget(index)
    if widget is None:
        raise Disabled(
            "No editable widget for item at row {!r} and column {!r}".format(
                index.row(), index.column()
            )
        )
    QTest.keyClicks(widget, sequence, delay=delay)


def key_click_item_view(model, view, index, key, delay=0):
    """ Perform key press on the given QAbstractItemModel (model) and
    QAbstractItemView (view) with the given row and column.

    Parameters
    ----------
    model : QAbstractItemModel
        Model from which QModelIndex will be obtained
    view : QAbstractItemView
        View from which the widget identified by the index will be
        found and key press be performed.
    index : int
    key : str
        Key to be pressed.

    Raises
    ------
    Disabled
        If the widget cannot be edited.
    LookupError
        If the index cannot be located.
        Note that the index error provides more
    """
    check_q_model_index_valid(index)
    widget = view.indexWidget(index)
    if widget is None:
        raise Disabled(
            "No editable widget for item at row {!r} and column {!r}".format(
                index.row(), index.column()
            )
        )
    key_click(widget, key=key, delay=delay)


def get_display_text_item_view(model, view, index):
    """ Return the textural representation for the given model, row and column.

    Parameters
    ----------
    model : QAbstractItemModel
        Model from which QModelIndex will be obtained
    view : QAbstractItemView
        View from which the widget identified by the index will be
        found and key press be performed.
    index : int

    Raises
    ------
    LookupError
        If the index cannot be located.
        Note that the index error provides more
    """
    check_q_model_index_valid(index)
    return model.data(index, QtCore.Qt.DisplayRole)


def mouse_click_combobox(combobox, index, delay):
    """Perform a mouse click on a QComboBox at a given index.

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
    if combobox:
        q_model_index = combobox.model().index(index, 0)
        check_q_model_index_valid(q_model_index)
        mouse_click_item_view(
            model=combobox.model(),
            view=combobox.view(),
            index=q_model_index,
            delay=delay,
        )
        # Otherwise the click won't get registered.
        key_click(combobox.view().viewport(), key="Enter", delay=delay)
    else:
        warnings.warn(
            "Attempted to click on a non-existant combobox. Nothing was "
            "performed."
        )


def key_sequence_qwidget(control, interaction, delay):
    """Performs simulated typing of a sequence of keys on the given widget
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

    Raises
    ------
    Disabled
        If the widget is not enabled.
    """
    if not control.isEnabled():
        raise Disabled("{!r} is disabled.".format(control))
    QTest.keyClicks(control, interaction.sequence, delay=delay)


def key_sequence_textbox(control, interaction, delay):
    """Performs simulated typing of a sequence of keys on a widget that is
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
    """Performs simulated typing of a key on the given widget after a delay.

    Parameters
    ----------
    control : Qwidget
        The Qt widget to be acted on.
    interaction : instance of command.KeyClick
        The interaction object holding the key input
        to be simulated being typed
    delay : int
        Time delay (in ms) in which the key click will be performed.

    Raises
    ------
    Disabled
        If the widget is not enabled.
    """
    if not control.isEnabled():
        raise Disabled("{!r} is disabled.".format(control))
    key_click(control, interaction.key, delay=delay)


def key_click_qslider(control, interaction, delay):
    """Performs simulated typing of a key on the given slider after a delay.
    Only allowed keys are:
    "Left", "Right", "Up", "Down", "Page Up", "Page Down"
    Also, note that up related keys correspond to an increment on the slider,
    and down a decrement.

    Parameters
    ----------
    control : QSlider
        The Qt slider to be acted on.
    interaction : instance of command.KeyClick
        The interaction object holding the key input
        to be simulated being typed
    delay : int
        Time delay (in ms) in which the key click will be performed.

    Raises
    ------
    ValueError
        If the interaction.key is not one of the valid keys.
    """
    valid_keys = {"Left", "Right", "Up", "Down", "Page Up", "Page Down"}
    if interaction.key not in valid_keys:
        raise ValueError(
            "Unexpected Key. Supported keys are: {}".format(sorted(valid_keys))
        )
    else:
        key_click(control, interaction.key, delay)
