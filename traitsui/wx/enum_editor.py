# (C) Copyright 2004-2023 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

""" Defines the various editors for single-selection enumerations, for the
wxPython user interface toolkit.
"""


import wx

from traits.api import Property

from traitsui.helper import enum_values_changed

from .editor import Editor

from .constants import OKColor, ErrorColor

from .helper import (
    TraitsUIPanel,
    disconnect,
    disconnect_no_id,
)
from functools import reduce

# -------------------------------------------------------------------------
#  'BaseEditor' class:
# -------------------------------------------------------------------------


class BaseEditor(Editor):
    """Base class for enumeration editors."""

    # -------------------------------------------------------------------------
    #  Trait definitions:
    # -------------------------------------------------------------------------

    #: Current set of enumeration names:
    names = Property()

    #: Current mapping from names to values:
    mapping = Property()

    #: Current inverse mapping from values to names:
    inverse_mapping = Property()

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
                self._values_changed, " " + self._name, dispatch="ui"
            )
        else:
            self._value = lambda: self.factory.values
            self.values_changed()
            factory.on_trait_change(
                self._values_changed, "values", dispatch="ui"
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

    def rebuild_editor(self):
        """Rebuilds the contents of the editor whenever the original factory
        object's **values** trait changes.
        """
        raise NotImplementedError

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
        self.rebuild_editor()

    def dispose(self):
        """Disposes of the contents of an editor."""
        if self._object is not None:
            self._object.on_trait_change(
                self._values_changed, " " + self._name, remove=True
            )
        else:
            self.factory.on_trait_change(
                self._values_changed, "values", remove=True
            )

        super().dispose()


# -------------------------------------------------------------------------
#  'SimpleEditor' class:
# -------------------------------------------------------------------------


class SimpleEditor(BaseEditor):
    """Simple style of enumeration editor, which displays a combo box."""

    def init(self, parent):
        """Finishes initializing the editor by creating the underlying toolkit
        widget.
        """
        super().init(parent)

        factory = self.factory

        if factory.evaluate is None:
            self.control = control = wx.Choice(
                parent, -1, wx.Point(0, 0), wx.Size(-1, -1), self.names
            )
            parent.Bind(
                wx.EVT_CHOICE, self.update_object, id=self.control.GetId()
            )
        else:
            self.control = control = wx.ComboBox(
                parent,
                -1,
                "",
                wx.Point(0, 0),
                wx.Size(-1, -1),
                self.names,
                style=wx.CB_DROPDOWN,
            )
            parent.Bind(
                wx.EVT_COMBOBOX, self.update_object, id=control.GetId()
            )
            parent.Bind(
                wx.EVT_TEXT_ENTER, self.update_text_object, id=control.GetId()
            )
            control.Bind(wx.EVT_KILL_FOCUS, self.on_kill_focus)

            if (not factory.is_grid_cell) and factory.auto_set:
                parent.Bind(
                    wx.EVT_TEXT, self.update_text_object, id=control.GetId()
                )

        self._no_enum_update = 0
        self.set_tooltip()

    def dispose(self):
        """Disposes of the contents of an editor."""
        disconnect(
            self.control, wx.EVT_COMBOBOX, wx.EVT_TEXT_ENTER, wx.EVT_TEXT
        )

        disconnect_no_id(self.control, wx.EVT_KILL_FOCUS)

        super().dispose()

    def update_object(self, event):
        """Handles the user selecting a new value from the combo box."""
        self._no_enum_update += 1
        try:
            new_value = self.mapping[event.GetString()]
            if new_value == self.value and self.factory.is_grid_cell:
                # If the enum editor is in a grid cell and the value did not
                # change, we want the enum editor to go away, reverting back to
                # the normal cell appearance. This is for 2 reasons:
                #  1. it looks nicer
                #  2. if the grid id suddenly closed, wx freaks & causes a
                #     segfault

                grid = self.control.Parent.Parent
                grid.EnableEditing(False)
                grid.EnableEditing(True)

            self.value = new_value

        except:
            from traitsui.api import raise_to_debug

            raise_to_debug()

        self._no_enum_update -= 1

    def update_text_object(self, event):
        """Handles the user typing text into the combo box text entry field."""
        if self._no_enum_update == 0:
            value = self.control.GetValue()
            try:
                value = self.mapping[value]
            except:
                try:
                    value = self.factory.evaluate(value)
                except Exception as excp:
                    self.error(excp)
                    return

            self._no_enum_update += 1
            try:
                self.value = value
                self.control.SetBackgroundColour(OKColor)
                self.control.Refresh()
            except:
                pass
            self._no_enum_update -= 1

    def on_kill_focus(self, event):
        """Handles the control losing the keyboard focus."""
        self.update_text_object(event)
        event.Skip()

    def update_editor(self):
        """Updates the editor when the object trait changes externally to the
        editor.
        """
        if self._no_enum_update == 0:
            if self.factory.evaluate is None:
                try:
                    self.control.SetStringSelection(
                        self.inverse_mapping[self.value]
                    )
                except:
                    pass
            else:
                try:
                    self.control.SetValue(self.str_value)
                except:
                    pass

    def error(self, excp):
        """Handles an error that occurs while setting the object's trait value."""
        self.control.SetBackgroundColour(ErrorColor)
        self.control.Refresh()

    def rebuild_editor(self):
        """Rebuilds the contents of the editor whenever the original factory
        object's **values** trait changes.
        """
        # Note: This code is unnecessarily complex due to a strange bug in
        # wxWidgets implementation of the wx.Combobox control that has strange
        # behavior when the current text field value is one of the selection
        # values when 'Clear' is called. In this case, even saving and
        # restoring the text field value does not work, so we go to great
        # lengths to detect this case and avoid using 'Clear', but still get
        # the equivalent visual results. Modify this code at your own risk...

        control = self.control
        clear = True
        cur_name = None
        if self.factory.evaluate is not None:
            n = control.GetCount()
            cur_names = [control.GetString(i) for i in range(n)]
            cur_name = control.GetValue()
            if cur_name in self.names:
                clear = False
                include = True
                for i in range(n - 1, -1, -1):
                    if cur_name == cur_names[i]:
                        include = False
                    else:
                        control.Delete(i)
                for name in self.names:
                    if include or (name != cur_name):
                        control.Append(name)
                cur_name = None
            else:
                point = control.GetInsertionPoint()

        if clear:
            control.Clear()
            control.AppendItems(self.names)

        if cur_name is not None:
            self._no_enum_update += 1
            control.SetValue(cur_name)
            control.SetInsertionPoint(point)
            self._no_enum_update -= 1

        self.update_editor()


class RadioEditor(BaseEditor):
    """Enumeration editor, used for the "custom" style, that displays radio
    buttons.
    """

    def init(self, parent):
        """Finishes initializing the editor by creating the underlying toolkit
        widget.
        """
        super().init(parent)

        # Create a panel to hold all of the radio buttons:
        self.control = TraitsUIPanel(parent, -1)
        self.rebuild_editor()

    def update_object(self, event):
        """Handles the user clicking one of the custom radio buttons."""
        try:
            self.value = event.GetEventObject().value
        except:
            pass

    def update_editor(self):
        """Updates the editor when the object trait changes externally to the
        editor.
        """
        value = self.value
        for button in self.control.GetChildren():
            state = button.value == value
            button.SetValue(state)
            if state:
                button.SetFocus()

    def rebuild_editor(self):
        """Rebuilds the contents of the editor whenever the original factory
        object's **values** trait changes.
        """
        # Clear any existing content:
        panel = self.control
        panel.SetSizer(None)
        panel.DestroyChildren()

        # Get the current trait value:
        cur_name = self.str_value

        # Create a sizer to manage the radio buttons:
        names = self.names
        mapping = self.mapping
        n = len(names)
        cols = self.factory.cols
        rows = (n + cols - 1) // cols
        # incr will keep track of how to increment index so that as we traverse
        # the grid in row major order, the elements are added to appear in
        # column major order
        incr = [n // cols] * cols
        rem = n % cols
        for i in range(cols):
            incr[i] += rem > i
        incr[-1] = -(reduce(lambda x, y: x + y, incr[:-1], 0) - 1)
        # e.g for a gird:
        # 0 2 4
        # 1 3 5
        # incr should be [2, 2, -3]
        if cols > 1:
            sizer = wx.GridSizer(0, cols, 2, 4)
        else:
            sizer = wx.BoxSizer(wx.VERTICAL)

        # Add the set of all possible choices:
        style = wx.RB_GROUP
        index = 0
        # populate the layout in row_major order
        for i in range(rows):
            for j in range(cols):
                if n > 0:
                    name = label = names[index]
                    label = self.string_value(label, str.capitalize)
                    control = wx.RadioButton(panel, -1, label, style=style)
                    control.value = mapping[name]
                    style = 0
                    control.SetValue(name == cur_name)
                    panel.Bind(
                        wx.EVT_RADIOBUTTON,
                        self.update_object,
                        id=control.GetId(),
                    )
                    self.set_tooltip(control)
                    index += incr[j]
                    n -= 1
                else:
                    control = wx.RadioButton(panel, -1, "")
                    control.value = ""
                    control.Show(False)
                sizer.Add(control, 0, wx.NORTH, 5)

        # Set-up the layout:
        panel.SetSizerAndFit(sizer)


class ListEditor(BaseEditor):
    """Enumeration editor, used for the "custom" style, that displays a list
    box.
    """

    def init(self, parent):
        """Finishes initializing the editor by creating the underlying toolkit
        widget.
        """
        super().init(parent)

        # Create a panel to hold all of the radio buttons:
        self.control = wx.ListBox(
            parent,
            -1,
            wx.Point(0, 0),
            wx.Size(-1, -1),
            self.names,
            style=wx.LB_SINGLE | wx.LB_NEEDED_SB,
        )
        parent.Bind(
            wx.EVT_LISTBOX, self.update_object, id=self.control.GetId()
        )
        self.set_tooltip()

    def dispose(self):
        """Disposes of the contents of an editor."""
        disconnect(self.control, wx.EVT_LISTBOX)

        super().dispose()

    def update_object(self, event):
        """Handles the user selecting a list box item."""
        if not self._ignore_update:
            value = self.control.GetStringSelection()
            try:
                value = self.mapping[value]
            except:
                try:
                    value = self.factory.evaluate(value)
                except:
                    pass
            try:
                self.value = value
            except:
                pass

    def update_editor(self):
        """Updates the editor when the object trait changes externally to the
        editor.
        """
        control = self.control
        try:
            index = control.FindString(self.inverse_mapping[self.value])
            if index >= 0:
                control.SetSelection(index)
        except:
            pass

    def rebuild_editor(self):
        """Rebuilds the contents of the editor whenever the original factory
        object's **values** trait changes.
        """
        self._ignore_update = True
        self.control.Clear()
        self.control.AppendItems(self.names)
        self._ignore_update = False

        # fixme: Is this line necessary?
        self.update_editor()
