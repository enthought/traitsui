# (C) Copyright 2004-2022 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

""" Defines the various instance editors for the wxPython user interface
toolkit.
"""


import wx

from pyface.wx.drag_and_drop import PythonDropTarget
from traits.api import HasTraits, Instance, Property

from traitsui.ui_traits import AView
from traitsui.helper import user_name_for
from traitsui.handler import Handler
from traitsui.instance_choice import InstanceChoiceItem

from . import toolkit
from .editor import Editor
from .constants import DropColor
from .helper import TraitsUIPanel, position_window


OrientationMap = {
    "default": None,
    "horizontal": wx.HORIZONTAL,
    "vertical": wx.VERTICAL,
}

# -------------------------------------------------------------------------
#  'CustomEditor' class:
# -------------------------------------------------------------------------


class CustomEditor(Editor):
    """Custom style of editor for instances. If selection among instances is
    allowed, the editor displays a combo box listing instances that can be
    selected. If the current instance is editable, the editor displays a panel
    containing trait editors for all the instance's traits.
    """

    #: Background color when an item can be dropped on the editor:
    ok_color = DropColor

    #: The orientation of the instance editor relative to the instance selector:
    orientation = wx.VERTICAL

    #: Class constant:
    extra = 0

    # -------------------------------------------------------------------------
    #  Trait definitions:
    # -------------------------------------------------------------------------

    #: List of InstanceChoiceItem objects used by the editor
    items = Property()

    #: The maximum extra padding that should be allowed around the editor:
    #: (Override of the Editor base class trait)
    border_size = 0

    #: The view to use for displaying the instance:
    view = AView

    def init(self, parent):
        """Finishes initializing the editor by creating the underlying toolkit
        widget.
        """
        factory = self.factory
        if factory.name != "":
            self._object, self._name, self._value = self.parse_extended_name(
                factory.name
            )

        # Create a panel to hold the object trait's view:
        if factory.editable:
            self.control = self._panel = parent = TraitsUIPanel(parent, -1)

        # Build the instance selector if needed:
        selectable = factory.selectable
        droppable = factory.droppable
        items = self.items
        for item in items:
            droppable |= item.is_droppable()
            selectable |= item.is_selectable()

        if selectable:
            self._object_cache = {}
            item = self.item_for(self.value)
            if item is not None:
                self._object_cache[id(item)] = self.value

            self._choice = choice = wx.Choice(
                parent, -1, wx.Point(0, 0), wx.Size(-1, -1), []
            )
            choice.Bind(wx.EVT_CHOICE, self.update_object, id=choice.GetId())
            if droppable:
                self._choice.SetBackgroundColour(self.ok_color)

            self.set_tooltip(self._choice)

            if factory.name != "":
                self._object.on_trait_change(
                    self.rebuild_items, self._name, dispatch="ui"
                )
                self._object.on_trait_change(
                    self.rebuild_items, self._name + "_items", dispatch="ui"
                )

            factory.on_trait_change(
                self.rebuild_items, "values", dispatch="ui"
            )
            factory.on_trait_change(
                self.rebuild_items, "values_items", dispatch="ui"
            )

            self.rebuild_items()

        elif droppable:
            self._choice = wx.TextCtrl(parent, -1, "", style=wx.TE_READONLY)
            self._choice.SetBackgroundColour(self.ok_color)
            self.set_tooltip(self._choice)

        if droppable:
            self._choice.SetDropTarget(PythonDropTarget(self))

        orientation = OrientationMap[factory.orientation]
        if orientation is None:
            orientation = self.orientation

        if (selectable or droppable) and factory.editable:
            sizer = wx.BoxSizer(orientation)
            sizer.Add(self._choice, self.extra, wx.EXPAND)
            if orientation == wx.VERTICAL:
                sizer.Add(
                    wx.StaticLine(parent, -1, style=wx.LI_HORIZONTAL),
                    0,
                    wx.EXPAND | wx.TOP | wx.BOTTOM,
                    5,
                )
            self.create_editor(parent, sizer)
            parent.SetSizer(sizer)
        elif self.control is None:
            if self._choice is None:
                self._choice = choice = wx.Choice(
                    parent, -1, wx.Point(0, 0), wx.Size(-1, -1), []
                )
                choice.Bind(
                    wx.EVT_CHOICE, self.update_object, id=choice.GetId()
                )
            self.control = self._choice
        else:
            sizer = wx.BoxSizer(orientation)
            self.create_editor(parent, sizer)
            parent.SetSizer(sizer)

        # Synchronize the 'view' to use:
        # fixme: A normal assignment can cause a crash (for unknown reasons) in
        # some cases, so we make sure that no notifications are generated:
        self.trait_setq(view=factory.view)
        self.sync_value(factory.view_name, "view", "from")

    def dispose(self):
        """Disposes of the contents of an editor."""
        # Make sure we aren't hanging on to any object refs:
        self._object_cache = None

        if self._ui is not None:
            self._ui.dispose()

        choice = self._choice
        if choice is not None:
            if isinstance(choice, wx.Choice):
                choice.Bind(wx.EVT_CHOICE, None, id=choice.GetId())

            if self._object is not None:
                self._object.on_trait_change(
                    self.rebuild_items, self._name, remove=True
                )
                self._object.on_trait_change(
                    self.rebuild_items, self._name + "_items", remove=True
                )

            self.factory.on_trait_change(
                self.rebuild_items, "values", remove=True
            )
            self.factory.on_trait_change(
                self.rebuild_items, "values_items", remove=True
            )

        super().dispose()

    def create_editor(self, parent, sizer):
        """Creates the editor control."""
        self._panel = TraitsUIPanel(parent, -1)
        sizer.Add(self._panel, 1, wx.EXPAND)

    def _get_items(self):
        """Gets the current list of InstanceChoiceItem items."""
        if self._items is not None:
            return self._items

        factory = self.factory
        if self._value is not None:
            values = self._value() + factory.values
        else:
            values = factory.values

        items = []
        adapter = factory.adapter
        for value in values:
            if not isinstance(value, InstanceChoiceItem):
                value = adapter(object=value)
            items.append(value)

        self._items = items

        return items

    def rebuild_items(self):
        """Rebuilds the object selector list."""
        # Clear the current cached values:
        self._items = None

        # Rebuild the contents of the selector list:
        name = None
        value = self.value
        choice = self._choice
        choice.Clear()
        for item in self.items:
            if item.is_selectable():
                item_name = item.get_name()
                choice.Append(item_name)
                if item.is_compatible(value):
                    name = item_name

        # Reselect the current item if possible:
        if name is not None:
            choice.SetStringSelection(name)
        else:
            # Otherwise, current value is no longer valid, try to discard it:
            try:
                self.value = None
            except:
                pass

    def item_for(self, object):
        """Returns the InstanceChoiceItem for a specified object."""
        for item in self.items:
            if item.is_compatible(object):
                return item

        return None

    def view_for(self, object, item):
        """Returns the view to use for a specified object."""
        view = ""
        if item is not None:
            view = item.get_view()

        if view == "":
            view = self.view

        return self.ui.handler.trait_view_for(
            self.ui.info, view, object, self.object_name, self.name
        )

    def update_object(self, event):
        """Handles the user selecting a new value from the combo box."""
        name = event.GetString()
        for item in self.items:
            if name == item.get_name():
                id_item = id(item)
                object = self._object_cache.get(id_item)
                if object is None:
                    object = item.get_object()
                    if (not self.factory.editable) and item.is_factory:
                        view = self.view_for(object, self.item_for(object))
                        view.ui(object, self.control, "modal")

                    if self.factory.cachable:
                        self._object_cache[id_item] = object

                self.value = object
                self.resynch_editor()
                break

    def update_editor(self):
        """Updates the editor when the object trait changes externally to the
        editor.
        """
        # Attach the current object value to the control (for use by
        # DockWindowFeature):

        # fixme: This code is somewhat fragile since it assumes that if a
        # DockControl is involved, the parent of this editor will be the
        # control being managed by the DockControl.
        parent = self.control.GetParent()
        parent._object = self.value
        dock_control = getattr(parent, "_dock_control", None)
        if dock_control is not None:
            dock_control.reset_tab()

        # Synchronize the editor contents:
        self.resynch_editor()

        # Update the selector (if any):
        choice = self._choice
        item = self.item_for(self.value)
        if (choice is not None) and (item is not None):
            name = item.get_name(self.value)
            if self._object_cache is not None:
                if choice.FindString(name) < 0:
                    choice.Append(name)
                choice.SetStringSelection(name)
            else:
                choice.SetValue(name)

    def resynch_editor(self):
        """Resynchronizes the contents of the editor when the object trait
        changes externally to the editor.
        """
        panel = self._panel
        if panel is not None:
            # Compute/update the maximum size the panel has ever been:
            dx, dy = panel.GetSize()
            mdx = mdy = 0
            if self._panel_size is not None:
                mdx, mdy = self._panel_size
            self._panel_size = size = wx.Size(max(mdx, dx), max(mdy, dy))

            # Dispose of the previous contents of the panel:
            panel.SetSizer(None)
            if self._ui is not None:
                self._ui.dispose()
                self._ui = None
            else:
                for child in panel.GetChildren():
                    toolkit.destroy_control(child)

            # Create the new content for the panel:
            sizer = wx.BoxSizer(wx.VERTICAL)
            stretch = 0
            value = self.value
            if not isinstance(value, HasTraits):
                str_value = ""
                if value is not None:
                    str_value = self.str_value
                control = wx.StaticText(panel, -1, str_value)
            else:
                view = self.view_for(value, self.item_for(value))
                context = value.trait_context()
                handler = None
                if isinstance(value, Handler):
                    handler = value
                context.setdefault("context", self.object)
                context.setdefault("context_handler", self.ui.handler)
                self._ui = ui = view.ui(
                    context,
                    panel,
                    "subpanel",
                    value.trait_view_elements(),
                    handler,
                    self.factory.id,
                )
                control = ui.control
                self.scrollable = ui._scrollable
                ui.parent = self.ui

                if view.resizable or view.scrollable or ui._scrollable:
                    stretch = 1

            # Make sure the panel and its contents are correctly sized (This
            # code is complicated by the various layout bugs present in wx.
            # Tamper with it at your own risk!):
            control.Freeze()
            if stretch and (size != (20, 20)):
                control.SetSize(size)
                panel.SetSize(size)
            else:
                panel.SetSize(control.GetSize())
            sizer.Add(control, stretch, wx.EXPAND)
            panel.SetSizer(sizer)
            control.Thaw()
            self.control.Layout()
            parent = self.control.GetParent()
            parent.Layout()

            # It is possible that this instance editor is embedded at some level
            # in a ScrolledWindow. If so, we need to inform the window that the
            # size of the editor's contents have (potentially) changed:
            while (parent is not None) and (
                not isinstance(parent, wx.ScrolledWindow)
            ):
                parent = parent.GetParent()

            if parent is not None:
                parent.SendSizeEvent()

    def error(self, excp):
        """Handles an error that occurs while setting the object's trait value."""
        pass

    def get_error_control(self):
        """Returns the editor's control for indicating error status."""
        return self._choice or self.control

    # -- UI preference save/restore interface ---------------------------------

    def restore_prefs(self, prefs):
        """Restores any saved user preference information associated with the
        editor.
        """
        ui = self._ui
        if (ui is not None) and (prefs.get("id") == ui.id):
            ui.set_prefs(prefs.get("prefs"))

    def save_prefs(self):
        """Returns any user preference information associated with the editor."""
        ui = self._ui
        if (ui is not None) and (ui.id != ""):
            return {"id": ui.id, "prefs": ui.get_prefs()}

        return None

    # -- Drag and drop event handlers -----------------------------------------

    def wx_dropped_on(self, x, y, data, drag_result):
        """Handles a Python object being dropped on the tree."""
        for item in self.items:
            if item.is_droppable() and item.is_compatible(data):
                if self._object_cache is not None:
                    self.rebuild_items()
                self.value = data
                return drag_result

        return wx.DragNone

    def wx_drag_over(self, x, y, data, drag_result):
        """Handles a Python object being dragged over the tree."""
        for item in self.items:
            if item.is_droppable() and item.is_compatible(data):
                return drag_result

        return wx.DragNone

    # -- Traits event handlers ------------------------------------------------

    def _view_changed(self, view):
        self.resynch_editor()


class SimpleEditor(CustomEditor):
    """Simple style of editor for instances, which displays a button. Clicking
    the button displays a dialog box in which the instance can be edited.
    """

    #: Class constants:
    orientation = wx.HORIZONTAL
    extra = 2

    #: The ui instance for the currently open editor dialog
    _dialog_ui = Instance("traitsui.ui.UI")

    def create_editor(self, parent, sizer):
        """Creates the editor control (a button)."""
        self._button = button = wx.Button(parent, -1, "")
        sizer.Add(button, 1, wx.EXPAND | wx.LEFT, 5)
        button.Bind(wx.EVT_BUTTON, self.edit_instance, id=button.GetId())

    def dispose(self):
        """Disposes of the contents of an editor."""
        button = self._button
        if button is not None:
            button.Bind(wx.EVT_BUTTON, None, id=button.GetId())

        if self._dialog_ui is not None:
            self._dialog_ui.dispose()
            self._dialog_ui = None

        super().dispose()

    def edit_instance(self, event):
        """Edit the contents of the object trait when the user clicks the
        button.
        """
        # Create the user interface:
        factory = self.factory
        view = self.ui.handler.trait_view_for(
            self.ui.info, factory.view, self.value, self.object_name, self.name
        )
        ui = self.value.edit_traits(
            view, self.control, factory.kind, id=factory.id
        )

        # Check to see if the view was 'modal', in which case it will already
        # have been closed (i.e. is None) by the time we get control back:
        if ui.control is not None:
            # Position the window on the display:
            position_window(ui.control)

            # Chain our undo history to the new user interface if it does not
            # have its own:
            if ui.history is None:
                ui.history = self.ui.history
        self._dialog_ui = ui

    def resynch_editor(self):
        """Resynchronizes the contents of the editor when the object trait
        changes externally to the editor.
        """
        button = self._button
        if button is not None:
            label = self.factory.label
            if label == "":
                label = user_name_for(self.name)
            button.SetLabel(label)
            button.Enable(isinstance(self.value, HasTraits))
