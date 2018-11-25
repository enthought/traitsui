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
#  Date:   10/13/2004
#
#------------------------------------------------------------------------------

""" Defines the concrete implementations of the traits Toolkit interface for
    the wxPython user interface toolkit.
"""

#-------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------

# Make sure that importimg from this backend is OK:
from __future__ import absolute_import
from traitsui.toolkit import assert_toolkit_import
assert_toolkit_import(['wx'])

import wx

# Ensure that we can import Pyface backend.  This starts App as a side-effect.
from pyface.toolkit import toolkit_object as pyface_toolkit
_app = pyface_toolkit('init:_app')

from traits.api import (
    HasPrivateTraits, Instance, Property, Category, cached_property
)
from traits.trait_notifiers import set_ui_handler
from pyface.wx.drag_and_drop import PythonDropTarget

from traitsui.theme import Theme
from traitsui.ui import UI
from traitsui.dock_window_theme import DockWindowTheme
from traitsui.toolkit import Toolkit

from .constants import WindowColor, screen_dx, screen_dy
from .helper import position_window

#-------------------------------------------------------------------------
#  Constants:
#-------------------------------------------------------------------------

EventSuffix = {
    wx.wxEVT_LEFT_DOWN: 'left_down',
    wx.wxEVT_LEFT_DCLICK: 'left_dclick',
    wx.wxEVT_LEFT_UP: 'left_up',
    wx.wxEVT_MIDDLE_DOWN: 'middle_down',
    wx.wxEVT_MIDDLE_DCLICK: 'middle_dclick',
    wx.wxEVT_MIDDLE_UP: 'middle_up',
    wx.wxEVT_RIGHT_DOWN: 'right_down',
    wx.wxEVT_RIGHT_DCLICK: 'right_dclick',
    wx.wxEVT_RIGHT_UP: 'right_up',
    wx.wxEVT_MOTION: 'mouse_move',
    wx.wxEVT_ENTER_WINDOW: 'enter',
    wx.wxEVT_LEAVE_WINDOW: 'leave',
    wx.wxEVT_MOUSEWHEEL: 'mouse_wheel',
    wx.wxEVT_PAINT: 'paint',
}

# Types of popup views:
Popups = {'popup', 'popover', 'info'}

#-------------------------------------------------------------------------
#  Handles UI notification handler requests that occur on a thread other than
#  the UI thread:
#-------------------------------------------------------------------------


def ui_handler(handler, *args):
    """ Handles UI notification handler requests that occur on a thread other
        than the UI thread.
    """
    wx.CallAfter(handler, *args)

# Tell the traits notification handlers to use this UI handler
set_ui_handler(ui_handler)

#-------------------------------------------------------------------------
#  'GUIToolkit' class:
#-------------------------------------------------------------------------


class GUIToolkit(Toolkit):
    """ Implementation class for wxPython toolkit.
    """
    #-------------------------------------------------------------------------
    #  Create wxPython specific user interfaces using information from the
    #  specified UI object:
    #-------------------------------------------------------------------------

    def ui_panel(self, ui, parent):
        """ Creates a wxPython panel-based user interface using information
            from the specified UI object.
        """
        from . import ui_panel
        ui_panel.ui_panel(ui, parent)

    def ui_subpanel(self, ui, parent):
        """ Creates a wxPython subpanel-based user interface using information
            from the specified UI object.
        """
        from . import ui_panel
        ui_panel.ui_subpanel(ui, parent)

    def ui_livemodal(self, ui, parent):
        """ Creates a wxPython modal "live update" dialog user interface using
            information from the specified UI object.
        """
        from . import ui_live
        ui_live.ui_livemodal(ui, parent)

    def ui_live(self, ui, parent):
        """ Creates a wxPython non-modal "live update" window user interface
            using information from the specified UI object.
        """
        from . import ui_live
        ui_live.ui_live(ui, parent)

    def ui_modal(self, ui, parent):
        """ Creates a wxPython modal dialog user interface using information
            from the specified UI object.
        """
        from . import ui_modal
        ui_modal.ui_modal(ui, parent)

    def ui_nonmodal(self, ui, parent):
        """ Creates a wxPython non-modal dialog user interface using
            information from the specified UI object.
        """
        from . import ui_modal
        ui_modal.ui_nonmodal(ui, parent)

    def ui_popup(self, ui, parent):
        """ Creates a wxPython temporary "live update" popup dialog user
            interface using information from the specified UI object.
        """
        from . import ui_live
        ui_live.ui_popup(ui, parent)

    def ui_popover(self, ui, parent):
        """ Creates a wxPython temporary "live update" popup dialog user
            interface using information from the specified UI object.
        """
        from . import ui_live
        ui_live.ui_popover(ui, parent)

    def ui_info(self, ui, parent):
        """ Creates a wxPython temporary "live update" popup dialog user
            interface using information from the specified UI object.
        """
        from . import ui_live
        ui_live.ui_info(ui, parent)

    def ui_wizard(self, ui, parent):
        """ Creates a wxPython wizard dialog user interface using information
            from the specified UI object.
        """
        from . import ui_wizard
        ui_wizard.ui_wizard(ui, parent)

    def view_application(self, context, view, kind=None, handler=None,
                         id='', scrollable=None, args=None):
        """ Creates a wxPython modal dialog user interface that
            runs as a complete application, using information from the
            specified View object.

        Parameters
        ----------
        context : object or dictionary
            A single object or a dictionary of string/object pairs, whose trait
            attributes are to be edited. If not specified, the current object is
            used.
        view : view or string
            A View object that defines a user interface for editing trait
            attribute values.
        kind : string
            The type of user interface window to create. See the
            **traitsui.view.kind_trait** trait for values and
            their meanings. If *kind* is unspecified or None, the **kind**
            attribute of the View object is used.
        handler : Handler object
            A handler object used for event handling in the dialog box. If
            None, the default handler for Traits UI is used.
        id : string
            A unique ID for persisting preferences about this user interface,
            such as size and position. If not specified, no user preferences
            are saved.
        scrollable : Boolean
            Indicates whether the dialog box should be scrollable. When set to
            True, scroll bars appear on the dialog box if it is not large enough
            to display all of the items in the view at one time.

        """
        from . import view_application
        return view_application.view_application(context, view, kind, handler,
                                                 id, scrollable, args)

    #-------------------------------------------------------------------------
    #  Positions the associated dialog window on the display:
    #-------------------------------------------------------------------------

    def position(self, ui):
        """ Positions the associated dialog window on the display.
        """
        view = ui.view
        window = ui.control

        # Set up the default position of the window:
        parent = window.GetParent()
        if parent is None:
            px, py = 0, 0
            pdx, pdy = screen_dx, screen_dy
        else:
            px, py = parent.GetPositionTuple()
            pdx, pdy = parent.GetSizeTuple()

        # Calculate the correct width and height for the window:
        cur_width, cur_height = window.GetSizeTuple()
        width = view.width
        height = view.height

        if width < 0.0:
            width = cur_width
        elif width <= 1.0:
            width = int(width * screen_dx)
        else:
            width = int(width)

        if height < 0.0:
            height = cur_height
        elif height <= 1.0:
            height = int(height * screen_dy)
        else:
            height = int(height)

        if view.kind in Popups:
            position_window(window, width, height)
            return

        # Calculate the correct position for the window:
        x = view.x
        y = view.y

        if x < -99999.0:
            # BH- I think this is the case when there is a parent
            # so this logic tries to place it in the middle of the parent
            # if possible, otherwise tries an offset from the parent
            x = px + (pdx - width) / 2
            if x < 0:
                x = px + 20
        elif x <= -1.0:
            x = px + pdx - width + int(x) + 1
        elif x < 0.0:
            x = px + pdx - width + int(x * pdx)
        elif x <= 1.0:
            x = px + int(x * pdx)
        else:
            x = int(x)

        if y < -99999.0:
            # BH- I think this is the case when there is a parent
            # so this logic tries to place it in the middle of the parent
            # if possible, otherwise tries an offset from the parent
            y = py + (pdy - height) / 2
            if y < 0:
                y = py + 20
        elif y <= -1.0:
            y = py + pdy - height + int(y) + 1
        elif x < 0.0:
            y = py + pdy - height + int(y * pdy)
        elif y <= 1.0:
            y = py + int(y * pdy)
        else:
            y = int(y)

        # make sure the position is on the visible screen, maybe
        # the desktop had been resized?
        x = min(x, wx.DisplaySize()[0])
        y = min(y, wx.DisplaySize()[1])

        # Position and size the window as requested:
        window.SetDimensions(max(0, x), max(0, y), width, height)

    #-------------------------------------------------------------------------
    #  Shows a 'Help' window for a specified UI and control:
    #-------------------------------------------------------------------------

    def show_help(self, ui, control):
        """ Shows a help window for a specified UI and control.
        """
        from . import ui_panel
        ui_panel.show_help(ui, control)

    #-------------------------------------------------------------------------
    #  Saves user preference information associated with a UI window:
    #-------------------------------------------------------------------------

    def save_window(self, ui):
        """ Saves user preference information associated with a UI window.
        """
        from . import helper

        helper.save_window(ui)

    #-------------------------------------------------------------------------
    #  Rebuilds a UI after a change to the content of the UI:
    #-------------------------------------------------------------------------

    def rebuild_ui(self, ui):
        """ Rebuilds a UI after a change to the content of the UI.
        """
        parent = size = None

        if ui.control is not None:
            size = ui.control.GetSize()
            parent = ui.control._parent
            info = ui.info
            ui.recycle()
            ui.info = info
            info.ui = ui

        ui.rebuild(ui, parent)

        if parent is not None:
            ui.control.SetSize(size)
            sizer = parent.GetSizer()
            if sizer is not None:
                sizer.Add(ui.control, 1, wx.EXPAND)

    #-------------------------------------------------------------------------
    #  Sets the title for the UI window:
    #-------------------------------------------------------------------------

    def set_title(self, ui):
        """ Sets the title for the UI window.
        """
        ui.control.SetTitle(ui.title)

    #-------------------------------------------------------------------------
    #  Sets the icon for the UI window:
    #-------------------------------------------------------------------------

    def set_icon(self, ui):
        """ Sets the icon for the UI window.
        """
        from pyface.image_resource import ImageResource

        if isinstance(ui.icon, ImageResource):
            ui.control.SetIcon(ui.icon.create_icon())

    #-------------------------------------------------------------------------
    #  Converts a keystroke event into a corresponding key name:
    #-------------------------------------------------------------------------

    def key_event_to_name(self, event):
        """ Converts a keystroke event into a corresponding key name.
        """
        from . import key_event_to_name

        return key_event_to_name.key_event_to_name(event)

    #-------------------------------------------------------------------------
    #  Hooks all specified events for all controls in a ui so that they can be
    #  routed to the correct event handler:
    #-------------------------------------------------------------------------

    def hook_events(self, ui, control, events=None, handler=None):
        """ Hooks all specified events for all controls in a UI so that they
            can be routed to the correct event handler.
        """
        if events is None:
            events = (
                wx.wxEVT_LEFT_DOWN,
                wx.wxEVT_LEFT_DCLICK,
                wx.wxEVT_LEFT_UP,
                wx.wxEVT_MIDDLE_DOWN,
                wx.wxEVT_MIDDLE_DCLICK,
                wx.wxEVT_MIDDLE_UP,
                wx.wxEVT_RIGHT_DOWN,
                wx.wxEVT_RIGHT_DCLICK,
                wx.wxEVT_RIGHT_UP,
                wx.wxEVT_MOTION,
                wx.wxEVT_ENTER_WINDOW,
                wx.wxEVT_LEAVE_WINDOW,
                wx.wxEVT_MOUSEWHEEL,
                wx.wxEVT_PAINT)
            control.SetDropTarget(PythonDropTarget(
                DragHandler(ui=ui, control=control)))
        elif events == 'keys':
            events = (wx.wxEVT_CHAR, )

        if handler is None:
            handler = ui.route_event

        id = control.GetId()
        event_handler = EventHandlerWrapper()
        connect = event_handler.Connect

        for event in events:
            connect(id, id, event, handler)

        control.PushEventHandler(event_handler)

        for child in control.GetChildren():
            self.hook_events(ui, child, events, handler)

    #-------------------------------------------------------------------------
    #  Routes a 'hooked' event to the correct handler method:
    #-------------------------------------------------------------------------

    def route_event(self, ui, event):
        """ Routes a hooked event to the correct handler method.
        """
        suffix = EventSuffix[event.GetEventType()]
        control = event.GetEventObject()
        handler = ui.handler
        method = None

        owner = getattr(control, '_owner', None)
        if owner is not None:
            method = getattr(handler, 'on_%s_%s' % (owner.get_id(), suffix),
                             None)

        if method is None:
            method = (getattr(handler, 'on_%s' % suffix, None) or
                      getattr(handler, 'on_any_event', None))

        if (method is None) or (method(ui.info, owner, event) is False):
            event.Skip()

    #-------------------------------------------------------------------------
    #  Indicates that an event should continue to be processed by the toolkit
    #-------------------------------------------------------------------------

    def skip_event(self, event):
        """ Indicates that an event should continue to be processed by the
            toolkit.
        """
        event.Skip()

    #-------------------------------------------------------------------------
    #  Destroys a specified GUI toolkit control:
    #-------------------------------------------------------------------------

    def destroy_control(self, control):
        """ Destroys a specified GUI toolkit control.
        """
        _popEventHandlers(control)
        control.Destroy()

    #-------------------------------------------------------------------------
    #  Destroys all of the child controls of a specified GUI toolkit control:
    #-------------------------------------------------------------------------

    def destroy_children(self, control):
        """ Destroys all of the child controls of a specified GUI toolkit
            control.
        """
        for child in control.GetChildren():
            _popEventHandlers(child)
        control.DestroyChildren()

    #-------------------------------------------------------------------------
    #  Returns a ( width, height ) tuple containing the size of a specified
    #  toolkit image:
    #-------------------------------------------------------------------------

    def image_size(self, image):
        """ Returns a ( width, height ) tuple containing the size of a
            specified toolkit image.
        """
        return (image.GetWidth(), image.GetHeight())

    #-------------------------------------------------------------------------
    #  Returns a dictionary of useful constants:
    #-------------------------------------------------------------------------

    def constants(self):
        """ Returns a dictionary of useful constants.

            Currently, the dictionary should have the following key/value pairs:

            - WindowColor': the standard window background color in the toolkit
              specific color format.
        """
        return {
            'WindowColor': WindowColor
        }

    #-------------------------------------------------------------------------
    #  GUI toolkit dependent trait definitions:
    #-------------------------------------------------------------------------

    def color_trait(self, *args, **traits):
        from . import color_trait as ct
        return ct.WxColor(*args, **traits)

    def rgb_color_trait(self, *args, **traits):
        from . import rgb_color_trait as rgbct
        return rgbct.RGBColor(*args, **traits)

    def font_trait(self, *args, **traits):
        from . import font_trait as ft
        return ft.WxFont(*args, **traits)

    #-------------------------------------------------------------------------
    #  'Editor' class methods:
    #-------------------------------------------------------------------------

    # Generic UI-base editor:
    def ui_editor(self):
        from . import ui_editor
        return ui_editor.UIEditor
#
#    # Drag and drop:
#    def dnd_editor ( self, *args, **traits ):
#        import dnd_editor as dnd
#        return dnd.ToolkitEditorFactory( *args, **traits)
#
#    # Key Binding:
#    def key_binding_editor ( self, *args, **traits ):
#        import key_binding_editor as kbe
#        return kbe.ToolkitEditorFactory( *args, **traits )
#
#    # History:
#    def history_editor ( self, *args, **traits ):
#        import history_editor as he
#        return he.HistoryEditor( *args, **traits )
#
#    # HTML:
#    def html_editor ( self, *args, **traits ):
#        import html_editor as he
#        return he.ToolkitEditorFactory( *args, **traits )
#
#    # Image:
#    def image_editor ( self, *args, **traits ):
#        import image_editor as ie
#        return ie.ImageEditor( *args, **traits )
#
#    # ListStr:
#    def list_str_editor ( self, *args, **traits ):
#        import list_str_editor as lse
#        return lse.ListStrEditor( *args, **traits )
#
#    # Ordered set:
#    def ordered_set_editor ( self, *args, **traits ):
#        import ordered_set_editor as ose
#        return ose.ToolkitEditorFactory( *args, **traits )
#
#    # Plot:
#    def plot_editor ( self, *args, **traits ):
#        import plot_editor as pe
#        return pe.ToolkitEditorFactory( *args, **traits )
#
#    # Popup:
#    def popup_editor ( self, *args, **traits ):
#        import popup_editor as pe
#        return pe.PopupEditor( *args, **traits )
#
#    # RGB Color:
#    def rgb_color_editor ( self, *args, **traits ):
#        import rgb_color_editor as rgbce
#        return rgbce.ToolkitEditorFactory( *args, **traits )
#
#    # Scrubber:
#    def scrubber_editor ( self, *args, **traits ):
#        import scrubber_editor as se
#        return se.ScrubberEditor( *args, **traits )
#
#    # Shell:

    def shell_editor(self, *args, **traits):
        from . import shell_editor as se
        return se.ToolkitEditorFactory(*args, **traits)
#
#    # Tabular:
#    def tabular_editor ( self, *args, **traits ):
#        import tabular_editor as te
#        return te.TabularEditor( *args, **traits )
#
#    # Value:
#    def value_editor ( self, *args, **traits ):
#        import value_editor as ve
#        return ve.ToolkitEditorFactory( *args, **traits )

#-------------------------------------------------------------------------
#  'DragHandler' class:
#-------------------------------------------------------------------------


class DragHandler(HasPrivateTraits):
    """ Handler for drag events.
    """
    #-------------------------------------------------------------------------
    #  Traits definitions:
    #-------------------------------------------------------------------------

    # The UI associated with the drag handler
    ui = Instance(UI)

    # The wx control associated with the drag handler
    control = Instance(wx.Window)

#-- Drag and drop event handlers: ----------------------------------------

    #-------------------------------------------------------------------------
    #  Handles a Python object being dropped on the control:
    #-------------------------------------------------------------------------

    def wx_dropped_on(self, x, y, data, drag_result):
        """ Handles a Python object being dropped on the window.
        """
        return self._drag_event('dropped_on', x, y, data, drag_result)

    #-------------------------------------------------------------------------
    #  Handles a Python object being dragged over the control:
    #-------------------------------------------------------------------------

    def wx_drag_over(self, x, y, data, drag_result):
        """ Handles a Python object being dragged over the tree.
        """
        return self._drag_event('drag_over', x, y, data, drag_result)

    #-------------------------------------------------------------------------
    #  Handles a dragged Python object leaving the window:
    #-------------------------------------------------------------------------

    def wx_drag_leave(self, data):
        """ Handles a dragged Python object leaving the window.
        """
        return self._drag_event('drag_leave')

    #-------------------------------------------------------------------------
    #  Handles routing a drag event to the appropriate handler:
    #-------------------------------------------------------------------------

    def _drag_event(self, suffix, x=None, y=None, data=None,
                    drag_result=None):
        """ Handles routing a drag event to the appropriate handler.
        """
        control = self.control
        handler = self.ui.handler
        method = None

        owner = getattr(control, '_owner', None)
        if owner is not None:
            method = getattr(handler, 'on_%s_%s' % (owner.get_id(), suffix),
                             None)

        if method is None:
            method = getattr(handler, 'on_%s' % suffix, None)

        if method is None:
            return wx.DragNone

        if x is None:
            result = method(self.ui.info, owner)
        else:
            result = method(self.ui.info, owner, x, y, data, drag_result)
        if result is None:
            result = drag_result
        return result


#-------------------------------------------------------------------------
#  Defines the extensions needed to make the generic Theme class specific to
#  wxPython:
#-------------------------------------------------------------------------


class WXTheme(Category, Theme):
    """ Defines the extensions needed to make the generic Theme class specific
        to wxPython.
    """

    # The color to use for content text:
    content_color = Property

    # The color to use for label text:
    label_color = Property

    # The image slice used to draw the theme:
    image_slice = Property(depends_on='image')

    #-- Property Implementations ---------------------------------------------

    def _get_content_color(self):
        if self._content_color is None:
            color = wx.BLACK
            islice = self.image_slice
            if islice is not None:
                color = islice.content_color

            self._content_color = color

        return self._content_color

    def _set_content_color(self, color):
        self._content_color = color

    def _get_label_color(self):
        if self._label_color is None:
            color = wx.BLACK
            islice = self.image_slice
            if islice is not None:
                color = islice.label_color

            self._label_color = color

        return self._label_color

    def _set_label_color(self, color):
        self._label_color = color

    @cached_property
    def _get_image_slice(self):
        from .image_slice import image_slice_for

        if self.image is None:
            return None

        return image_slice_for(self.image)
#-------------------------------------------------------------------------
#  Defines the extensions needed to make the generic DockWindowTheme class
#  specific to wxPython:
#-------------------------------------------------------------------------


class WXDockWindowTheme(Category, DockWindowTheme):
    """ Defines the extensions needed to make the generic DockWindowTheme class
        specific to wxPython.
    """

    # The bitmap for the 'tab_inactive_edge' image:
    tab_inactive_edge_bitmap = Property(depends_on='tab_inactive_edge')

    # The bitmap for the 'tab_hover_edge' image:
    tab_hover_edge_bitmap = Property(depends_on='tab_hover_edge')

    #-- Property Implementations ---------------------------------------------

    @cached_property
    def _get_tab_inactive_edge_bitmap(self):
        image = self.tab_inactive_edge
        if image is None:
            return None

        return image.create_image().ConvertToBitmap()

    @cached_property
    def _get_tab_hover_edge_bitmap(self):
        image = self.tab_hover_edge
        if image is None:
            return self.tab_inactive_edge_bitmap

        return image.create_image().ConvertToBitmap()


#-------------------------------------------------------------------------

class EventHandlerWrapper(wx.EvtHandler):
    """ Simple wrapper around wx.EvtHandler used to determine which event
    handlers were added by traitui.
    """
    pass


def _popEventHandlers(ctrl):
    """ Pop any event handlers that have been pushed on to a window and its
        children.
    """

    # Assume that all traitsui event handlers are on the top of the stack
    while ctrl is not ctrl.GetEventHandler():
        handler = ctrl.GetEventHandler()
        if isinstance(handler, EventHandlerWrapper):
            ctrl.PopEventHandler(True)
        else:
            break
    for child in ctrl.GetChildren():
        _popEventHandlers(child)
