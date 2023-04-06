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

""" Defines the base class for PyQt editors.
"""


from pyface.qt import QtCore, QtGui

from traits.api import HasTraits, Instance, Str, Callable

from traitsui.api import Editor as UIEditor

from .constants import OKColor, ErrorColor


class Editor(UIEditor):
    """Base class for PyQt editors for Traits-based UIs."""

    def clear_layout(self):
        """Delete the contents of a control's layout."""
        layout = self.control.layout()
        while True:
            itm = layout.takeAt(0)
            if itm is None:
                break

            itm.widget().setParent(None)

    def _control_changed(self, control):
        """Handles the **control** trait being set."""
        # FIXME: Check we actually make use of this.
        if control is not None:
            control._editor = self

    def set_focus(self):
        """Assigns focus to the editor's underlying toolkit widget."""
        if self.control is not None:
            self.control.setFocus()

    def update_editor(self):
        """Updates the editor when the object trait changes externally to the
        editor.
        """
        new_value = self.str_value
        if self.control.text() != new_value:
            self.control.setText(new_value)

    def get_control_widget(self):
        """Get the concrete widget for the control.

        Some editors may use a QLayout  instead of a Qwidget, which may not be
        suitable for certain usages (eg. for parenting other widgets).
        """
        if isinstance(self.control, QtGui.QLayout):
            return self.control.parentWidget()
        else:
            return self.control

    def set_tooltip_text(self, control, text):
        """Sets the tooltip for a specified control."""
        control.setToolTip(text)

    def _enabled_changed(self, enabled):
        """Handles the **enabled** state of the editor being changed."""
        if self.control is not None:
            self._enabled_changed_helper(self.control, enabled)
        if self.label_control is not None:
            self.label_control.setEnabled(enabled)

    def _enabled_changed_helper(self, control, enabled):
        """A helper that allows the control to be a layout and recursively
        manages all its widgets.
        """
        if isinstance(control, QtGui.QWidget):
            control.setEnabled(enabled)
        else:
            for i in range(control.count()):
                itm = control.itemAt(i)
                self._enabled_changed_helper(
                    (itm.widget() or itm.layout()), enabled
                )

    def _visible_changed(self, visible):
        """Handles the **visible** state of the editor being changed."""
        if self.label_control is not None:
            self.label_control.setVisible(visible)
        if self.control is None:
            # We are being called after the editor has already gone away.
            return

        self._visible_changed_helper(self.control, visible)

        page = self.control.parent()
        if (
            page is None
            or page.parent() is None
            or page.parent().parent() is None
            or page.layout() is None
            or page.layout().count() != 1
        ):
            return

        # The TabWidget (representing the notebook) has a StackedWidget inside it,
        # which then contains our parent.
        # Even after the tab is removed, the parent-child relationship between
        # our container widget (representing the page) and the enclosing TabWidget,
        # so the following reference is still valid.
        stack_widget = page.parent()
        notebook = stack_widget.parent()
        is_tabbed_group = notebook.property("traits_tabbed_group")
        if (
            notebook is None
            or not isinstance(notebook, QtGui.QTabWidget)
            or not is_tabbed_group
        ):
            return

        if not visible:
            # Store the page number and name on the parent
            for i in range(0, notebook.count()):
                if notebook.widget(i) == page:
                    self._tab_index = i
                    self._tab_text = notebook.tabText(i)
                    page.setVisible(False)
                    notebook.removeTab(i)
                    break
        else:
            # Check to see if our parent has previously-stored tab
            # index and text attributes
            if (
                getattr(self, "_tab_index", None) is not None
                and getattr(self, "_tab_text", None) is not None
            ):
                page.setVisible(True)
                notebook.insertTab(self._tab_index, page, self._tab_text)
        return

    def _visible_changed_helper(self, control, visible):
        """A helper that allows the control to be a layout and recursively
        manages all its widgets.
        """
        if isinstance(control, QtGui.QWidget):
            control.setVisible(visible)
        else:
            for i in range(control.count()):
                itm = control.itemAt(i)
                self._visible_changed_helper(
                    (itm.widget() or itm.layout()), visible
                )

    def get_error_control(self):
        """Returns the editor's control for indicating error status."""
        return self.control

    def in_error_state(self):
        """Returns whether or not the editor is in an error state."""
        return False

    def set_error_state(self, state=None, control=None):
        """Sets the editor's current error state."""
        if state is None:
            state = self.invalid
        state = state or self.in_error_state()

        if control is None:
            control = self.get_error_control()

        if not isinstance(control, list):
            control = [control]

        for item in control:
            if item is None:
                continue

            pal = QtGui.QPalette(item.palette())

            if state:
                color = ErrorColor
                if getattr(item, "_ok_color", None) is None:
                    item._ok_color = QtGui.QColor(
                        pal.color(QtGui.QPalette.ColorRole.Base)
                    )
            else:
                color = getattr(item, "_ok_color", OKColor)

            pal.setColor(QtGui.QPalette.ColorRole.Base, color)
            item.setPalette(pal)

    def _invalid_changed(self, state):
        """Handles the editor's invalid state changing."""
        self.set_error_state()

    def perform(self, action, action_event=None):
        """Performs the action described by a specified Action object."""
        self.ui.do_undoable(self._perform, action)

    def _perform(self, action):
        method_name = action.action
        info = self._menu_context["info"]
        handler = self._menu_context["handler"]
        object = self._menu_context["object"]
        selection = self._menu_context["selection"]
        self._menu_context["action"] = action

        if method_name.find(".") >= 0:
            if method_name.find("(") < 0:
                method_name += "()"
            try:
                eval(method_name, globals(), self._menu_context)
            except:
                from traitsui.api import raise_to_debug

                raise_to_debug()
            return

        method = getattr(handler, method_name, None)
        if method is not None:
            method(info, selection)
            return

        if action.on_perform is not None:
            action.on_perform(selection)
            return

        action.perform(selection)

    def eval_when(self, condition, object, trait):
        """Evaluates a condition within a defined context, and sets a
        specified object trait based on the result, which is assumed to be a
        Boolean.
        """
        if condition != "":
            value = True
            try:
                if not eval(condition, globals(), self._menu_context):
                    value = False
            except:
                from traitsui.api import raise_to_debug

                raise_to_debug()
            setattr(object, trait, value)

    def add_to_menu(self, menu_item):
        """Adds a menu item to the menu bar being constructed."""
        action = menu_item.item.action
        self.eval_when(action.enabled_when, menu_item, "enabled")
        self.eval_when(action.checked_when, menu_item, "checked")

    def can_add_to_menu(self, action):
        """Returns whether the action should be defined in the user interface."""
        if action.defined_when != "":

            try:
                if not eval(
                    action.defined_when, globals(), self._menu_context
                ):
                    return False
            except:
                from traitsui.api import raise_to_debug

                raise_to_debug()

        if action.visible_when != "":
            try:
                if not eval(
                    action.visible_when, globals(), self._menu_context
                ):
                    return False
            except:
                from traitsui.api import raise_to_debug

                raise_to_debug()

        return True

    # TODO: move this method, it should be part of ui_panel or some other
    # place that is responsible for setting up the Qt layout.
    def set_size_policy(self, direction, resizable, springy, stretch):
        """Set the size policy of the editor's controller.

        Based on the "direction" of the group that contains this editor
        (VGroup or HGroup), set the stretch factor and the resizing
        policy of the control.

        Parameters
        ----------
        direction : QtGui.QBoxLayout.Direction
            Directionality of the group that contains this editor. Either
            QtGui.QBoxLayout.Direction.LeftToRight or QtGui.QBoxLayout.Direction.TopToBottom

        resizable : bool
            True if control should be resizable in the orientation opposite
            to the group directionality

        springy : bool
            True if control should be resizable in the orientation equal
            to the group directionality

        stretch : int
            Stretch factor used by Qt to distribute the total size to
            each component.
        """

        policy = self.control.sizePolicy()

        if direction == QtGui.QBoxLayout.Direction.LeftToRight:
            if springy:
                policy.setHorizontalStretch(stretch)
                policy.setHorizontalPolicy(QtGui.QSizePolicy.Policy.Expanding)
            if resizable:
                policy.setVerticalStretch(stretch)
                policy.setVerticalPolicy(QtGui.QSizePolicy.Policy.Expanding)

        else:  # TopToBottom
            if springy:
                policy.setVerticalStretch(stretch)
                policy.setVerticalPolicy(QtGui.QSizePolicy.Policy.Expanding)
            if resizable:
                policy.setHorizontalStretch(stretch)
                policy.setHorizontalPolicy(QtGui.QSizePolicy.Policy.Expanding)

        self.control.setSizePolicy(policy)


class EditorWithList(Editor):
    """Editor for an object that contains a list."""

    # -------------------------------------------------------------------------
    #  Trait definitions:
    # -------------------------------------------------------------------------

    #: Object containing the list being monitored
    list_object = Instance(HasTraits)

    #: Name of the monitored trait
    list_name = Str()

    #: Function used to evaluate the current list object value:
    list_value = Callable()

    def init(self, parent):
        """Initializes the object."""
        factory = self.factory
        name = factory.name
        if name != "":
            (
                self.list_object,
                self.list_name,
                self.list_value,
            ) = self.parse_extended_name(name)
        else:
            self.list_object, self.list_name = factory, "values"
            self.list_value = lambda: factory.values

        self.list_object.on_trait_change(
            self._list_updated, self.list_name, dispatch="ui"
        )
        self.list_object.on_trait_change(
            self._list_updated, self.list_name + "_items", dispatch="ui"
        )

        self._list_updated()

    def dispose(self):
        """Disconnects the listeners set up by the constructor."""
        self.list_object.on_trait_change(
            self._list_updated, self.list_name, remove=True
        )
        self.list_object.on_trait_change(
            self._list_updated, self.list_name + "_items", remove=True
        )

        super().dispose()

    def _list_updated(self):
        """Handles the monitored trait being updated."""
        self.list_updated(self.list_value())

    def list_updated(self, values):
        """Handles the monitored list being updated."""
        raise NotImplementedError


class EditorFromView(Editor):
    """An editor generated from a View object."""

    def init(self, parent):
        """Initializes the object."""
        self._ui = ui = self.init_ui(parent)
        if ui.history is None:
            ui.history = self.ui.history

        self.control = ui.control

    def init_ui(self, parent):
        """Creates and returns the traits UI defined by this editor.
        (Must be overridden by a subclass).
        """
        raise NotImplementedError

    def update_editor(self):
        """Updates the editor when the object trait changes externally to the
        editor.
        """
        # Normally nothing needs to be done here, since it should all be handled
        # by the editor's internally created traits UI:
        pass

    def dispose(self):
        """Disposes of the editor."""
        self._ui.dispose()

        super().dispose()
