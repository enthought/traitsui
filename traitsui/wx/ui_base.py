# (C) Copyright 2004-2023 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

""" Defines the base class for the wxPython-based Traits UI modal and non-modal
    dialogs.
"""

import wx

from pyface.action.schema.api import (
    ActionManagerBuilder, MenuBarSchema, ToolBarSchema,
)
from traits.api import HasPrivateTraits, Instance

from traitsui.base_panel import BasePanel as _BasePanel
from traitsui.menu import Action
from .editor import Editor
from .helper import restore_window


class ButtonEditor(Editor):
    """Editor for buttons."""

    # Action associated with the button
    action = Instance(Action)

    def __init__(self, **traits):
        # XXX Why does this need to be an Editor subclass? -- CJW
        HasPrivateTraits.__init__(self, **traits)

    def perform(self, event):
        """Handles the associated button being clicked."""
        handler = self.ui.handler
        self.ui.do_undoable(handler.perform, self.ui.info, self.action, event)


class BaseDialog(_BasePanel):
    """Base class for Traits UI dialog boxes."""

    # The different dialog styles.
    NONMODAL = 0
    MODAL = 1
    POPUP = 2
    POPOVER = 3
    INFO = 4

    # Types of 'popup' dialogs:
    POPUP_TYPES = {POPUP, POPOVER, INFO}

    def init(self, ui, parent, style):
        """Initialise the dialog by creating the controls."""

        raise NotImplementedError

    @staticmethod
    def display_ui(ui, parent, style):
        ui.owner.init(ui, parent, style)
        ui.control = ui.owner.control
        ui.control._parent = parent

        try:
            ui.prepare_ui()
        except:
            ui.control.Destroy()
            ui.control.ui = None
            ui.control = None
            ui.owner = None
            ui.result = False
            raise

        ui.handler.position(ui.info)
        restore_window(ui, is_popup=(style in BaseDialog.POPUP_TYPES))

        ui.control.Layout()
        # Check if the control is already being displayed modally. This would be
        # the case if after the window was displayed, some event caused the ui to
        # get rebuilt (typically when the user fires the 'updated' event on the ui
        # ). In this case, calling ShowModal again leads to the parent window
        # hanging even after the control has been closed by clicking OK or Cancel
        # (maybe the modal mode isn't ending?)
        if style == BaseDialog.MODAL and not ui.control.IsModal():
            ui.control.ShowModal()
        else:
            ui.control.Show()

    def default_icon(self):
        """Return a default icon for a TraitsUI dialog."""
        from pyface.image_resource import ImageResource

        return ImageResource("frame.ico")

    def set_icon(self, icon=None):
        """Sets the frame's icon."""
        from pyface.image_resource import ImageResource

        if not isinstance(icon, ImageResource):
            icon = self.default_icon()
        self.control.SetIcon(icon.create_icon())

    def add_statusbar(self):
        """Adds a status bar to the dialog."""
        ui = self.ui
        statusbar = ui.view.statusbar
        context = ui.context
        if statusbar is not None:
            widths = []
            listeners = []
            control = wx.StatusBar(self.control)
            control.SetFieldsCount(len(statusbar))
            for i, item in enumerate(statusbar):
                width = abs(item.width)
                if width <= 1.0:
                    widths.append(-max(1, int(1000 * width)))
                else:
                    widths.append(int(width))

                set_text = self._set_status_text(control, i)
                name = item.name
                control.SetStatusText(ui.get_extended_value(name), i)
                col = name.find(".")
                object = "object"
                if col >= 0:
                    object = name[:col]
                    name = name[col + 1 :]
                object = context[object]
                object.observe(set_text, name, dispatch="ui")
                listeners.append((object, set_text, name))

            control.SetStatusWidths(widths)
            self.control.SetStatusBar(control)
            ui._statusbar = listeners

    def _set_status_text(self, control, i):
        def set_status_text(event):
            text = event.new
            control.SetStatusText(text, i)

        return set_status_text

    def add_menubar(self):
        """Adds a menu bar to the dialog."""
        menubar = self.ui.view.menubar
        menubar = self.ui.view.menubar
        if isinstance(menubar, MenuBarSchema):
            builder = self.ui.view.action_manager_builder
            menubar = builder.create_action_manager(menubar)
        if menubar is not None:
            self._last_group = self._last_parent = None
            self.control.SetMenuBar(
                menubar.create_menu_bar(self.control, self)
            )
            self._last_group = self._last_parent = None

    def add_toolbar(self):
        """Adds a toolbar to the dialog."""
        toolbar = self.ui.view.toolbar
        if isinstance(toolbar, ToolBarSchema):
            builder = self.ui.view.action_manager_builder
            toolbar = builder.create_action_manager(toolbar)
        if toolbar is not None:
            self._last_group = self._last_parent = None
            self.control.SetToolBar(
                toolbar.create_tool_bar(self.control, self)
            )
            self._last_group = self._last_parent = None

    def add_button(
        self,
        action,
        sizer,
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
        button = wx.Button(self.control, -1, name)
        button.Enable(enabled)
        if default:
            button.SetDefault()
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
        self.control.Bind(wx.EVT_BUTTON, method, id=button.GetId())
        sizer.Add(button, 0, wx.LEFT, 5)
        if action.tooltip != "":
            button.SetToolTip(action.tooltip)
        return button
