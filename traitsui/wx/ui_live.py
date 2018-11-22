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
#  Date:   11/01/2004
#
#------------------------------------------------------------------------------

""" Creates a wxPython user interface for a specified UI object, where the UI
    is "live", meaning that it immediately updates its underlying object(s).
"""

#-------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------

from __future__ import absolute_import
import wx

from .helper \
    import restore_window, save_window, TraitsUIScrolledPanel

from .ui_base \
    import BaseDialog

from .ui_panel \
    import panel, show_help

from .constants \
    import DefaultTitle, WindowColor, screen_dy, \
    scrollbar_dx
from traitsui.undo \
    import UndoHistory

from traitsui.menu \
    import UndoButton, RevertButton, OKButton, CancelButton, HelpButton

#-------------------------------------------------------------------------
#  Constants:
#-------------------------------------------------------------------------

# Types of supported windows:
NONMODAL = 0
MODAL = 1
POPUP = 2
POPOVER = 3
INFO = 4

# Types of 'popup' dialogs:
Popups = {POPUP, POPOVER, INFO}

#-------------------------------------------------------------------------
#  Creates a 'live update' wxPython user interface for a specified UI object:
#-------------------------------------------------------------------------


def ui_live(ui, parent):
    """ Creates a live, non-modal wxPython user interface for a specified UI
    object.
    """
    ui_dialog(ui, parent, NONMODAL)


def ui_livemodal(ui, parent):
    """ Creates a live, modal wxPython user interface for a specified UI object.
    """
    ui_dialog(ui, parent, MODAL)


def ui_popup(ui, parent):
    """ Creates a live, temporary popup wxPython user interface for a specified
        UI object.
    """
    ui_dialog(ui, parent, POPUP)


def ui_popover(ui, parent):
    """ Creates a live, temporary popup wxPython user interface for a specified
        UI object.
    """
    ui_dialog(ui, parent, POPOVER)


def ui_info(ui, parent):
    """ Creates a live, temporary popup wxPython user interface for a specified
        UI object.
    """
    ui_dialog(ui, parent, INFO)


def ui_dialog(ui, parent, style):
    """ Creates a live wxPython user interface for a specified UI object.
    """
    if ui.owner is None:
        ui.owner = LiveWindow()

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
    restore_window(ui, is_popup=(style in Popups))

    ui.control.Layout()
    # Check if the control is already being displayed modally. This would be
    # the case if after the window was displayed, some event caused the ui to
    # get rebuilt (typically when the user fires the 'updated' event on the ui
    # ). In this case, calling ShowModal again leads to the parent window
    # hanging even after the control has been closed by clicking OK or Cancel
    # (maybe the modal mode isn't ending?)
    if style == MODAL and not ui.control.IsModal():
        ui.control.ShowModal()
    else:
        ui.control.Show()

#-------------------------------------------------------------------------
#  'LiveWindow' class:
#-------------------------------------------------------------------------


class LiveWindow(BaseDialog):
    """ User interface window that immediately updates its underlying object(s).
    """

    #-------------------------------------------------------------------------
    #  Initializes the object:
    #-------------------------------------------------------------------------

    def init(self, ui, parent, style):
        self.is_modal = (style == MODAL)
        window_style = 0
        view = ui.view
        if view.resizable:
            window_style |= wx.RESIZE_BORDER

        title = view.title
        if title == '':
            title = DefaultTitle

        history = ui.history
        window = ui.control
        if window is not None:
            if history is not None:
                history.on_trait_change(self._on_undoable, 'undoable',
                                        remove=True)
                history.on_trait_change(self._on_redoable, 'redoable',
                                        remove=True)
                history.on_trait_change(self._on_revertable, 'undoable',
                                        remove=True)
            window.SetSizer(None)
            ui.reset()
        else:
            self.ui = ui
            if style == MODAL:
                if view.resizable:
                    window_style |= (wx.MAXIMIZE_BOX | wx.MINIMIZE_BOX)
                window = wx.Dialog(
                    parent, -1, title, style=window_style | wx.DEFAULT_DIALOG_STYLE)
            elif style == NONMODAL:
                if parent is not None:
                    window_style |= (wx.FRAME_FLOAT_ON_PARENT |
                                     wx.FRAME_NO_TASKBAR)
                window = wx.Frame(parent, -1, title, style=window_style |
                                  (wx.DEFAULT_FRAME_STYLE & (~wx.RESIZE_BORDER)))
            else:
                if window_style == 0:
                    window_style = wx.SIMPLE_BORDER
                if parent is not None:
                    window_style |= (wx.FRAME_FLOAT_ON_PARENT |
                                     wx.FRAME_NO_TASKBAR)

                if isinstance(parent, tuple):
                    window = wx.Frame(None, -1, '', style=window_style)
                    window._control_region = parent
                else:
                    window = wx.Frame(parent, -1, '', style=window_style)
                window._kind = ui.view.kind
                self._monitor = MouseMonitor(ui)

            # Set the correct default window background color:
            window.SetBackgroundColour(WindowColor)

            self.control = window
            wx.EVT_CLOSE(window, self._on_close_page)
            wx.EVT_CHAR(window, self._on_key)

        self.set_icon(view.icon)
        buttons = [self.coerce_button(button)
                   for button in view.buttons]
        nbuttons = len(buttons)
        no_buttons = ((nbuttons == 1) and self.is_button(buttons[0], ''))
        has_buttons = (
            (not no_buttons) and (
                (nbuttons > 0) or view.undo or view.revert or view.ok or view.cancel))
        if has_buttons or (view.menubar is not None):
            if history is None:
                history = UndoHistory()
        else:
            history = None
        ui.history = history

        # Create the actual trait sheet panel and imbed it in a scrollable
        # window (if requested):
        sw_sizer = wx.BoxSizer(wx.VERTICAL)
        if ui.scrollable:
            sizer = wx.BoxSizer(wx.VERTICAL)
            sw = TraitsUIScrolledPanel(window)
            trait_sheet = panel(ui, sw)
            sizer.Add(trait_sheet, 1, wx.EXPAND)
            tsdx, tsdy = trait_sheet.GetSize()
            sw.SetScrollRate(16, 16)
            max_dy = (2 * screen_dy) / 3
            sw.SetSizer(sizer)
            sw.SetSize(wx.Size(tsdx + ((tsdy > max_dy) * scrollbar_dx),
                               min(tsdy, max_dy)))
        else:
            sw = panel(ui, window)

        sw_sizer.Add(sw, 1, wx.EXPAND)
        sw_sizer.SetMinSize(sw.GetSize())

        # Check to see if we need to add any of the special function buttons:
        if (not no_buttons) and (has_buttons or view.help):
            sw_sizer.Add(wx.StaticLine(window, -1), 0, wx.EXPAND)
            b_sizer = wx.BoxSizer(wx.HORIZONTAL)

            # Convert all button flags to actual button actions if no buttons
            # were specified in the 'buttons' trait:
            if nbuttons == 0:
                if view.undo:
                    self.check_button(buttons, UndoButton)

                if view.revert:
                    self.check_button(buttons, RevertButton)

                if view.ok:
                    self.check_button(buttons, OKButton)

                if view.cancel:
                    self.check_button(buttons, CancelButton)

                if view.help:
                    self.check_button(buttons, HelpButton)

            # Create a button for each button action:
            for raw_button, button in zip(view.buttons, buttons):
                button = self.coerce_button(button)
                default = raw_button == view.default_button

                if self.is_button(button, 'Undo'):
                    self.undo = self.add_button(
                        button, b_sizer, self._on_undo, False, default=default)
                    self.redo = self.add_button(button, b_sizer,
                                                self._on_redo, False, 'Redo')
                    history.on_trait_change(self._on_undoable, 'undoable',
                                            dispatch='ui')
                    history.on_trait_change(self._on_redoable, 'redoable',
                                            dispatch='ui')
                    if history.can_undo:
                        self._on_undoable(True)

                    if history.can_redo:
                        self._on_redoable(True)

                elif self.is_button(button, 'Revert'):
                    self.revert = self.add_button(
                        button, b_sizer, self._on_revert, False, default=default)
                    history.on_trait_change(self._on_revertable, 'undoable',
                                            dispatch='ui')
                    if history.can_undo:
                        self._on_revertable(True)

                elif self.is_button(button, 'OK'):
                    self.ok = self.add_button(button, b_sizer, self._on_ok,
                                              default=default)
                    ui.on_trait_change(self._on_error, 'errors',
                                       dispatch='ui')

                elif self.is_button(button, 'Cancel'):
                    self.add_button(button, b_sizer, self._on_cancel,
                                    default=default)

                elif self.is_button(button, 'Help'):
                    self.add_button(button, b_sizer, self._on_help,
                                    default=default)

                elif not self.is_button(button, ''):
                    self.add_button(button, b_sizer, default=default)

            sw_sizer.Add(b_sizer, 0, wx.ALIGN_RIGHT | wx.ALL, 5)

        # Add the menu bar, tool bar and status bar (if any):
        self.add_menubar()
        self.add_toolbar()
        self.add_statusbar()

        # Lay all of the dialog contents out:
        window.SetSizer(sw_sizer)
        window.Fit()

    #-------------------------------------------------------------------------
    #  Closes the dialog window:
    #-------------------------------------------------------------------------

    def close(self, rc=wx.ID_OK):
        """ Closes the dialog window.
        """
        ui = self.ui
        ui.result = (rc == wx.ID_OK)
        save_window(ui)
        if self.is_modal:
            self.control.EndModal(rc)

        ui.finish()
        self.ui = self.undo = self.redo = self.revert = self.control = None

    #-------------------------------------------------------------------------
    #  Handles the user clicking the window/dialog 'close' button/icon:
    #-------------------------------------------------------------------------

    def _on_close_page(self, event):
        """ Handles the user clicking the window/dialog "close" button/icon.
        """
        if not self.ui.view.close_result:
            self._on_cancel(event)
        else:
            self._on_ok(event)

    #-------------------------------------------------------------------------
    #  Handles the user giving focus to another window for a 'popup' view:
    #-------------------------------------------------------------------------

    def _on_close_popup(self, event):
        """ Handles the user giving focus to another window for a 'popup' view.
        """
        if not event.GetActive():
            self.close_popup()

    def close_popup(self):
        # Close the window if it has not already been closed:
        if self.ui.info is not None and self.ui.info.ui is not None:
            if self._on_ok():
                self._monitor.Stop()

    #-------------------------------------------------------------------------
    #  Handles the user clicking the 'OK' button:
    #-------------------------------------------------------------------------

    def _on_ok(self, event=None):
        """ Handles the user clicking the **OK** button.
        """
        if self.ui.handler.close(self.ui.info, True):
            wx.EVT_ACTIVATE(self.control, None)
            self.close(wx.ID_OK)
            return True

        return False

    #-------------------------------------------------------------------------
    #  Handles the user hitting the 'Esc'ape key:
    #-------------------------------------------------------------------------

    def _on_key(self, event):
        """ Handles the user pressing the Escape key.
        """
        if event.GetKeyCode() == 0x1B:
            self._on_close_page(event)


    #-------------------------------------------------------------------------
    #  Handles a 'Cancel' all changes request:
    #-------------------------------------------------------------------------

    def _on_cancel(self, event):
        """ Handles a request to cancel all changes.
        """
        if self.ui.handler.close(self.ui.info, False):
            self._on_revert(event)
            self.close(wx.ID_CANCEL)

    #-------------------------------------------------------------------------
    #  Handles editing errors:
    #-------------------------------------------------------------------------

    def _on_error(self, errors):
        """ Handles editing errors.
        """
        self.ok.Enable(errors == 0)

    #-------------------------------------------------------------------------
    #  Handles the undo history 'undoable' state changing:
    #-------------------------------------------------------------------------

    def _on_undoable(self, state):
        """ Handles a change to the "undoable" state of the undo history
        """
        self.undo.Enable(state)

    #-------------------------------------------------------------------------
    #  Handles the undo history 'redoable' state changing:
    #-------------------------------------------------------------------------

    def _on_redoable(self, state):
        """ Handles a change to the "redoable state of the undo history.
        """
        self.redo.Enable(state)

    #-------------------------------------------------------------------------
    #  Handles the 'revert' state changing:
    #-------------------------------------------------------------------------

    def _on_revertable(self, state):
        """ Handles a change to the "revert" state.
        """
        self.revert.Enable(state)

#-------------------------------------------------------------------------
#  'MouseMonitor' class:
#-------------------------------------------------------------------------


class MouseMonitor(wx.Timer):
    """ Monitors a specified window and closes it the first time the mouse
        pointer leaves the window.
    """

    def __init__(self, ui):
        super(MouseMonitor, self).__init__()
        self.ui = ui
        kind = ui.view.kind
        self.is_activated = self.is_info = (kind == 'info')
        self.border = 3
        if kind == 'popup':
            self.border = 10
        self.Start(100)

    def Notify(self):
        ui = self.ui
        control = ui.control
        if ui.control is None:
            # Looks like someone forgot to tell us that the ui has been closed:
            self.Stop()
            return

        mx, my = wx.GetMousePosition()
        cx, cy = control.ClientToScreenXY(0, 0)
        cdx, cdy = control.GetSizeTuple()

        if self.is_activated:
            # Don't close the popup if any mouse buttons are currently pressed:
            ms = wx.GetMouseState()
            if ms.LeftIsDown() or ms.MiddleIsDown() or ms.RightIsDown():
                return

            # Check for the special case of the mouse pointer having to be
            # within the original bounds of the object the popup was created
            # for:
            if self.is_info:
                parent = control.GetParent()
                if isinstance(parent, wx.Window):
                    px, py, pdx, pdy = parent.GetScreenRect()
                else:
                    px, py, pdx, pdy = control._control_region
                if ((mx < px) or (mx >= (px + pdx)) or
                        (my < py) or (my >= (py + pdy))):
                    ui.owner.close_popup()
                    self.is_activated = False

            else:
                # Allow for a 'dead zone' border around the window to allow for
                # small motor control problems:
                border = self.border
                if ((mx < (cx - border)) or (mx >= (cx + cdx + border)) or
                        (my < (cy - border)) or (my >= (cy + cdy + border))):
                    ui.owner.close_popup()
                    self.is_activated = False
        elif (cx <= mx < (cx + cdx)) and (cy <= my < (cy + cdy)):
            self.is_activated = True
