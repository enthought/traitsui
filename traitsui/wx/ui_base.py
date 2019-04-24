#------------------------------------------------------------------------------
#
#  Copyright (c) 2005, Enthought, Inc.
#  All rights reserved.
#
#  This software is provided without warranty under the terms of the BSD
#  license included in enthought/LICENSE.txt and may be redistributed only
#  under the conditions described in the aforementioned license.  The license
#  is also available online at http://www.enthought.com/licenses/BSD.txt
#
#  Thanks for using Enthought open source!
#
#  Author: David C. Morrill
#  Date:   12/18/2004
#
#------------------------------------------------------------------------------

""" Defines the base class for the wxPython-based Traits UI modal and non-modal
    dialogs.
"""

from __future__ import absolute_import
import wx

from traits.api import HasPrivateTraits, Instance

from traitsui.base_panel import BasePanel as _BasePanel
from traitsui.menu import Action
from .editor import Editor


class ButtonEditor(Editor):
    """ Editor for buttons.
    """
    # Action associated with the button
    action = Instance(Action)

    def __init__(self, **traits):
        # XXX Why does this need to be an Editor subclass? -- CJW
        HasPrivateTraits.__init__(self, **traits)

    def perform(self, event):
        """ Handles the associated button being clicked.
        """
        handler = self.ui.handler
        self.ui.do_undoable(handler.perform, self.ui.info, self.action, event)


class BaseDialog(_BasePanel):
    """ Base class for Traits UI dialog boxes.
    """

    def default_icon(self):
        """ Return a default icon for a TraitsUI dialog. """
        from pyface.image_resource import ImageResource
        return ImageResource('frame.ico')

    def set_icon(self, icon=None):
        """ Sets the frame's icon.
        """
        from pyface.image_resource import ImageResource

        if not isinstance(icon, ImageResource):
            icon = self.default_icon()
        self.control.SetIcon(icon.create_icon())

    def add_statusbar(self):
        """ Adds a status bar to the dialog.
        """
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
                set_text(ui.get_extended_value(name))
                col = name.find('.')
                object = 'object'
                if col >= 0:
                    object = name[: col]
                    name = name[col + 1:]
                object = context[object]
                object.on_trait_change(set_text, name, dispatch='ui')
                listeners.append((object, set_text, name))

            control.SetStatusWidths(widths)
            self.control.SetStatusBar(control)
            ui._statusbar = listeners

    def _set_status_text(self, control, i):
        def set_status_text(text):
            control.SetStatusText(text, i)

        return set_status_text

    def add_menubar(self):
        """ Adds a menu bar to the dialog.
        """
        menubar = self.ui.view.menubar
        if menubar is not None:
            self._last_group = self._last_parent = None
            self.control.SetMenuBar(
                menubar.create_menu_bar(self.control, self))
            self._last_group = self._last_parent = None

    def add_toolbar(self):
        """ Adds a toolbar to the dialog.
        """
        toolbar = self.ui.view.toolbar
        if toolbar is not None:
            self._last_group = self._last_parent = None
            self.control.SetToolBar(
                toolbar.create_tool_bar(self.control, self))
            self._last_group = self._last_parent = None

    def add_button(self, action, sizer, method=None, enabled=True,
                   name=None, default=False):
        """ Creates a button.
        """
        ui = self.ui
        if ((action.defined_when != '') and
                (not ui.eval_when(action.defined_when))):
            return None

        if name is None:
            name = action.name
        id = action.id
        button = wx.Button(self.control, -1, name)
        button.Enable(enabled)
        if default:
            button.SetDefault()
        if (method is None) or (action.enabled_when != '') or (id != ''):
            editor = ButtonEditor(ui=ui,
                                  action=action,
                                  control=button)
            if id != '':
                ui.info.bind(id, editor)
            if action.visible_when != '':
                ui.add_visible(action.visible_when, editor)
            if action.enabled_when != '':
                ui.add_enabled(action.enabled_when, editor)
            if method is None:
                method = editor.perform
        wx.EVT_BUTTON(self.control, button.GetId(), method)
        sizer.Add(button, 0, wx.LEFT, 5)
        if action.tooltip != '':
            button.SetToolTipString(action.tooltip)
        return button
