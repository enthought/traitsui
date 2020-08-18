
from functools import reduce

from pyface.qt import QtCore
from pyface.qt.QtTest import QTest
from traitsui.qt4.key_event_to_name import key_map as _KEY_MAP
from traitsui.testing.exceptions import Disabled


def get_displayed_text(widget):
    try:
        return widget.displayText()
    except AttributeError:
        return widget.toPlainText()


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


def check_q_model_index_valid(index):
    if not index.isValid():
        row = index.row()
        column = index.column()
        raise LookupError(
            "Unabled to locate item with row {!r} and column {!r}.".format(
                row, column,
            )
        )


def mouse_click_item_view(model, view, index, delay=0):
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


def mouse_dclick_item_view(model, view, index, delay=0):
    """ Perform mouse double click on the given QAbstractItemModel (model) and
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
    QTest.mouseDClick(
        view.viewport(),
        QtCore.Qt.LeftButton,
        QtCore.Qt.NoModifier,
        rect.center(),
        delay=delay,
    )


def key_sequence_item_view(model, view, index, sequence, delay=0):
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


def key_press_item_view(model, view, index, key, delay=0):
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
    key_press(widget, key=key, delay=delay)


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


def mouse_click_tab_index(tab_widget, index, delay=0):
    tabbar = tab_widget.tabBar()
    rect = tabbar.tabRect(index)
    QTest.mouseClick(
        tabbar,
        QtCore.Qt.LeftButton,
        QtCore.Qt.NoModifier,
        rect.center(),
        delay=delay,
    )


def mouse_click_qlayout(layout, index, delay=0):
    """ Performing a mouse click on an index in a QLayout
    """
    if not 0 <= index < layout.count():
        raise IndexError(index)
    widget = layout.itemAt(index).widget()
    QTest.mouseClick(
        widget,
        QtCore.Qt.LeftButton,
        delay=delay,
    )


def mouse_click_combobox(combobox, index, delay=0):
    """ Perform a mouse click on a QComboBox.
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
    key_press(
        combobox.view().viewport(), key="Enter", delay=delay,
    )
