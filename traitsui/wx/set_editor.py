# (C) Copyright 2004-2023 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

""" Defines the set editors for the wxPython user interface toolkit.
"""

#  fixme: Add undo/redo support
#  fixme: Allow factory to handle a TraitListObject for the 'values' trait.

import wx

from traits.api import Property

from traitsui.helper import enum_values_changed

from .editor import Editor

from .helper import TraitsUIPanel


# -------------------------------------------------------------------------
#  'SimpleEditor' class:
# -------------------------------------------------------------------------


class SimpleEditor(Editor):
    """Simple style of editor for sets.

    The editor displays two list boxes, with buttons for moving the selected
    items from left to right, or vice versa. If **can_move_all** on the
    factory is True, then buttons are displayed for moving all the items to
    one box or the other. If the set is ordered, buttons are displayed for
    moving the selected item up or down in right-side list box.
    """

    # -------------------------------------------------------------------------
    #  Trait definitions:
    # -------------------------------------------------------------------------

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

        self.control = panel = TraitsUIPanel(parent, -1)
        hsizer = wx.BoxSizer(wx.HORIZONTAL)
        vsizer = wx.BoxSizer(wx.VERTICAL)

        self._unused = self._create_listbox(
            panel,
            hsizer,
            self._on_unused,
            self._on_use,
            factory.left_column_title,
        )

        self._use_all = self._unuse_all = self._up = self._down = None
        if factory.can_move_all:
            self._use_all = self._create_button(
                ">>", panel, vsizer, 15, self._on_use_all
            )

        self._use = self._create_button(">", panel, vsizer, 15, self._on_use)
        self._unuse = self._create_button(
            "<", panel, vsizer, 0, self._on_unuse
        )
        if factory.can_move_all:
            self._unuse_all = self._create_button(
                "<<", panel, vsizer, 15, self._on_unuse_all
            )

        if factory.ordered:
            self._up = self._create_button(
                "Move Up", panel, vsizer, 30, self._on_up
            )
            self._down = self._create_button(
                "Move Down", panel, vsizer, 0, self._on_down
            )

        hsizer.Add(vsizer, 0, wx.LEFT | wx.RIGHT, 8)
        self._used = self._create_listbox(
            panel,
            hsizer,
            self._on_value,
            self._on_unuse,
            factory.right_column_title,
        )

        panel.SetSizer(hsizer)

        self.context_object.on_trait_change(
            self.update_editor, self.extended_name + "_items?", dispatch="ui"
        )
        self.set_tooltip()

    def _get_names(self):
        """Gets the current set of enumeration names."""
        return self._names

    def _get_mapping(self):
        """Gets the current mapping."""
        return self._mapping

    def _get_inverse_mapping(self):
        """Gets the current inverse mapping."""
        return self._inverse_mapping

    def _create_listbox(self, parent, sizer, handler1, handler2, title):
        """Creates a list box."""
        column_sizer = wx.BoxSizer(wx.VERTICAL)

        # Add the column title in emphasized text:
        title_widget = wx.StaticText(parent, -1, title)
        font = title_widget.GetFont()
        emphasis_font = wx.Font(
            font.GetPointSize() + 1, font.GetFamily(), font.GetStyle(), wx.BOLD
        )
        title_widget.SetFont(emphasis_font)
        column_sizer.Add(title_widget, 0, 0)

        # Create the list box and add it to the column:
        list = wx.ListBox(parent, -1, style=wx.LB_EXTENDED | wx.LB_NEEDED_SB)
        column_sizer.Add(list, 1, wx.EXPAND)

        # Add the column to the SetEditor widget:
        sizer.Add(column_sizer, 1, wx.EXPAND)

        # Hook up the event handlers:
        parent.Bind(wx.EVT_LISTBOX, handler1, id=list.GetId())
        parent.Bind(wx.EVT_LISTBOX_DCLICK, handler2, id=list.GetId())

        return list

    def _create_button(self, label, parent, sizer, space_before, handler):
        """Creates a button."""
        button = wx.Button(parent, -1, label, style=wx.BU_EXACTFIT)
        sizer.AddSpacer(space_before)
        sizer.Add(button, 0, wx.EXPAND | wx.BOTTOM, 8)
        parent.Bind(wx.EVT_BUTTON, handler, id=button.GetId())
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
            return

        # Get a list of the selected items in the right box:
        used = self._used
        used_labels = self._get_selected_strings(used)

        # Get a list of the selected items in the left box:
        unused = self._unused
        unused_labels = self._get_selected_strings(unused)

        # Empty list boxes in preparation for rebuilding from current values:
        used.Clear()
        unused.Clear()

        # Ensure right list box is kept alphabetized unless insertion
        # order is relevant:
        if not self.factory.ordered:
            values = sorted(values[:])

        # Rebuild the right listbox:
        used_selections = []
        for i, value in enumerate(values):
            label = mapping[value]
            used.Append(label)
            del mapping[value]
            if label in used_labels:
                used_selections.append(i)

        # Rebuild the left listbox:
        unused_selections = []
        unused_items = sorted(mapping.values())
        mapping = self.mapping
        self._unused_items = [mapping[ui] for ui in unused_items]
        for i, unused_item in enumerate(unused_items):
            unused.Append(unused_item)
            if unused_item in unused_labels:
                unused_selections.append(i)

        # If nothing is selected, default selection should be top of left box,
        # or of right box if left box is empty:
        if (len(used_selections) == 0) and (len(unused_selections) == 0):
            if unused.GetCount() == 0:
                used_selections.append(0)
            else:
                unused_selections.append(0)

        used_count = used.GetCount()
        for i in used_selections:
            if i < used_count:
                used.SetSelection(i)

        unused_count = unused.GetCount()
        for i in unused_selections:
            if i < unused_count:
                unused.SetSelection(i)

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

    # -------------------------------------------------------------------------
    #  Event handlers:
    # -------------------------------------------------------------------------

    def _on_value(self, event):
        if not self.factory.ordered:
            self._clear_selection(self._unused)
        self._check_left_right()
        self._check_up_down()

    def _on_unused(self, event):
        if not self.factory.ordered:
            self._clear_selection(self._used)
        self._check_left_right()
        self._check_up_down()

    def _on_use(self, event):
        self._unused_items, self.value = self._transfer_items(
            self._unused, self._used, self._unused_items, self.value
        )

    def _on_unuse(self, event):
        self.value, self._unused_items = self._transfer_items(
            self._used, self._unused, self.value, self._unused_items
        )

    def _on_use_all(self, event):
        self._unused_items, self.value = self._transfer_all(
            self._unused, self._used, self._unused_items, self.value
        )

    def _on_unuse_all(self, event):
        self.value, self._unused_items = self._transfer_all(
            self._used, self._unused, self.value, self._unused_items
        )

    def _on_up(self, event):
        self._move_item(-1)

    def _on_down(self, event):
        self._move_item(1)

    # -------------------------------------------------------------------------
    #  Private methods:
    # -------------------------------------------------------------------------

    # -------------------------------------------------------------------------
    # Unselects all items in the given ListBox
    # -------------------------------------------------------------------------

    def _clear_selection(self, box):
        """Unselects all items in the given ListBox"""
        for i in box.GetSelections():
            box.Deselect(i)

    def _transfer_all(self, list_from, list_to, values_from, values_to):
        """Transfers all items from one list to another."""
        values_from = values_from[:]
        values_to = values_to[:]

        self._clear_selection(list_from)
        while list_from.GetCount() > 0:
            index_to = list_to.GetCount()
            list_from.SetSelection(0)
            list_to.InsertItems(
                self._get_selected_strings(list_from), index_to
            )
            list_from.Delete(0)
            values_to.append(values_from[0])
            del values_from[0]

        list_to.SetSelection(0)
        self._check_left_right()
        self._check_up_down()

        return (values_from, values_to)

    def _transfer_items(self, list_from, list_to, values_from, values_to):
        """Transfers the selected item from one list to another."""
        values_from = values_from[:]
        values_to = values_to[:]
        indices_from = list_from.GetSelections()
        index_from = max(self._get_first_selection(list_from), 0)
        index_to = max(self._get_first_selection(list_to), 0)

        self._clear_selection(list_to)

        # Get the list of strings in the "from" box to be moved:
        selected_list = self._get_selected_strings(list_from)

        # fixme: I don't know why I have to reverse the list to get
        # correct behavior from the ordered list box.  Investigate -- LP
        selected_list.reverse()
        list_to.InsertItems(selected_list, index_to)

        # Delete the transferred items from the left box:
        for i in range(len(indices_from) - 1, -1, -1):
            list_from.Delete(indices_from[i])

        # Delete the transferred items from the "unused" value list:
        for item_label in selected_list:
            val_index_from = values_from.index(self.mapping[item_label])
            values_to.insert(index_to, values_from[val_index_from])
            del values_from[val_index_from]

            # If right list is ordered, keep moved items selected:
            if self.factory.ordered:
                list_to.SetSelection(list_to.FindString(item_label))

        # Reset the selection in the left box:
        count = list_from.GetCount()
        if count > 0:
            if index_from >= count:
                index_from -= 1
            list_from.SetSelection(index_from)

        self._check_left_right()
        self._check_up_down()

        return (values_from, values_to)

    def _move_item(self, direction):
        """Moves an item up or down within the "used" list."""
        # Move the item up/down within the list:
        listbox = self._used
        index_from = self._get_first_selection(listbox)
        index_to = index_from + direction
        label = listbox.GetString(index_from)
        listbox.Deselect(index_from)
        listbox.Delete(index_from)
        listbox.Insert(label, index_to)
        listbox.SetSelection(index_to)

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
            index_selected = self._used.GetSelections()
            self._up.Enable(
                (len(index_selected) == 1) and (index_selected[0] > 0)
            )
            self._down.Enable(
                (len(index_selected) == 1)
                and (index_selected[0] < (self._used.GetCount() - 1))
            )

    def _check_left_right(self):
        """Sets the proper enabled state for the left and right buttons."""
        self._use.Enable(
            self._unused.GetCount() > 0
            and self._get_first_selection(self._unused) >= 0
        )
        self._unuse.Enable(
            self._used.GetCount() > 0
            and self._get_first_selection(self._used) >= 0
        )

        if self.factory.can_move_all:
            self._use_all.Enable(
                (self._unused.GetCount() > 0)
                and (self._get_first_selection(self._unused) >= 0)
            )
            self._unuse_all.Enable(
                (self._used.GetCount() > 0)
                and (self._get_first_selection(self._used) >= 0)
            )

    # -------------------------------------------------------------------------
    # Returns a list of the selected strings in the listbox
    # -------------------------------------------------------------------------

    def _get_selected_strings(self, listbox):
        """Returns a list of the selected strings in the given *listbox*."""
        stringlist = []
        for label_index in listbox.GetSelections():
            stringlist.append(listbox.GetString(label_index))

        return stringlist

    # -------------------------------------------------------------------------
    # Returns the index of the first (or only) selected item.
    # -------------------------------------------------------------------------

    def _get_first_selection(self, listbox):
        """Returns the index of the first (or only) selected item."""
        select_list = listbox.GetSelections()
        if len(select_list) == 0:
            return -1

        return select_list[0]
