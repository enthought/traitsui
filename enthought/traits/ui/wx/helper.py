#------------------------------------------------------------------------------
#
#  Copyright (c) 2005, Enthought, Inc.
#  All rights reserved.
#  
#  This software is provided without warranty under the terms of the BSD
#  license included in enthought/LICENSE.txt and may be redistributed only
#  under the conditions described in the aforementioned license.  The license
#  is also available online at http://www.enthought.com/licenses/BSD.txt
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
import sys

from os.path \
    import join, dirname, abspath
    
from constants \
    import standard_bitmap_width, screen_dx, screen_dy
    
from enthought.traits.api \
    import HasPrivateTraits, Enum, Trait, CTrait, Instance, Str, Any, Int, \
           Event, Bool, BaseTraitHandler, TraitError
    
from enthought.traits.ui.api \
    import View
    
from enthought.traits.ui.ui_traits \
    import SequenceTypes

from enthought.pyface.timer.api \
    import do_later
    
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
#  Positions one window near another:
#-------------------------------------------------------------------------------

def position_near ( origin, target, offset_x = 0, offset_y = 0, 
                                    align_x  = 1, align_y  = 1 ):
    """ Positions one window near another.
    """
    # Calculate the target window position relative to the origin window:                                         
    x, y     = origin.ClientToScreenXY( 0, 0 )
    dx, dy   = target.GetSizeTuple()
    odx, ody = origin.GetSizeTuple()
    if align_x < 0:
        x = x + odx - dx
    if align_y < 0:
        y = y + ody - dy
    x += offset_x
    y += offset_y
    
    # Position the target window (making sure it will fit on the screen):
    target.SetPosition( wx.Point( max( 0, min( x, screen_dx - dx ) ),
                                  max( 0, min( y, screen_dy - dy ) ) ) )
    
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
#  Restores the user preference items for a specified UI:
#-------------------------------------------------------------------------------
    
def restore_window ( ui ):
    """ Restores the user preference items for a specified UI.
    """
    prefs = ui.restore_prefs()
    if prefs is not None:
        ui.control.SetDimensions( *prefs )
    
#-------------------------------------------------------------------------------
#  Saves the user preference items for a specified UI:
#-------------------------------------------------------------------------------
    
def save_window ( ui ):
    """ Saves the user preference items for a specified UI.
    """
    control = ui.control
    ui.save_prefs( control.GetPositionTuple() + control.GetSizeTuple() ) 

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
#  PopupControl' class:
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
                    
