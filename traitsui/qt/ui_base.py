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

"""Defines the base class for the PyQt-based Traits UI modal and non-modal
   dialogs.
"""


from pyface.qt import QtCore, QtGui
from pyface.action.schema.api import (
    ActionManagerBuilder, MenuBarSchema, ToolBarSchema,
)
from traits.api import HasPrivateTraits, Instance

from traitsui.base_panel import BasePanel as _BasePanel
from traitsui.menu import Action
from .constants import DefaultTitle
from .editor import Editor
from .helper import restore_window, save_window


class ButtonEditor(Editor):
    """Editor for buttons."""

    # -------------------------------------------------------------------------
    #  Trait definitions:
    # -------------------------------------------------------------------------

    #: Action associated with the button
    action = Instance(Action)

    def __init__(self, **traits):
        # XXX Why does this need to be an Editor subclass? -- CJW
        HasPrivateTraits.__init__(self, **traits)

    def perform(self):
        """Handles the associated button being clicked."""
        handler = self.ui.handler
        self.ui.do_undoable(handler.perform, self.ui.info, self.action, None)


class BasePanel(_BasePanel):
    """Base class for Traits UI panels."""

    def add_button(
        self,
        action,
        bbox,
        role,
        method=None,
        enabled=True,
        name=None,
        default=False,
    ):
        """Creates a button."""
        ui = self.ui
        if (action.defined_when != "") and (
            not ui.eval_when(action.defined_when)
        ):
            return None

        if name is None:
            name = action.name
        id = action.id
        button = bbox.addButton(name, role)
        button.setAutoDefault(False)
        button.setDefault(default)
        button.setEnabled(enabled)
        if (method is None) or (action.enabled_when != "") or (id != ""):
            editor = ButtonEditor(ui=ui, action=action, control=button)
            if id != "":
                ui.info.bind(id, editor)
            if action.visible_when != "":
                ui.add_visible(action.visible_when, editor)
            if action.enabled_when != "":
                ui.add_enabled(action.enabled_when, editor)
            if method is None:
                method = editor.perform

        if method is not None:
            button.clicked.connect(method)

        if action.tooltip != "":
            button.setToolTip(action.tooltip)

        return button

    def _on_undoable(self, event):
        """Handles a change to the "undoable" state of the undo history"""
        state = event.new
        self.undo.setEnabled(state)

    def _on_redoable(self, event):
        """Handles a change to the "redoable" state of the undo history."""
        state = event.new
        self.redo.setEnabled(state)

    def _on_revertable(self, event):
        """Handles a change to the "revert" state."""
        state = event.new
        self.revert.setEnabled(state)


class _StickyDialog(QtGui.QDialog):
    """A QDialog that will only close if the traits handler allows it."""

    def __init__(self, ui, parent):
        """Initialise the dialog."""

        QtGui.QDialog.__init__(self, parent)

        # Create the main window so we can add toolbars etc.
        self._mw = QtGui.QMainWindow()
        layout = QtGui.QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self._mw)
        self.setLayout(layout)

        # Set the dialog's window flags and properties.
        # On some X11 window managers, using the Dialog flag instead of
        # just the Window flag could cause the subsequent minimize and maximize
        # button hint to be ignored such that those actions are not
        # available (but the window can still be resize unless the size
        # constraint is fixed). On some X11 window managers, having two
        # _StickyDialog open where one has a Window flag and other has a Dialog
        # flag results in the latter (Dialog) to be always placed on top of
        # the former (Window).
        flags = QtCore.Qt.WindowType.Window
        if not ui.view.resizable:
            flags |= QtCore.Qt.WindowType.WindowSystemMenuHint
            layout.setSizeConstraint(QtGui.QLayout.SizeConstraint.SetFixedSize)
        try:
            flags |= QtCore.Qt.WindowType.WindowCloseButtonHint
            if ui.view.resizable:
                # Cast to int to deal with cast-to-int deprecation warning on
                # PyQt5 5.12.3
                flags |= int(
                    QtCore.Qt.WindowType.WindowMinimizeButtonHint
                    | QtCore.Qt.WindowType.WindowMaximizeButtonHint
                )
        except AttributeError:
            # Either PyQt or Qt is too old.
            pass
        self.setWindowFlags(flags)

        self._ui = ui
        self._result = None

    def showEvent(self, e):
        self.raise_()

    def closeEvent(self, e):
        """Reimplemented to check when the clicks the window close button.
        (Note that QDialog doesn't get a close event when the dialog is closed
        in any other way.)"""

        if self._ok_to_close():
            QtGui.QDialog.closeEvent(self, e)
        else:
            # Ignore the event thereby keeping the dialog open.
            e.ignore()

    def keyPressEvent(self, e):
        """Reimplemented to ignore the Escape key if appropriate, and to ignore
        the Enter key if no default button has been explicitly set."""

        if (
            e.key() in (QtCore.Qt.Key.Key_Enter, QtCore.Qt.Key.Key_Return)
            and not self._ui.view.default_button
        ):
            return

        if e.key() == QtCore.Qt.Key.Key_Escape and not self._ok_to_close():
            return

        QtGui.QDialog.keyPressEvent(self, e)

    def sizeHint(self):
        """Reimplemented to provide an appropriate size hint for the window."""
        size = QtGui.QDialog.sizeHint(self)
        view = self._ui.view
        if view.width > 0:
            size.setWidth(int(view.width))
        if view.height > 0:
            size.setHeight(int(view.height))
        return size

    def done(self, r):
        """Reimplemented to ignore calls to accept() or reject() if
        appropriate."""

        # If we already have a result then we already know that we are done.
        if self._result is not None:
            QtGui.QDialog.done(self, self._result)
        elif self._ok_to_close(bool(r)):
            QtGui.QDialog.done(self, r)

    def _ok_to_close(self, is_ok=None):
        """Let the handler decide if the dialog should be closed."""

        # The is_ok flag is also the dialog result.  If we don't know it then
        # the the user closed the dialog other than by an 'Ok' or 'Cancel'
        # button.
        if is_ok is None:
            # Use the view's default, if there is one.
            is_ok = self._ui.view.close_result
            if is_ok is None:
                # There is no default, so use False for a modal dialog and True
                # for a non-modal one.
                is_ok = not self.isModal()

        ok_to_close = self._ui.handler.close(self._ui.info, is_ok)
        if ok_to_close:
            # Save the result now.
            self._result = is_ok

        return ok_to_close


class BaseDialog(BasePanel):
    """Base class for Traits UI dialog boxes."""

    #: The different dialog styles.
    NONMODAL, MODAL, POPUP = list(range(3))

    def init(self, ui, parent, style):
        """Initialise the dialog by creating the controls."""

        raise NotImplementedError

    def create_dialog(self, parent, style):
        """Create the dialog control."""

        self.control = control = _StickyDialog(self.ui, parent)

        view = self.ui.view

        control.setModal(style == BaseDialog.MODAL)
        control.setWindowTitle(view.title or DefaultTitle)

        control.finished.connect(self._on_finished)

    def add_contents(self, panel, buttons):
        """Add a panel (either a widget, layout or None) and optional buttons
        to the dialog."""

        # If the panel is a layout then provide a widget for it.
        if isinstance(panel, QtGui.QLayout):
            w = QtGui.QWidget()
            panel.setContentsMargins(0, 0, 0, 0)
            w.setLayout(panel)
            panel = w

        if panel is not None:
            self.control._mw.setCentralWidget(panel)

        # Add the optional buttons.
        if buttons is not None:
            self.control.layout().addWidget(buttons)

        # Add the menu bar, tool bar and status bar (if any).
        self._add_menubar()
        self._add_toolbar()
        self._add_statusbar()

    def close(self, rc=True):
        """Close the dialog and set the given return code."""

        self.ui.dispose(rc)
        self.ui = self.control = None

    @staticmethod
    def display_ui(ui, parent, style):
        """Display the UI."""

        ui.owner.init(ui, parent, style)
        ui.control = ui.owner.control
        ui.control._parent = parent

        try:
            ui.prepare_ui()
        except BaseException:
            ui.control.setParent(None)
            ui.control.ui = None
            ui.control = None
            ui.owner = None
            ui.result = False
            raise

        ui.handler.position(ui.info)
        restore_window(ui)

        # if an item asked for initial focus, give it to them
        if ui._focus_control is not None:
            ui._focus_control.setFocus()
            ui._focus_control = None

        if style == BaseDialog.NONMODAL:
            ui.control.show()
        else:
            ui.control.setWindowModality(QtCore.Qt.WindowModality.ApplicationModal)
            ui.control.exec_()

    def set_icon(self, icon=None):
        """Sets the dialog's icon."""

        from pyface.image_resource import ImageResource

        if not isinstance(icon, ImageResource):
            icon = self.default_icon()

        self.control.setWindowIcon(icon.create_icon())

    def _on_error(self, event):
        """Handles editing errors."""
        errors = event.new
        self.ok.setEnabled(errors == 0)

    def _add_menubar(self):
        """Adds a menu bar to the dialog."""
        menubar = self.ui.view.menubar
        if isinstance(menubar, MenuBarSchema):
            builder = self.ui.view.action_manager_builder
            menubar = builder.create_action_manager(menubar)
        if menubar is not None:
            self._last_group = self._last_parent = None
            self.control.layout().setMenuBar(
                menubar.create_menu_bar(self.control, self)
            )
            self._last_group = self._last_parent = None

    def _add_toolbar(self):
        """Adds a toolbar to the dialog."""
        toolbar = self.ui.view.toolbar
        if isinstance(toolbar, ToolBarSchema):
            builder = self.ui.view.action_manager_builder
            toolbar = builder.create_action_manager(toolbar)
        if toolbar is not None:
            self._last_group = self._last_parent = None
            qt_toolbar = toolbar.create_tool_bar(self.control, self)
            qt_toolbar.setMovable(False)
            self.control._mw.addToolBar(qt_toolbar)
            self._last_group = self._last_parent = None

    def _add_statusbar(self):
        """Adds a statusbar to the dialog."""
        if self.ui.view.statusbar is not None:
            control = QtGui.QStatusBar()
            control.setSizeGripEnabled(self.ui.view.resizable)
            listeners = []
            for item in self.ui.view.statusbar:
                # Create the status widget with initial text
                name = item.name
                item_control = QtGui.QLabel()
                item_control.setText(self.ui.get_extended_value(name))

                # Add the widget to the control with correct size
                width = abs(item.width)
                stretch = 0
                if width <= 1.0:
                    stretch = int(100 * width)
                else:
                    item_control.setMinimumWidth(int(width))
                control.addWidget(item_control, stretch)

                # Set up event listener for updating the status text
                col = name.find(".")
                obj = "object"
                if col >= 0:
                    obj = name[:col]
                    name = name[col + 1 :]
                obj = self.ui.context[obj]
                set_text = self._set_status_text(item_control)
                obj.observe(set_text, name, dispatch="ui")
                listeners.append((obj, set_text, name))

            self.control._mw.setStatusBar(control)
            self.ui._statusbar = listeners

    def _set_status_text(self, control):
        """Helper function for _add_statusbar."""

        def set_status_text(event):
            text = event.new
            control.setText(text)

        return set_status_text
