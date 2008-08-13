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

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

import wx
import wx.lib.scrolledpanel

import sys

from os.path \
    import join, dirname, abspath
    
from enthought.traits.api \
    import HasPrivateTraits, Enum, Trait, CTrait, Instance, Str, Any, Int, \
           Event, Bool, BaseTraitHandler, TraitError
    
from enthought.traits.ui.api \
    import View
    
from enthought.traits.ui.ui_traits \
    import convert_image, SequenceTypes

from enthought.pyface.timer.api \
    import do_later
    
from constants \
    import standard_bitmap_width, screen_dx, screen_dy
    
from editor \
    import Editor

#-------------------------------------------------------------------------------
#  Trait definitions:  
#-------------------------------------------------------------------------------

# Layout orientation for a control and its associated editor
Orientation = Enum( 'horizontal', 'vertical' )

#-------------------------------------------------------------------------------
#  Data:
#-------------------------------------------------------------------------------

# Bitmap cache dictionary (indexed by filename)
_bitmap_cache = {}

### NOTE: This needs major improvements:

app_path    = None
traits_path = None

#-------------------------------------------------------------------------------
#  Convert an image file name to a cached bitmap:
#-------------------------------------------------------------------------------

def bitmap_cache ( name, standard_size, path = None ):
    """ Converts an image file name to a cached bitmap.
    """
    global app_path, traits_path
    
    if name[:1] == '@':
        image = convert_image( name.replace( ' ', '_' ).lower() )
        if image is not None:
            return image.create_image().ConvertToBitmap()
            
    if path is None:
        if traits_path is None:
           import  enthought.traits.ui.wx
           traits_path = join( dirname( enthought.traits.ui.wx.__file__ ), 
                               'images' )
        path = traits_path
    elif path == '':
        if app_path is None:
            app_path = join( dirname( sys.argv[0] ), '..', 'images' )
        path = app_path
        
    filename = abspath( join( path, name.replace( ' ', '_' ).lower() + '.gif' ))
    bitmap   = _bitmap_cache.get( filename + ('*'[ not standard_size: ]) )
    if bitmap is not None:
        return bitmap
        
    std_bitmap = bitmap = wx.BitmapFromImage( wx.Image( filename ) )
    _bitmap_cache[ filename ] = bitmap
    
    dx = bitmap.GetWidth()
    if dx < standard_bitmap_width:
        dy = bitmap.GetHeight()
        std_bitmap = wx.EmptyBitmap( standard_bitmap_width, dy )
        dc1 = wx.MemoryDC()
        dc2 = wx.MemoryDC()
        dc1.SelectObject( std_bitmap )
        dc2.SelectObject( bitmap )
        dc1.SetPen( wx.TRANSPARENT_PEN )
        dc1.SetBrush( wx.WHITE_BRUSH )
        dc1.DrawRectangle( 0, 0, standard_bitmap_width, dy )
        dc1.Blit( (standard_bitmap_width - dx) / 2, 0, dx, dy, dc2, 0, 0 ) 
        
    _bitmap_cache[ filename + '*' ] = std_bitmap
    
    if standard_size:
        return std_bitmap
        
    return bitmap
    
#-------------------------------------------------------------------------------
#  Returns an appropriate width for a wxChoice widget based upon the list of
#  values it contains:
#-------------------------------------------------------------------------------
    
def choice_width ( values ):
    """ Returns an appropriate width for a wxChoice widget based upon the list 
        of values it contains:
    """
    return max( [ len( x ) for x in values ] ) * 6
    
#-------------------------------------------------------------------------------
#  Saves the user preference items for a specified UI:
#-------------------------------------------------------------------------------
    
def save_window ( ui ):
    """ Saves the user preference items for a specified UI.
    """
    control = ui.control
    ui.save_prefs( control.GetPositionTuple() + control.GetSizeTuple() ) 
    
#-------------------------------------------------------------------------------
#  Restores the user preference items for a specified UI:
#-------------------------------------------------------------------------------
    
def restore_window ( ui, is_popup = False ):
    """ Restores the user preference items for a specified UI.
    """
    prefs = ui.restore_prefs()
    if prefs is not None:
        x, y, dx, dy = prefs
        if is_popup:
            position_window( ui.control, dx, dy )
        else:
            ui.control.SetDimensions( x, y, dx, dy )

#-------------------------------------------------------------------------------
#  Positions a window on the screen with a specified width and height so that
#  the window completely fits on the screen if possible:
#-------------------------------------------------------------------------------

def position_window ( window, width = None, height = None, parent = None ):
    """ Positions a window on the screen with a specified width and height so 
        that the window completely fits on the screen if possible.
    """
    dx, dy = window.GetSizeTuple()
    width  = width  or dx
    height = height or dy
    
    if parent is None:
        parent = window._parent
    
    if parent is None:
        # Center the popup on the screen:
        window.SetDimensions( (screen_dx - width)  / 2, 
                              (screen_dy - height) / 2, width, height )
        return
        
    # Calculate the desired size of the popup control:
    if isinstance( parent, wx.Window ):
        x, y     = parent.ClientToScreenXY( 0, 0 )
        cdx, cdy = parent.GetSizeTuple()
    else:
        # Special case of parent being a screen position and size tuple (used 
        # to pop-up a dialog for a table cell):
        x, y, cdx, cdy = parent
        
    adjacent = (getattr( window, '_kind', 'popup' ) == 'popup')
    width    = min( max( cdx, width ), screen_dx )
    height   = min( height, screen_dy )
        
    # Calculate the best position and size for the pop-up:
    
    # Note: This code tries to deal with the fact that the user may have 
    # multiple monitors. wx does not report this information, so the screen_dx, 
    # screen_dy values usually just provide the size of the primary monitor. To 
    # get around this, the code assumes that the original (x,y) values are 
    # valid, and that all monitors are the same size. If this assumption is not
    # true, popups may appear in wierd positions on the secondary monitors.
    nx     = x % screen_dx
    xdelta = x - nx
    rx     = nx + cdx
    if (nx + width) > screen_dx:
        if (rx - width) < 0:
            nx = screen_dx - width
        else:
            nx = rx - width
    
    ny     = y % screen_dy
    ydelta = y - ny
    by     = ny
    if adjacent:
        by += cdy
    if (by + height) > screen_dy:
        if not adjacent:
            ny += cdy
        if (ny - height) < 0:
            ny = screen_dy - height
        else:
            by = ny - height
            
    # Position and size the window as requested:
    window.SetDimensions( nx + xdelta, by + ydelta, width, height )
    
#-------------------------------------------------------------------------------
#  Returns the top-level window for a specified control:
#-------------------------------------------------------------------------------

def top_level_window_for ( control ):
    """ Returns the top-level window for a specified control.
    """
    parent = control.GetParent()
    while parent is not None:
        control = parent
        parent  = control.GetParent()
        
    return control
    
#-------------------------------------------------------------------------------
#  Recomputes the mappings for a new set of enumeration values:
#-------------------------------------------------------------------------------
 
def enum_values_changed ( values ):
    """ Recomputes the mappings for a new set of enumeration values.
    """
    
    if isinstance( values, dict ):
        data = [ ( str( v ), n ) for n, v in values.items() ]
        if len( data ) > 0:
            data.sort( lambda x, y: cmp( x[0], y[0] ) )
            col = data[0][0].find( ':' ) + 1
            if col > 0:
                data = [ ( n[ col: ], v ) for n, v in data ]
    elif not isinstance( values, SequenceTypes ):
        handler = values
        if isinstance( handler, CTrait ):
            handler = handler.handler
        if not isinstance( handler, BaseTraitHandler ):
            raise TraitError, "Invalid value for 'values' specified"
        if handler.is_mapped:
            data = [ ( str( n ), n ) for n in handler.map.keys() ]
            data.sort( lambda x, y: cmp( x[0], y[0] ) )
        else:
            data = [ ( str( v ), v ) for v in handler.values ]
    else:
        data = [ ( str( v ), v ) for v in values ]
    
    names           = [ x[0] for x in data ]
    mapping         = {}
    inverse_mapping = {}
    for name, value in data:
        mapping[ name ] = value
        inverse_mapping[ value ] = name
        
    return ( names, mapping, inverse_mapping )  

#-------------------------------------------------------------------------------
#  Creates a wx.Panel that correctly sets its background color to be the same
#  as its parents:
#-------------------------------------------------------------------------------
                
def traits_ui_panel ( parent, *args, **kw ):
    """ Creates a wx.Panel that correctly sets its background color to be the 
        same as its parents.
    """
    panel = wx.Panel( parent, *args, **kw )
    panel.SetBackgroundColour( parent.GetBackgroundColour() )
                            
    # Set up the painting event handlers:
    wx.EVT_ERASE_BACKGROUND( panel, _erase_background )
    wx.EVT_PAINT( panel, _on_paint )
    
    return panel
    
def _erase_background ( event ):
    """ Do not erase the background here (do it in the 'on_paint' handler).
    """
    pass
           
def _on_paint ( event ):
    """ Paint the background using the associated ImageSlice object.
    """
    from image_slice import paint_parent
    
    control = event.GetEventObject()
    paint_parent( wx.PaintDC( control ), control )
    
    
    
#-------------------------------------------------------------------------------
#  Creates a wx.ScrolledWindow that correctly sets its background color to be
#  the same as its parents:
#-------------------------------------------------------------------------------

def traits_ui_scrolled_window ( parent ):
    """ Creates a wx.ScrolledWindow that correctly sets its background color to 
        be the same as its parents.
    """
    sw = wx.ScrolledWindow( parent )
    sw.SetBackgroundColour( parent.GetBackgroundColour() )
    
    return sw
    
#-------------------------------------------------------------------------------
#  Disconnects a wx event handle from its associated control:
#-------------------------------------------------------------------------------

def disconnect ( control, *events ):
    """ Disconnects a wx event handle from its associated control.
    """
    id = control.GetId()
    for event in events:
        event( control, id, None )

def disconnect_no_id ( control, *events ):
    """ Disconnects a wx event handle from its associated control.
    """
    for event in events:
        event( control, None )

#-------------------------------------------------------------------------------
#  'ScrolledPanel' class:
#-------------------------------------------------------------------------------

class ScrolledPanel ( wx.lib.scrolledpanel.ScrolledPanel ):
    
    def ScrollChildIntoView ( self, child ):
        """ Scrolls the panel such that the specified child window is in view.
            This method overrides the original in the base class so that
            nested subpanels are handled correctly.
        """        
        sppux, sppuy = self.GetScrollPixelsPerUnit()
        vsx, vsy     = self.GetViewStart()

        subwindow = child.FindFocus()
        crx, cry, crdx, crdy = subwindow.GetRect()
        while subwindow is not child:
            subwindow = subwindow.GetParent()
            pwx,pwy   = subwindow.GetRect()[:2]
            crx, cry  = crx + pwx, cry + pwy
            
        cr = wx.Rect( crx, cry, crdx, crdy )
        
        client_size      = self.GetClientSize()
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
            self.Scroll( new_vsx, new_vsy )


def traits_ui_scrolled_panel ( parent, *args, **kw ):
    """ Creates a wx.Panel that correctly sets its background color to be the
        same as its parents.
    """
    panel = ScrolledPanel( parent, *args, **kw )
    panel.SetBackgroundColour( parent.GetBackgroundColour() )

    return panel

#-------------------------------------------------------------------------------
#  Initializes standard wx event handlers for a specified control and object:
#-------------------------------------------------------------------------------
        
# Standard wx event handlers:    
handlers = ( 
    ( wx.EVT_ERASE_BACKGROUND, '_erase_background' ),
    ( wx.EVT_PAINT,            '_paint' ),
    ( wx.EVT_SIZE,             '_size' ),
    ( wx.EVT_LEFT_DOWN,        '_left_down' ),
    ( wx.EVT_LEFT_UP,          '_left_up' ),
    ( wx.EVT_LEFT_DCLICK,      '_left_dclick' ),
    ( wx.EVT_MIDDLE_DOWN,      '_middle_down' ),
    ( wx.EVT_MIDDLE_UP,        '_middle_up' ),
    ( wx.EVT_MIDDLE_DCLICK,    '_middle_dclick' ),
    ( wx.EVT_RIGHT_DOWN,       '_right_down' ),
    ( wx.EVT_RIGHT_UP,         '_right_up' ),
    ( wx.EVT_RIGHT_DCLICK,     '_right_dclick' ),
    ( wx.EVT_MOTION,           '_motion' )
)    
    
def init_wx_handlers ( control, object, prefix = '' ):
    """ Initializes a standard set of wx event handlers for a specified control
        and object using a specified prefix.
    """
    global handlers
    
    for handler, name in handlers:
        method = getattr( object, prefix + name, None )
        if method is not None:
            handler( control, method )


#-------------------------------------------------------------------------------
#  Safely tries to pop up an FBI window if enthought.debug is installed
#-------------------------------------------------------------------------------

def open_fbi():
    try:
        from enthought.developer.helper.fbi import if_fbi
        if not if_fbi():
            import traceback
            traceback.print_exc()
    except ImportError:
        pass

#-------------------------------------------------------------------------------
#  'GroupEditor' class:
#-------------------------------------------------------------------------------
        
class GroupEditor ( Editor ):
    
    #---------------------------------------------------------------------------
    #  Initializes the object:
    #---------------------------------------------------------------------------
    
    def __init__ ( self, **traits ):
        """ Initializes the object.
        """
        self.set( **traits )
        
#-------------------------------------------------------------------------------
#  'PopupControl' class:
#-------------------------------------------------------------------------------

class PopupControl ( HasPrivateTraits ):

    #-- Constructor Traits -----------------------------------------------------
    
    # The control the popup should be positioned relative to:
    control = Instance( wx.Window )
    
    # The minimum width of the popup:
    width = Int
    
    # The minimum height of the popup:
    height = Int
    
    # Should the popup be resizable?
    resizable = Bool( False )
    
    #-- Public Traits ----------------------------------------------------------
    
    # The value (if any) set by the popup control:
    value = Any
    
    # Event fired when the popup control is closed:
    closed = Event
    
    #-- Private Traits ---------------------------------------------------------
    
    # The popup control:
    popup = Instance( wx.Window )
    
    #-- Public Methods ---------------------------------------------------------
    
    def __init__ ( self, **traits ):
        """ Initializes the object.
        """
        super( PopupControl, self ).__init__( **traits )
        
        style = wx.SIMPLE_BORDER
        if self.resizable:
            style = wx.RESIZE_BORDER
            
        self.popup = popup = wx.Frame( None, -1, '', style = style )
        wx.EVT_ACTIVATE( popup, self._on_close_popup )
        self.create_control( popup )
        self._position_control()
        popup.Show()

    def create_control ( self ):
        """ Creates the control. 
        
            Must be overridden by a subclass.
        """
        raise NotImplementedError

    def dispose ( self ):
        """ Called when the popup is being closed to allow any custom clean-up.
            
            Can be overridden by a subclass.
        """
        pass
        
    #-- Event Handlers ---------------------------------------------------------
    
    def _value_changed ( self, value ):
        """ Handles the 'value' being changed.
        """
        do_later( self._close_popup )
        
    #-- Private Methods --------------------------------------------------------
    
    def _position_control ( self ):
        """ Initializes the popup control's initial position and size.
        """
        # Calculate the desired size of the popup control:
        px,  cy  = self.control.ClientToScreenXY( 0, 0 )
        cdx, cdy = self.control.GetSizeTuple()
        pdx, pdy = self.popup.GetSizeTuple()
        pdx, pdy = max( pdx, cdx, self.width ), max( pdy, self.height )
        
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
        self.popup.SetDimensions( px, py, pdx, pdy )
        
    def _on_close_popup ( self, event ):
        """ Closes the popup control when it is deactivated.
        """
        if not event.GetActive():
            self._close_popup()
 
    def _close_popup ( self ):
        """ Closes the dialog.
        """
        wx.EVT_ACTIVATE( self.popup, None )
        self.dispose()
        self.closed = True
        self.popup.Destroy()
        self.popup = self.control = None
                    
