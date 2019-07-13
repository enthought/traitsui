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
#  Date:   10/25/2004
#
#------------------------------------------------------------------------------

""" Defines helper functions and classes used to define wxPython-based trait
    editors and trait editor factories.
"""

#-------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------

from __future__ import absolute_import
from operator import itemgetter

import wx
import wx.lib.scrolledpanel

import sys

from os.path \
    import join, dirname, abspath

from traits.api \
    import HasPrivateTraits, Enum, CTrait, Instance, Any, Int, \
    Event, Bool, BaseTraitHandler, TraitError

from traitsui.ui_traits \
    import convert_image, SequenceTypes

from pyface.timer.api \
    import do_later

from .constants \
    import standard_bitmap_width, screen_dx, screen_dy

from .editor \
    import Editor
import six


#-------------------------------------------------------------------------
#  Trait definitions:
#-------------------------------------------------------------------------

# Layout orientation for a control and its associated editor
Orientation = Enum('horizontal', 'vertical')

#-------------------------------------------------------------------------
#  Data:
#-------------------------------------------------------------------------

# Bitmap cache dictionary (indexed by filename)
_bitmap_cache = {}

### NOTE: This needs major improvements:

app_path = None
traits_path = None

#-------------------------------------------------------------------------
#  Convert an image file name to a cached bitmap:
#-------------------------------------------------------------------------


def bitmap_cache(name, standard_size, path=None):
    """ Converts an image file name to a cached bitmap.
    """
    global app_path, traits_path

    if name[:1] == '@':
        image = convert_image(name.replace(' ', '_').lower())
        if image is not None:
            return image.create_image().ConvertToBitmap()

    if path is None:
        if traits_path is None:
            import traitsui.wx
            traits_path = join(dirname(traitsui.wx.__file__),
                               'images')
        path = traits_path
    elif path == '':
        if app_path is None:
            app_path = join(dirname(sys.argv[0]), '..', 'images')
        path = app_path

    filename = abspath(join(path, name.replace(' ', '_').lower() + '.gif'))
    bitmap = _bitmap_cache.get(filename + ('*'[not standard_size:]))
    if bitmap is not None:
        return bitmap

    std_bitmap = bitmap = wx.BitmapFromImage(wx.Image(filename))
    _bitmap_cache[filename] = bitmap

    dx = bitmap.GetWidth()
    if dx < standard_bitmap_width:
        dy = bitmap.GetHeight()
        std_bitmap = wx.EmptyBitmap(standard_bitmap_width, dy)
        dc1 = wx.MemoryDC()
        dc2 = wx.MemoryDC()
        dc1.SelectObject(std_bitmap)
        dc2.SelectObject(bitmap)
        dc1.SetPen(wx.TRANSPARENT_PEN)
        dc1.SetBrush(wx.WHITE_BRUSH)
        dc1.DrawRectangle(0, 0, standard_bitmap_width, dy)
        dc1.Blit((standard_bitmap_width - dx) / 2, 0, dx, dy, dc2, 0, 0)

    _bitmap_cache[filename + '*'] = std_bitmap

    if standard_size:
        return std_bitmap

    return bitmap

#-------------------------------------------------------------------------
#  Returns an appropriate width for a wxChoice widget based upon the list of
#  values it contains:
#-------------------------------------------------------------------------


def choice_width(values):
    """ Returns an appropriate width for a wxChoice widget based upon the list
        of values it contains:
    """
    return max([len(x) for x in values]) * 6

#-------------------------------------------------------------------------
#  Saves the user preference items for a specified UI:
#-------------------------------------------------------------------------


def save_window(ui):
    """ Saves the user preference items for a specified UI.
    """
    control = ui.control
    ui.save_prefs(control.GetPositionTuple() + control.GetSizeTuple())

#-------------------------------------------------------------------------
#  Restores the user preference items for a specified UI:
#-------------------------------------------------------------------------


def restore_window(ui, is_popup=False):
    """ Restores the user preference items for a specified UI.
    """
    prefs = ui.restore_prefs()
    if prefs is not None:
        x, y, dx, dy = prefs

        # Check to see if the window's position is within a display.
        # If it is not entirely within 1 display, move it and/or
        # resize it to the closest window

        closest = find_closest_display(x, y)
        x, y, dx, dy = get_position_for_display(x, y, dx, dy, closest)

        if is_popup:
            position_window(ui.control, dx, dy)
        else:
            if (dx, dy) == (0, 0):
                # The window was saved minimized
                ui.control.SetDimensions(x, y, -1, -1)
            else:
                ui.control.SetDimensions(x, y, dx, dy)


def find_closest_display(x, y):
    """ For a virtual screen position, find the closest display.
        There are a few reasons to use this function:
            * the number of displays changed
            * the size of the displays changed
            * the orientation of one or more displays changed.
    """
    closest = None
    for display_num in range(wx.Display.GetCount()):
        display = wx.Display(display_num)
        if closest is None:
            closest = display
        else:
            def _distance(x, y, display):
                dis_x, dis_y, dis_w, dis_h = display.GetGeometry()
                dis_mid_x = dis_x + dis_w / 2
                dis_mid_y = dis_y + dis_h / 2

                return (x - dis_mid_x)**2 + (y - dis_mid_y)**2

            if _distance(x, y, display) < _distance(x, y, closest):
                closest = display

    return closest


def get_position_for_display(x, y, dx, dy, display):
    """ calculates a valid position and size for a window to fit
        inside a display
    """
    dis_x, dis_y, dis_w, dis_h = display.GetGeometry()
    dx = min(dx, dis_w)
    dy = min(dy, dis_h)
    if ((x + dx) > (dis_x + dis_w)) or (x < dis_x):
        x = dis_x
    if ((y + dy) > (dis_y + dis_h)) or (y < dis_y):
        y = dis_y

    return x, y, dx, dy

#-------------------------------------------------------------------------
#  Positions a window on the screen with a specified width and height so that
#  the window completely fits on the screen if possible:
#-------------------------------------------------------------------------


def position_window(window, width=None, height=None, parent=None):
    """ Positions a window on the screen with a specified width and height so
        that the window completely fits on the screen if possible.
    """
    dx, dy = window.GetSizeTuple()
    width = width or dx
    height = height or dy

    if parent is None:
        parent = window._parent

    if parent is None:
        # Center the popup on the screen:
        window.SetDimensions((screen_dx - width) / 2,
                             (screen_dy - height) / 2, width, height)
        return

    # Calculate the desired size of the popup control:
    if isinstance(parent, wx.Window):
        x, y = parent.ClientToScreenXY(0, 0)
        parent_dx, parent_dy = parent.GetSizeTuple()
    else:
        # Special case of parent being a screen position and size tuple (used
        # to pop-up a dialog for a table cell):
        x, y, parent_dx, parent_dy = parent

    adjacent = (getattr(window, '_kind', 'popup') == 'popup')
    width = min(max(parent_dx, width), screen_dx)
    height = min(height, screen_dy)

    closest = find_closest_display(x, y)

    if adjacent:
        y += parent_dy

    x, y, dx, dy = get_position_for_display(x, y, width, height, closest)

    window.SetDimensions(x, y, dx, dy)

#-------------------------------------------------------------------------
#  Returns the top-level window for a specified control:
#-------------------------------------------------------------------------


def top_level_window_for(control):
    """ Returns the top-level window for a specified control.
    """
    parent = control.GetParent()
    while parent is not None:
        control = parent
        parent = control.GetParent()

    return control

#-------------------------------------------------------------------------
#  Recomputes the mappings for a new set of enumeration values:
#-------------------------------------------------------------------------


def enum_values_changed(values):
    """ Recomputes the mappings for a new set of enumeration values.
    """

    if isinstance(values, dict):
        data = [(six.text_type(v), n) for n, v in values.items()]
        if len(data) > 0:
            data.sort(key=itemgetter(0))
            col = data[0][0].find(':') + 1
            if col > 0:
                data = [(n[col:], v) for n, v in data]
    elif not isinstance(values, SequenceTypes):
        handler = values
        if isinstance(handler, CTrait):
            handler = handler.handler
        if not isinstance(handler, BaseTraitHandler):
            raise TraitError("Invalid value for 'values' specified")
        if handler.is_mapped:
            data = [(six.text_type(n), n) for n in handler.map.keys()]
            data.sort(key=itemgetter(0))
        else:
            data = [(six.text_type(v), v) for v in handler.values]
    else:
        data = [(six.text_type(v), v) for v in values]

    names = [x[0] for x in data]
    mapping = {}
    inverse_mapping = {}
    for name, value in data:
        mapping[name] = value
        inverse_mapping[value] = name

    return (names, mapping, inverse_mapping)

#-------------------------------------------------------------------------
#  Disconnects a wx event handle from its associated control:
#-------------------------------------------------------------------------


def disconnect(control, *events):
    """ Disconnects a wx event handle from its associated control.
    """
    id = control.GetId()
    for event in events:
        event(control, id, None)


def disconnect_no_id(control, *events):
    """ Disconnects a wx event handle from its associated control.
    """
    for event in events:
        event(control, None)

#-------------------------------------------------------------------------
#  Creates a wx.Panel that correctly sets its background color to be the same
#  as its parents:
#-------------------------------------------------------------------------


class TraitsUIPanel(wx.Panel):

    def __init__(self, parent, *args, **kw):
        """ Creates a wx.Panel that correctly sets its background color to be
            the same as its parents.
        """
        bg_color = kw.pop('bg_color', None)
        wx.Panel.__init__(self, parent, *args, **kw)

        wx.EVT_CHILD_FOCUS(self, self.OnChildFocus)

        if bg_color:
            self.SetBackgroundColour(bg_color)
        else:
            # Mac/Win needs this, otherwise background color is black
            attr = self.GetDefaultAttributes()
            self.SetBackgroundColour(attr.colBg)

    def OnChildFocus(self, event):
        """ If the ChildFocusEvent contains one of the Panel's direct children,
            then we will Skip it to let it pass up the widget hierarchy.

            Otherwise, we consume the event to make sure it doesn't go any
            farther. This works around a problem in wx 2.8.8.1 where each Panel
            in a nested hierarchy generates many events that might consume too
            many resources. We do, however, let one event bubble up to the top
            so that it may inform a top-level ScrolledPanel that a descendant
            has acquired focus.
        """
        if event.GetWindow() in self.GetChildren():
            event.Skip()

#-------------------------------------------------------------------------
#  'ChildFocusOverride' class:
#-------------------------------------------------------------------------

# PyEvtHandler was only introduced in wxPython 2.8.8. Fortunately, it is only
# necessary in wxPython 2.8.8.
if wx.__version__ < '2.8.8':

    class ChildFocusOverride(object):

        def __init__(self, window):
            # Set up the event listener.
            window.Bind(wx.EVT_CHILD_FOCUS, window.OnChildFocus)

else:

    class ChildFocusOverride(wx.PyEvtHandler):
        """ Override the scroll-to-focus behaviour in wx 2.8.8's ScrolledWindow
            C++ implementation for ScrolledPanel.

            Instantiating this class with the ScrolledPanel will register the
            new instance as the event handler for the panel.
        """

        def __init__(self, window):
            self.window = window
            wx.PyEvtHandler.__init__(self)

            # Make self the event handler for the window.
            window.PushEventHandler(self)

        def ProcessEvent(self, event):
            if isinstance(event, wx.ChildFocusEvent):
                # Handle this one with our code and don't let the C++ event handler
                # get it.
                return self.window.OnChildFocus(event)
            else:
                # Otherwise, just pass this along in the event handler chain.
                result = self.GetNextHandler().ProcessEvent(event)
                return result

#-------------------------------------------------------------------------
#  'TraitsUIScrolledPanel' class:
#-------------------------------------------------------------------------


class TraitsUIScrolledPanel(wx.lib.scrolledpanel.ScrolledPanel):

    def __init__(self, parent, id=-1, pos=wx.DefaultPosition,
                 size=wx.DefaultSize, style=wx.TAB_TRAVERSAL,
                 name="scrolledpanel"):

        wx.PyScrolledWindow.__init__(self, parent, id, pos=pos, size=size,
                                     style=style, name=name)
        # FIXME: The ScrolledPanel class calls SetInitialSize in its __init__
        # method, but for some reason, that leads to very a small window size.
        # Calling SetSize seems to work okay, but its not clear why
        # SetInitialSize does not work.
        self.SetSize(size)
        self.SetBackgroundColour(parent.GetBackgroundColour())

        # Override the C++ ChildFocus event handler:
        ChildFocusOverride(self)

    def OnChildFocus(self, event):
        """ Handle a ChildFocusEvent.

        Returns a boolean so it can be used as a library call, too.
        """
        self.ScrollChildIntoView(self.FindFocus())

        return True

    def ScrollChildIntoView(self, child):
        """ Scrolls the panel such that the specified child window is in view.
            This method overrides the original in the base class so that
            nested subpanels are handled correctly.
        """
        if child is None:
            return

        sppux, sppuy = self.GetScrollPixelsPerUnit()
        vsx, vsy = self.GetViewStart()

        crx, cry, crdx, crdy = child.GetRect()
        subwindow = child.GetParent()
        while subwindow not in [self, None]:
            # Make sure that the descendant's position information is relative
            # to us, not its local parent.
            pwx, pwy = subwindow.GetRect()[:2]
            crx, cry = crx + pwx, cry + pwy
            subwindow = subwindow.GetParent()

        cr = wx.Rect(crx, cry, crdx, crdy)

        client_size = self.GetClientSize()
        new_vsx, new_vsy = -1, -1

        # Is it before the left edge?
        if (cr.x < 0) and (sppux > 0):
            new_vsx = vsx + (cr.x / sppux)

        # Is it above the top?
        if (cr.y < 0) and (sppuy > 0):
            new_vsy = vsy + (cr.y / sppuy)

        # For the right and bottom edges, scroll enough to show the whole
        # control if possible, but if not just scroll such that the top/left
        # edges are still visible:

        # Is it past the right edge ?
        if (cr.right > client_size.width) and (sppux > 0):
            diff = (cr.right - client_size.width) / sppux
            if (cr.x - (diff * sppux)) > 0:
                new_vsx = vsx + diff + 1
            else:
                new_vsx = vsx + (cr.x / sppux)

        # Is it below the bottom ?
        if (cr.bottom > client_size.height) and (sppuy > 0):
            diff = (cr.bottom - client_size.height) / sppuy
            if (cr.y - (diff * sppuy)) > 0:
                new_vsy = vsy + diff + 1
            else:
                new_vsy = vsy + (cr.y / sppuy)

        # Perform the scroll if any adjustments are needed:
        if (new_vsx != -1) or (new_vsy != -1):
            self.Scroll(new_vsx, new_vsy)

#-------------------------------------------------------------------------
#  Initializes standard wx event handlers for a specified control and object:
#-------------------------------------------------------------------------

# Standard wx event handlers:
handlers = (
    (wx.EVT_ERASE_BACKGROUND, '_erase_background'),
    (wx.EVT_PAINT, '_paint'),
    (wx.EVT_SIZE, '_size'),
    (wx.EVT_LEFT_DOWN, '_left_down'),
    (wx.EVT_LEFT_UP, '_left_up'),
    (wx.EVT_LEFT_DCLICK, '_left_dclick'),
    (wx.EVT_MIDDLE_DOWN, '_middle_down'),
    (wx.EVT_MIDDLE_UP, '_middle_up'),
    (wx.EVT_MIDDLE_DCLICK, '_middle_dclick'),
    (wx.EVT_RIGHT_DOWN, '_right_down'),
    (wx.EVT_RIGHT_UP, '_right_up'),
    (wx.EVT_RIGHT_DCLICK, '_right_dclick'),
    (wx.EVT_MOTION, '_motion'),
    (wx.EVT_ENTER_WINDOW, '_enter'),
    (wx.EVT_LEAVE_WINDOW, '_leave'),
    (wx.EVT_MOUSEWHEEL, '_wheel')
)


def init_wx_handlers(control, object, prefix=''):
    """ Initializes a standard set of wx event handlers for a specified control
        and object using a specified prefix.
    """
    global handlers

    for handler, name in handlers:
        method = getattr(object, prefix + name, None)
        if method is not None:
            handler(control, method)

#-------------------------------------------------------------------------
#  'GroupEditor' class:
#-------------------------------------------------------------------------


class GroupEditor(Editor):

    #-------------------------------------------------------------------------
    #  Initializes the object:
    #-------------------------------------------------------------------------

    def __init__(self, **traits):
        """ Initializes the object.
        """
        self.trait_set(**traits)

#-------------------------------------------------------------------------
#  'PopupControl' class:
#-------------------------------------------------------------------------


class PopupControl(HasPrivateTraits):

    #-- Constructor Traits ---------------------------------------------------

    # The control the popup should be positioned relative to:
    control = Instance(wx.Window)

    # The minimum width of the popup:
    width = Int

    # The minimum height of the popup:
    height = Int

    # Should the popup be resizable?
    resizable = Bool(False)

    #-- Public Traits --------------------------------------------------------

    # The value (if any) set by the popup control:
    value = Any

    # Event fired when the popup control is closed:
    closed = Event

    #-- Private Traits -------------------------------------------------------

    # The popup control:
    popup = Instance(wx.Window)

    #-- Public Methods -------------------------------------------------------

    def __init__(self, **traits):
        """ Initializes the object.
        """
        super(PopupControl, self).__init__(**traits)

        style = wx.SIMPLE_BORDER
        if self.resizable:
            style = wx.RESIZE_BORDER

        self.popup = popup = wx.Frame(None, -1, '', style=style)
        wx.EVT_ACTIVATE(popup, self._on_close_popup)
        self.create_control(popup)
        self._position_control()
        popup.Show()

    def create_control(self):
        """ Creates the control.

            Must be overridden by a subclass.
        """
        raise NotImplementedError

    def dispose(self):
        """ Called when the popup is being closed to allow any custom clean-up.

            Can be overridden by a subclass.
        """
        pass

    #-- Event Handlers -------------------------------------------------------

    def _value_changed(self, value):
        """ Handles the 'value' being changed.
        """
        do_later(self._close_popup)

    #-- Private Methods ------------------------------------------------------

    def _position_control(self):
        """ Initializes the popup control's initial position and size.
        """
        # Calculate the desired size of the popup control:
        px, cy = self.control.ClientToScreenXY(0, 0)
        cdx, cdy = self.control.GetSizeTuple()
        pdx, pdy = self.popup.GetSizeTuple()
        pdx, pdy = max(pdx, cdx, self.width), max(pdy, self.height)

        # Calculate the best position and size for the pop-up:
        py = cy + cdy
        if (py + pdy) > screen_dy:
            if (cy - pdy) < 0:
                bottom = screen_dy - py
                if cy > bottom:
                    py, pdy = 0, cy
                else:
                    pdy = bottom
            else:
                py = cy - pdy

        # Finally, position the popup control:
        self.popup.SetDimensions(px, py, pdx, pdy)

    def _on_close_popup(self, event):
        """ Closes the popup control when it is deactivated.
        """
        if not event.GetActive():
            self._close_popup()

    def _close_popup(self):
        """ Closes the dialog.
        """
        wx.EVT_ACTIVATE(self.popup, None)
        self.dispose()
        self.closed = True
        self.popup.Destroy()
        self.popup = self.control = None

#-------------------------------------------------------------------------
#  'BufferDC' class:
#-------------------------------------------------------------------------


class BufferDC(wx.MemoryDC):
    """ An off-screen buffer class.

        This class implements a off-screen output buffer. Data is meant to
        be drawn in the buffer and then blitted directly to the output device
        context.
    """

    def __init__(self, dc, width=None, height=None):
        """Initializes the buffer."""
        wx.MemoryDC.__init__(self)

        # If only a single argument is passed, it is assumed to be a wx.Window
        # and that we have been created within a 'paint' event for that window:
        if width is None:
            width, height = dc.GetClientSize()
            dc = wx.PaintDC(dc)

        self.dc = dc
        self.bitmap = wx.EmptyBitmap(width, height)

        self.SelectObject(self.bitmap)

        self.SetFont(dc.GetFont())

    def copy(self, x=0, y=0):
        """ Performs the blit of the buffer contents to the specified device
            context location.
        """
        self.dc.Blit(x, y, self.bitmap.GetWidth(), self.bitmap.GetHeight(),
                     self, 0, 0)

#-------------------------------------------------------------------------
#  'Slider' class:
#-------------------------------------------------------------------------


class Slider(wx.Slider):
    """ This is a 'fixed' version of the wx.Slider control which does not
        erase its background, which can cause a lot of update flicker and is
        completely unnecessary.
    """

    def __init__(self, *args, **kw):
        super(Slider, self).__init__(*args, **kw)

        wx.EVT_ERASE_BACKGROUND(self, self._erase_background)

    def _erase_background(self, event):
        pass
