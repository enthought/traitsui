# (C) Copyright 2009-2023 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

# ------------------------------------------------------------------------------
# Copyright (c) 2008, Riverbank Computing Limited
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD license.
# However, when used with the GPL version of PyQt the additional terms
# described in the PyQt GPL exception also apply

#
# Author: Riverbank Computing Limited
# ------------------------------------------------------------------------------

""" Defines the various instance editors and the instance editor factory for
    the PyQt user interface toolkit..
"""


from pyface.qt import QtCore, QtGui

from traits.api import HasTraits, Instance, Property
from traits.observation.api import trait

from traitsui.ui_traits import AView
from traitsui.helper import user_name_for
from traitsui.handler import Handler
from traitsui.instance_choice import InstanceChoice, InstanceChoiceItem
from .editor import Editor
from .drop_editor import _DropEventFilter
from .constants import DropColor
from .helper import position_window


OrientationMap = {
    "default": None,
    "horizontal": QtGui.QBoxLayout.Direction.LeftToRight,
    "vertical": QtGui.QBoxLayout.Direction.TopToBottom,
}


class CustomEditor(Editor):
    """Custom style of editor for instances. If selection among instances is
    allowed, the editor displays a combo box listing instances that can be
    selected. If the current instance is editable, the editor displays a panel
    containing trait editors for all the instance's traits.
    """

    #: Background color when an item can be dropped on the editor:
    ok_color = DropColor

    #: The orientation of the instance editor relative to the instance selector:
    orientation = QtGui.QBoxLayout.Direction.TopToBottom

    #: Class constant:
    extra = 0

    # -------------------------------------------------------------------------
    #  Trait definitions:
    # -------------------------------------------------------------------------

    #: List of InstanceChoiceItem objects used by the editor
    items = Property()

    #: The view to use for displaying the instance
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
            self.control = self._panel = parent = QtGui.QWidget()

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

            self._choice = QtGui.QComboBox()
            self._choice.activated.connect(self.update_object)

            self.set_tooltip(self._choice)

            if factory.name != "":
                self._object.observe(
                    self.rebuild_items, self._name + ".items", dispatch="ui"
                )

            factory.observe(self.rebuild_items, "values.items", dispatch="ui")

            self.rebuild_items()

        elif droppable:
            self._choice = QtGui.QLineEdit()
            self._choice.setReadOnly(True)
            self.set_tooltip(self._choice)

        orientation = OrientationMap[factory.orientation]
        if orientation is None:
            orientation = self.orientation

        if (selectable or droppable) and factory.editable:
            layout = QtGui.QBoxLayout(orientation, parent)
            layout.setContentsMargins(0, 0, 0, 0)
            layout.addWidget(self._choice)

            if orientation == QtGui.QBoxLayout.Direction.TopToBottom:
                hline = QtGui.QFrame()
                hline.setFrameShape(QtGui.QFrame.Shape.HLine)
                hline.setFrameShadow(QtGui.QFrame.Shadow.Sunken)

                layout.addWidget(hline)

            self.create_editor(parent, layout)
        elif self.control is None:
            if self._choice is None:
                self._choice = QtGui.QComboBox()
                self._choice.activated[int].connect(self.update_object)

            self.control = self._choice
        else:
            layout = QtGui.QBoxLayout(orientation, parent)
            layout.setContentsMargins(0, 0, 0, 0)
            self.create_editor(parent, layout)

        if droppable:
            # Install EventFilter on control to handle DND events.
            drop_event_filter = _DropEventFilter(self.control)
            self.control.installEventFilter(drop_event_filter)

        # Synchronize the 'view' to use:
        # fixme: A normal assignment can cause a crash (for unknown reasons) in
        # some cases, so we make sure that no notifications are generated:
        self.trait_setq(view=factory.view)
        self.sync_value(factory.view_name, "view", "from")

    def create_editor(self, parent, layout):
        """Creates the editor control."""
        self._panel = QtGui.QWidget()
        layout.addWidget(self._panel)

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
            # rebuild_items when an item's name changes so it is reflected by
            # combobox. This change was added to fix enthought/traitsui#1641
            if isinstance(value, InstanceChoice):
                value.object.observe(
                    self.rebuild_items,
                    trait(value.name_trait, optional=True),
                    dispatch="ui",
                )
            items.append(value)

        self._items = items

        return items

    def rebuild_items(self, event=None):
        """Rebuilds the object selector list."""
        # Clear the current cached values:
        self._items = None

        # Rebuild the contents of the selector list:
        name = -1
        value = self.value
        choice = self._choice
        choice.clear()
        for i, item in enumerate(self.items):
            if item.is_selectable():
                choice.addItem(item.get_name())
                if item.is_compatible(value):
                    name = i

        # Reselect the current item if possible:
        if name >= 0:
            choice.setCurrentIndex(name)
        else:
            # Otherwise, current value is no longer valid, set combobox empty
            try:
                self.value = None
                choice.setCurrentIndex(-1)
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

    def update_object(self, index):
        """Handles the user selecting a new value from the combo box."""
        item = self.items[index]
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

    def update_editor(self):
        """Updates the editor when the object trait changes externally to the
        editor.
        """
        # Synchronize the editor contents:
        self.resynch_editor()

        # Update the selector (if any):
        choice = self._choice
        item = self.item_for(self.value)
        if choice is not None:
            if item is not None:
                name = item.get_name(self.value)
                if self._object_cache is not None:
                    idx = choice.findText(name)
                    if idx < 0:
                        idx = choice.count()
                        choice.addItem(name)

                    choice.setCurrentIndex(idx)
                else:
                    choice.setText(name)
            else:
                # choice can also be a QLineEdit in which case we just leave
                # text as empty
                if isinstance(choice, QtGui.QComboBox):
                    choice.setCurrentIndex(-1)

    def resynch_editor(self):
        """Resynchronizes the contents of the editor when the object trait
        changes externally to the editor.
        """
        panel = self._panel
        if panel is not None:
            # Dispose of the previous contents of the panel:
            layout = panel.layout()
            if layout is None:
                layout = QtGui.QVBoxLayout(panel)
                layout.setContentsMargins(0, 0, 0, 0)
            elif self._ui is not None:
                self._ui.dispose()
                self._ui = None
            else:
                child = layout.takeAt(0)
                while child is not None:
                    child = layout.takeAt(0)

                del child

            # Create the new content for the panel:
            stretch = 0
            value = self.value
            if not isinstance(value, HasTraits):
                str_value = ""
                if value is not None:
                    str_value = self.str_value
                control = QtGui.QLabel(str_value)
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

            # FIXME: Handle stretch.
            layout.addWidget(control)

    def dispose(self):
        """Disposes of the contents of an editor."""
        # Make sure we aren't hanging on to any object refs:
        self._object_cache = None

        if self._ui is not None:
            self._ui.dispose()

        if self._choice is not None:
            # _choice can also be a QLineEdit in which case we never set up
            # this observer.
            if isinstance(self._choice, QtGui.QComboBox):
                if self._object is not None:
                    self._object.observe(
                        self.rebuild_items,
                        self._name + ".items",
                        remove=True,
                        dispatch="ui",
                    )

                self.factory.observe(
                    self.rebuild_items,
                    "values.items",
                    remove=True,
                    dispatch="ui",
                )

        super().dispose()

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

    # -- Traits event handlers ------------------------------------------------

    def _view_changed(self, view):
        self.resynch_editor()


class SimpleEditor(CustomEditor):
    """Simple style of editor for instances, which displays a button. Clicking
    the button displays a dialog box in which the instance can be edited.
    """

    #: The ui instance for the currently open editor dialog
    _dialog_ui = Instance("traitsui.ui.UI")

    #: Class constants:
    orientation = QtGui.QBoxLayout.Direction.LeftToRight
    extra = 2

    def create_editor(self, parent, layout):
        """Creates the editor control (a button)."""
        self._button = QtGui.QPushButton()
        self._button.setAutoDefault(False)
        layout.addWidget(self._button)
        self._button.clicked.connect(self.edit_instance)
        # Make sure the editor is properly disposed if parent UI is closed
        self._button.destroyed.connect(self._parent_closed)

    def edit_instance(self):
        """Edit the contents of the object trait when the user clicks the
        button.
        """
        # Create the user interface:
        factory = self.factory
        view = self.ui.handler.trait_view_for(
            self.ui.info, factory.view, self.value, self.object_name, self.name
        )
        self._dialog_ui = self.value.edit_traits(
            view, kind=factory.kind, id=factory.id
        )

        # Check to see if the view was 'modal', in which case it will already
        # have been closed (i.e. is None) by the time we get control back:
        if self._dialog_ui.control is not None:
            # Position the window on the display:
            position_window(self._dialog_ui.control)

            # Chain our undo history to the new user interface if it does not
            # have its own:
            if self._dialog_ui.history is None:
                self._dialog_ui.history = self.ui.history

        else:
            self._dialog_ui = None

    def resynch_editor(self):
        """Resynchronizes the contents of the editor when the object trait
        changes externally to the editor.
        """
        button = self._button
        if button is not None:
            label = self.factory.label
            if label == "":
                label = user_name_for(self.name)

            button.setText(label)
            button.setEnabled(isinstance(self.value, HasTraits))

    def _parent_closed(self):
        if self._dialog_ui is not None:
            if self._dialog_ui.control is not None:
                self._dialog_ui.control.close()
            self._dialog_ui.dispose()
            self._dialog_ui = None
