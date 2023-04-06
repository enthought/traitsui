# (C) Copyright 2008-2023 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

# ------------------------------------------------------------------------------
# Copyright (c) 2007, Riverbank Computing Limited
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD license.
# However, when used with the GPL version of PyQt the additional terms
# described in the PyQt GPL exception also apply

#
# Author: Riverbank Computing Limited
# ------------------------------------------------------------------------------

""" Defines the set editors for the PyQt user interface toolkit.
"""


from pyface.qt import QtCore, QtGui

from traitsui.helper import enum_values_changed

from .editor import Editor

from traits.api import Instance, Property


class SimpleEditor(Editor):
    """Simple style of editor for sets.

    The editor displays two list boxes, with buttons for moving the selected
    items from left to right, or vice versa. If **can_move_all** on the factory
    is True, then buttons are displayed for moving all the items to one box
    or the other. If the set is ordered, buttons are displayed for moving the
    selected item up or down in right-side list box.
    """

    # -------------------------------------------------------------------------
    #  Trait definitions:
    # -------------------------------------------------------------------------

    #: The top level QLayout for the editor:
    root_layout = Instance(QtGui.QLayout)

    #: Current set of enumeration names:
    names = Property()

    #: Current mapping from names to values:
    mapping = Property()

    #: Current inverse mapping from values to names:
    inverse_mapping = Property()

    #: Is set editor scrollable? This value overrides the default.
    scrollable = True

    def init(self, parent):
        """Finishes initializing the editor by creating the underlying toolkit
        widget.
        """
        self.control = QtGui.QWidget()
        self.root_layout = QtGui.QGridLayout(self.control)
        self.root_layout.setContentsMargins(0, 0, 0, 0)

        factory = self.factory
        if factory.name != "":
            self._object, self._name, self._value = self.parse_extended_name(
                factory.name
            )
            self.values_changed()
            self._object.on_trait_change(
                self._values_changed, self._name, dispatch="ui"
            )
        else:
            self._value = lambda: self.factory.values
            self.values_changed()
            factory.on_trait_change(
                self._values_changed, "values", dispatch="ui"
            )

        blayout = QtGui.QVBoxLayout()

        self._unused = self._create_listbox(
            0, self._on_unused, self._on_use, factory.left_column_title
        )

        self._use_all = self._unuse_all = self._up = self._down = None

        if factory.can_move_all:
            self._use_all = self._create_button(
                ">>", blayout, self._on_use_all
            )

        self._use = self._create_button(">", blayout, self._on_use)
        self._unuse = self._create_button("<", blayout, self._on_unuse)

        if factory.can_move_all:
            self._unuse_all = self._create_button(
                "<<", blayout, self._on_unuse_all
            )

        if factory.ordered:
            self._up = self._create_button("Move Up", blayout, self._on_up)
            self._down = self._create_button(
                "Move Down", blayout, self._on_down
            )

        self.root_layout.addLayout(blayout, 1, 1, QtCore.Qt.AlignmentFlag.AlignCenter)

        self._used = self._create_listbox(
            2, self._on_value, self._on_unuse, factory.right_column_title
        )

        self.context_object.on_trait_change(
            self.update_editor, self.extended_name + "_items?", dispatch="ui"
        )

    def _get_names(self):
        """Gets the current set of enumeration names."""
        return self._names

    def _get_mapping(self):
        """Gets the current mapping."""
        return self._mapping

    def _get_inverse_mapping(self):
        """Gets the current inverse mapping."""
        return self._inverse_mapping

    def _create_listbox(self, col, handler1, handler2, title):
        """Creates a list box."""
        # Add the column title in emphasized text:
        title_widget = QtGui.QLabel(title)
        font = QtGui.QFont(title_widget.font())
        font.setBold(True)
        font.setPointSize(font.pointSize() + 1)
        title_widget.setFont(font)
        self.root_layout.addWidget(title_widget, 0, col, QtCore.Qt.AlignmentFlag.AlignLeft)

        # Create the list box and add it to the column:
        list = QtGui.QListWidget()
        list.setSelectionMode(QtGui.QAbstractItemView.SelectionMode.ExtendedSelection)
        self.root_layout.addWidget(list, 1, col)

        list.itemClicked.connect(handler1)
        list.itemDoubleClicked.connect(handler2)

        return list

    def _create_button(self, label, layout, handler):
        """Creates a button."""
        button = QtGui.QPushButton(label)
        # The connection type is set to workaround Qt5 + MacOSX issue with
        # event dispatching. See enthought/traitsui#1308
        button.clicked.connect(handler, type=QtCore.Qt.ConnectionType.QueuedConnection)
        layout.addWidget(button)
        return button

    def values_changed(self):
        """Recomputes the cached data based on the underlying enumeration model
        or the values of the factory.
        """
        (
            self._names,
            self._mapping,
            self._inverse_mapping,
        ) = enum_values_changed(self._value(), self.string_value)

    def _values_changed(self):
        """Handles the underlying object model's enumeration set or factory's
        values being changed.
        """
        self.values_changed()
        self.update_editor()

    def update_editor(self):
        """Updates the editor when the object trait changes externally to the
        editor.
        """
        # Check for any items having been deleted from the enumeration that are
        # still present in the object value:
        mapping = self.inverse_mapping.copy()
        values = [v for v in self.value if v in mapping]
        if len(values) < len(self.value):
            self.value = values

        # Get a list of the selected items in the right box:
        used = self._used
        used_labels = self._get_selected_strings(used)

        # Get a list of the selected items in the left box:
        unused = self._unused
        unused_labels = self._get_selected_strings(unused)

        # Empty list boxes in preparation for rebuilding from current values:
        used.clear()
        unused.clear()

        # Ensure right list box is kept alphabetized unless insertion
        # order is relevant:
        if not self.factory.ordered:
            values = sorted(values[:])

        # Rebuild the right listbox:
        used_selections = []
        for i, value in enumerate(values):
            label = mapping[value]
            used.addItem(label)
            del mapping[value]
            if label in used_labels:
                used_selections.append(i)

        # Rebuild the left listbox:
        unused_selections = []
        unused_items = sorted(mapping.values())
        mapping = self.mapping
        self._unused_items = [mapping[ui] for ui in unused_items]
        for i, unused_item in enumerate(unused_items):
            unused.addItem(unused_item)
            if unused_item in unused_labels:
                unused_selections.append(i)

        # If nothing is selected, default selection should be top of left box,
        # or of right box if left box is empty:
        if (len(used_selections) == 0) and (len(unused_selections) == 0):
            if unused.count() == 0:
                used_selections.append(0)
            else:
                unused_selections.append(0)

        used_count = used.count()
        for i in used_selections:
            if i < used_count:
                used.item(i).setSelected(True)

        unused_count = unused.count()
        for i in unused_selections:
            if i < unused_count:
                unused.item(i).setSelected(True)

        self._check_up_down()
        self._check_left_right()

    def dispose(self):
        """Disposes of the contents of an editor."""
        if self._object is not None:
            self._object.on_trait_change(
                self._values_changed, self._name, remove=True
            )
        else:
            self.factory.on_trait_change(
                self._values_changed, "values", remove=True
            )

        self.context_object.on_trait_change(
            self.update_editor, self.extended_name + "_items?", remove=True
        )

        super().dispose()

    def get_error_control(self):
        """Returns the editor's control for indicating error status."""
        return [self._unused, self._used]

    def _on_value(self):
        if not self.factory.ordered:
            self._unused.clearSelection()
        self._check_left_right()
        self._check_up_down()

    def _on_unused(self):
        if not self.factory.ordered:
            self._used.clearSelection()
        self._check_left_right()
        self._check_up_down()

    def _on_use(self):
        self._unused_items, self.value = self._transfer_items(
            self._unused, self._used, self._unused_items, self.value
        )

    def _on_unuse(self):
        self.value, self._unused_items = self._transfer_items(
            self._used, self._unused, self.value, self._unused_items
        )

    def _on_use_all(self):
        self._unused_items, self.value = self._transfer_all(
            self._unused, self._used, self._unused_items, self.value
        )

    def _on_unuse_all(self):
        self.value, self._unused_items = self._transfer_all(
            self._used, self._unused, self.value, self._unused_items
        )

    def _on_up(self):
        self._move_item(-1)

    def _on_down(self):
        self._move_item(1)

    def _transfer_all(self, list_from, list_to, values_from, values_to):
        """Transfers all items from one list to another."""
        values_from = values_from[:]
        values_to = values_to[:]

        list_from.clearSelection()
        while list_from.count() > 0:
            index_to = list_to.count()
            list_from.item(0).setSelected(True)
            list_to.insertItems(
                index_to, self._get_selected_strings(list_from)
            )
            list_from.takeItem(0)
            values_to.append(values_from[0])
            del values_from[0]

        list_to.item(0).setSelected(True)
        self._check_left_right()
        self._check_up_down()

        return (values_from, values_to)

    def _transfer_items(self, list_from, list_to, values_from, values_to):
        """Transfers the selected item from one list to another."""
        values_from = values_from[:]
        values_to = values_to[:]
        index_from = max(self._get_first_selection(list_from), 0)
        index_to = max(self._get_first_selection(list_to), 0)

        list_to.clearSelection()

        # Get the list of strings in the "from" box to be moved:
        selected_list = self._get_selected_strings(list_from)

        # fixme: I don't know why I have to reverse the list to get
        # correct behavior from the ordered list box.  Investigate -- LP
        selected_list.reverse()
        list_to.insertItems(index_to, selected_list)

        # Delete the transferred items from the left box:
        items_from = list_from.selectedItems()
        for i in range(len(items_from) - 1, -1, -1):
            list_from.takeItem(list_from.row(items_from[i]))
        del items_from

        # Delete the transferred items from the "unused" value list:
        for item_label in selected_list:
            val_index_from = values_from.index(self.mapping[item_label])
            values_to.insert(index_to, values_from[val_index_from])
            del values_from[val_index_from]

            # If right list is ordered, keep moved items selected:
            if self.factory.ordered:
                items = list_to.findItems(
                    item_label,
                    QtCore.Qt.MatchFlag.MatchFixedString | QtCore.Qt.MatchFlag.MatchCaseSensitive,
                )
                if items:
                    items[0].setSelected(True)

        # Reset the selection in the left box:
        count = list_from.count()
        if count > 0:
            if index_from >= count:
                index_from = count - 1
            list_from.item(index_from).setSelected(True)

        self._check_left_right()
        self._check_up_down()

        return (values_from, values_to)

    def _move_item(self, direction):
        """Moves an item up or down within the "used" list."""
        # Move the item up/down within the list:
        listbox = self._used
        index_from = self._get_first_selection(listbox)
        index_to = index_from + direction
        label = listbox.takeItem(index_from).text()
        listbox.insertItem(index_to, label)
        listbox.item(index_to).setSelected(True)

        # Enable the up/down buttons appropriately:
        self._check_up_down()

        # Move the item up/down within the editor's trait value:
        value = self.value
        if direction < 0:
            index = index_to
            values = [value[index_from], value[index_to]]
        else:
            index = index_from
            values = [value[index_to], value[index_from]]
        self.value = value[:index] + values + value[index + 2 :]

    def _check_up_down(self):
        """Sets the proper enabled state for the up and down buttons."""
        if self.factory.ordered:
            selected = self._used.selectedItems()
            self._up.setEnabled(
                len(selected) == 1 and selected[0] is not self._used.item(0)
            )
            self._down.setEnabled(
                len(selected) == 1
                and selected[0] is not self._used.item(self._used.count() - 1)
            )

    def _check_left_right(self):
        """Sets the proper enabled state for the left and right buttons."""
        self._use.setEnabled(
            self._unused.count() > 0
            and self._get_first_selection(self._unused) >= 0
        )
        self._unuse.setEnabled(
            self._used.count() > 0
            and self._get_first_selection(self._used) >= 0
        )

        if self.factory.can_move_all:
            self._use_all.setEnabled(
                self._unused.count() > 0
                and self._get_first_selection(self._unused) >= 0
            )
            self._unuse_all.setEnabled(
                self._used.count() > 0
                and self._get_first_selection(self._used) >= 0
            )

    # -------------------------------------------------------------------------
    # Returns a list of the selected strings in the listbox
    # -------------------------------------------------------------------------

    def _get_selected_strings(self, listbox):
        """Returns a list of the selected strings in the given *listbox*."""
        return [str(itm.text()) for itm in listbox.selectedItems()]

    # -------------------------------------------------------------------------
    # Returns the index of the first (or only) selected item.
    # -------------------------------------------------------------------------

    def _get_first_selection(self, listbox):
        """Returns the index of the first (or only) selected item."""
        select_list = listbox.selectedItems()
        if len(select_list) == 0:
            return -1

        return listbox.row(select_list[0])
