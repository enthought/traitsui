# (C) Copyright 2004-2023 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

""" Defines the concrete implementations of the traits Toolkit interface for
    the wxPython user interface toolkit.
"""

# Make sure that importimg from this backend is OK:
import logging

from traitsui.toolkit import assert_toolkit_import

assert_toolkit_import(["wx"])

import wx

# Ensure that we can import Pyface backend.  This starts App as a side-effect.
from pyface.toolkit import toolkit_object as pyface_toolkit

_app = pyface_toolkit("init:_app")

from traits.api import HasPrivateTraits, Instance
from traits.trait_notifiers import set_ui_handler
from pyface.api import SystemMetrics
from pyface.wx.drag_and_drop import PythonDropTarget

from traitsui.theme import Theme
from traitsui.ui import UI
from traitsui.toolkit import Toolkit
from .constants import WindowColor
from .helper import position_window

logger = logging.getLogger(__name__)

#: Mapping from wx events to method suffixes.
EventSuffix = {
    wx.wxEVT_LEFT_DOWN: "left_down",
    wx.wxEVT_LEFT_DCLICK: "left_dclick",
    wx.wxEVT_LEFT_UP: "left_up",
    wx.wxEVT_MIDDLE_DOWN: "middle_down",
    wx.wxEVT_MIDDLE_DCLICK: "middle_dclick",
    wx.wxEVT_MIDDLE_UP: "middle_up",
    wx.wxEVT_RIGHT_DOWN: "right_down",
    wx.wxEVT_RIGHT_DCLICK: "right_dclick",
    wx.wxEVT_RIGHT_UP: "right_up",
    wx.wxEVT_MOTION: "mouse_move",
    wx.wxEVT_ENTER_WINDOW: "enter",
    wx.wxEVT_LEAVE_WINDOW: "leave",
    wx.wxEVT_MOUSEWHEEL: "mouse_wheel",
    wx.wxEVT_PAINT: "paint",
}

#: Types of popup views:
Popups = {"popup", "popover", "info"}


# -------------------------------------------------------------------------
# Traits UI dispatch infrastructure
# -------------------------------------------------------------------------


def ui_handler(handler, *args):
    """Handles UI notification handler requests that occur on a thread other
    than the UI thread.
    """
    wx.CallAfter(handler, *args)


# Tell the traits notification handlers to use this UI handler
set_ui_handler(ui_handler)


# -------------------------------------------------------------------------
# Wx Toolkit Implementation
# -------------------------------------------------------------------------


class GUIToolkit(Toolkit):
    """Implementation class for wxPython toolkit."""

    def ui_panel(self, ui, parent):
        """Creates a wxPython panel-based user interface using information
        from the specified UI object.
        """
        from . import ui_panel

        ui_panel.ui_panel(ui, parent)

    def ui_subpanel(self, ui, parent):
        """Creates a wxPython subpanel-based user interface using information
        from the specified UI object.
        """
        from . import ui_panel

        ui_panel.ui_subpanel(ui, parent)

    def ui_livemodal(self, ui, parent):
        """Creates a wxPython modal "live update" dialog user interface using
        information from the specified UI object.
        """
        from . import ui_live

        ui_live.ui_livemodal(ui, parent)

    def ui_live(self, ui, parent):
        """Creates a wxPython non-modal "live update" window user interface
        using information from the specified UI object.
        """
        from . import ui_live

        ui_live.ui_live(ui, parent)

    def ui_modal(self, ui, parent):
        """Creates a wxPython modal dialog user interface using information
        from the specified UI object.
        """
        from . import ui_modal

        ui_modal.ui_modal(ui, parent)

    def ui_nonmodal(self, ui, parent):
        """Creates a wxPython non-modal dialog user interface using
        information from the specified UI object.
        """
        from . import ui_modal

        ui_modal.ui_nonmodal(ui, parent)

    def ui_popup(self, ui, parent):
        """Creates a wxPython temporary "live update" popup dialog user
        interface using information from the specified UI object.
        """
        from . import ui_live

        ui_live.ui_popup(ui, parent)

    def ui_popover(self, ui, parent):
        """Creates a wxPython temporary "live update" popup dialog user
        interface using information from the specified UI object.
        """
        from . import ui_live

        ui_live.ui_popover(ui, parent)

    def ui_info(self, ui, parent):
        """Creates a wxPython temporary "live update" popup dialog user
        interface using information from the specified UI object.
        """
        from . import ui_live

        ui_live.ui_info(ui, parent)

    def ui_wizard(self, ui, parent):
        """Creates a wxPython wizard dialog user interface using information
        from the specified UI object.
        """
        from . import ui_wizard

        ui_wizard.ui_wizard(ui, parent)

    def view_application(
        self,
        context,
        view,
        kind=None,
        handler=None,
        id="",
        scrollable=None,
        args=None,
    ):
        """Creates a wxPython modal dialog user interface that
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

        return view_application.view_application(
            context, view, kind, handler, id, scrollable, args
        )

    def position(self, ui):
        """Positions the associated dialog window on the display."""
        view = ui.view
        window = ui.control

        # Set up the default position of the window:
        parent = window.GetParent()
        if parent is None:
            px, py = 0, 0
            pdx = SystemMetrics().screen_width
            pdy = SystemMetrics().screen_height
        else:
            px, py = parent.GetPosition()
            pdx, pdy = parent.GetSize()

        # Calculate the correct width and height for the window:
        cur_width, cur_height = window.GetSize()
        width = view.width
        height = view.height

        if width < 0.0:
            width = cur_width
        elif width <= 1.0:
            width = int(width * SystemMetrics().screen_width)
        else:
            width = int(width)

        if height < 0.0:
            height = cur_height
        elif height <= 1.0:
            height = int(height * SystemMetrics().screen_height)
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
            x = px + (pdx - width) // 2
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
            y = py + (pdy - height) // 2
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
        window.SetSize(max(0, x), max(0, y), width, height)

    def show_help(self, ui, control):
        """Shows a help window for a specified UI and control."""
        from . import ui_panel

        ui_panel.show_help(ui, control)

    def save_window(self, ui):
        """Saves user preference information associated with a UI window."""
        from . import helper

        helper.save_window(ui)

    def rebuild_ui(self, ui):
        """Rebuilds a UI after a change to the content of the UI."""
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

    def set_title(self, ui):
        """Sets the title for the UI window."""
        ui.control.SetTitle(ui.title)

    def set_icon(self, ui):
        """Sets the icon for the UI window."""
        from pyface.image_resource import ImageResource

        if isinstance(ui.icon, ImageResource):
            ui.control.SetIcon(ui.icon.create_icon())

    def key_event_to_name(self, event):
        """Converts a keystroke event into a corresponding key name."""
        from . import key_event_to_name

        return key_event_to_name.key_event_to_name(event)

    def hook_events(self, ui, control, events=None, handler=None):
        """Hooks all specified events for all controls in a UI so that they
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
                wx.wxEVT_PAINT,
            )
            control.SetDropTarget(
                PythonDropTarget(DragHandler(ui=ui, control=control))
            )
        elif events == "keys":
            events = (wx.wxEVT_CHAR,)

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

    def route_event(self, ui, event):
        """Routes a hooked event to the correct handler method."""
        suffix = EventSuffix[event.GetEventType()]
        control = event.GetEventObject()
        handler = ui.handler
        method = None

        owner = getattr(control, "_owner", None)
        if owner is not None:
            method = getattr(
                handler, "on_%s_%s" % (owner.get_id(), suffix), None
            )

        if method is None:
            method = getattr(handler, "on_%s" % suffix, None) or getattr(
                handler, "on_any_event", None
            )

        if (method is None) or (method(ui.info, owner, event) is False):
            event.Skip()

    def skip_event(self, event):
        """Indicates that an event should continue to be processed by the
        toolkit.
        """
        event.Skip()

    def destroy_control(self, control):
        """Destroys a specified GUI toolkit control."""
        _popEventHandlers(control)

        def _destroy_control(control):
            try:
                control.Destroy()
            except Exception:
                logger.exception(
                    "Wx control %r not destroyed cleanly", control
                )

        wx.CallAfter(_destroy_control, control)

    def destroy_children(self, control):
        """Destroys all of the child controls of a specified GUI toolkit
        control.
        """
        for child in control.GetChildren():
            _popEventHandlers(child)
        wx.CallAfter(control.DestroyChildren)

    def image_size(self, image):
        """Returns a ( width, height ) tuple containing the size of a
        specified toolkit image.
        """
        return (image.GetWidth(), image.GetHeight())

    def constants(self):
        """Returns a dictionary of useful constants.

        Currently, the dictionary should have the following key/value pairs:

        - WindowColor': the standard window background color in the toolkit
          specific color format.
        """
        return {"WindowColor": WindowColor}

    # -------------------------------------------------------------------------
    #  GUI toolkit dependent trait definitions:
    # -------------------------------------------------------------------------

    def color_trait(self, *args, **traits):
        from . import color_trait as ct

        return ct.WxColor(*args, **traits)

    def rgb_color_trait(self, *args, **traits):
        from . import rgb_color_trait as rgbct

        return rgbct.RGBColor(*args, **traits)

    def font_trait(self, *args, **traits):
        from . import font_trait as ft

        return ft.WxFont(*args, **traits)


class DragHandler(HasPrivateTraits):
    """Handler for drag events."""

    # -------------------------------------------------------------------------
    #  Traits definitions:
    # -------------------------------------------------------------------------

    #: The UI associated with the drag handler
    ui = Instance(UI)

    #: The wx control associated with the drag handler
    control = Instance(wx.Window)

    # -- Drag and drop event handlers: ----------------------------------------

    def wx_dropped_on(self, x, y, data, drag_result):
        """Handles a Python object being dropped on the window."""
        return self._drag_event("dropped_on", x, y, data, drag_result)

    def wx_drag_over(self, x, y, data, drag_result):
        """Handles a Python object being dragged over the tree."""
        return self._drag_event("drag_over", x, y, data, drag_result)

    def wx_drag_leave(self, data):
        """Handles a dragged Python object leaving the window."""
        return self._drag_event("drag_leave")

    def _drag_event(self, suffix, x=None, y=None, data=None, drag_result=None):
        """Handles routing a drag event to the appropriate handler."""
        control = self.control
        handler = self.ui.handler
        method = None

        owner = getattr(control, "_owner", None)
        if owner is not None:
            method = getattr(
                handler, "on_%s_%s" % (owner.get_id(), suffix), None
            )

        if method is None:
            method = getattr(handler, "on_%s" % suffix, None)

        if method is None:
            return wx.DragNone

        if x is None:
            result = method(self.ui.info, owner)
        else:
            result = method(self.ui.info, owner, x, y, data, drag_result)
        if result is None:
            result = drag_result
        return result


class EventHandlerWrapper(wx.EvtHandler):
    """Simple wrapper around wx.EvtHandler used to determine which event
    handlers were added by traitui.
    """

    pass


def _popEventHandlers(ctrl, handler_type=EventHandlerWrapper):
    """Pop any event handlers that have been pushed on to a window and its
    children.
    """
    # FIXME: have to special case URLResolvingHtmlWindow because it doesn't
    # want its EvtHandler cleaned up.  See issue #752.
    from .html_editor import URLResolvingHtmlWindow

    handler = ctrl.GetEventHandler()
    while ctrl is not handler:
        next_handler = handler.GetNextHandler()
        if isinstance(handler, handler_type):
            ctrl.PopEventHandler(True)
        handler = next_handler
    for child in ctrl.GetChildren():
        _popEventHandlers(child, handler_type)
