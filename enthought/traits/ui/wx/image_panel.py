#-------------------------------------------------------------------------------
#  
#  Defines a themed panel that wraps itself around a single child widget. 
#  
#  Written by: David C. Morrill
#  
#  Date: 08/11/2007
#  
#  (c) Copyright 2007 by Enthought, Inc.
#  
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

import wx

from enthought.traits.api \
    import Str, Property, Instance, cached_property
    
from themed_window \
    import ThemedWindow
    
from helper \
    import traits_ui_panel
    
#-------------------------------------------------------------------------------
#  Constants:
#-------------------------------------------------------------------------------

# Size of an empty text string:
ZeroTextSize = ( 0, 0, 0, 0 )
    
#-------------------------------------------------------------------------------
#  'ImagePanel' class:  
#-------------------------------------------------------------------------------    
                      
class ImagePanel ( ThemedWindow ):
    
    # The optional text to display in the top or bottom of the image slice:
    text = Str( event = 'updated' )
    
    # Is the image panel capable of displaying text?
    can_show_text = Property
    
    # The adjusted size of the panel, taking into account the size of its
    # current children and the image border:
    adjusted_size = Property
    
    # The best size of the panel, taking into account the best size of its
    # children and the image border:
    best_size = Property
    
    # The underlying wx control:
    control = Instance( wx.Window )

    #-- Private Traits ---------------------------------------------------------
    
    # The size of the current text:
    text_size = Property( depends_on = 'text, control' )
    
    #-- Public Methods ---------------------------------------------------------
    
    def create_control ( self, parent ):
        """ Creates the underlying wx.Panel control.
        """
        self.control = control = wx.Panel( parent, -1,
                          style = wx.TAB_TRAVERSAL | wx.FULL_REPAINT_ON_RESIZE )
    
        # Set up the sizer for the control:                                                   
        control.SetSizer( ImageSizer( self.theme ) )
                                                   
        # Initialize the control (set-up event handlers, ...)
        self.init_control()
                                                    
        # Attach the image slice to the control:
        control._image_slice = self.theme.image_slice
        
        # Set the panel's background colour to the image slice bg_color:
        control.SetBackgroundColour( control._image_slice.bg_color )
        
        return control
        
    #-- Property Implementations -----------------------------------------------
    
    def _get_adjusted_size ( self ):
        """ Returns the adjusted size of the panel taking into account the
            size of its current children and the image border.
        """
        control = self.control
        dx, dy  = 0, 0
        for child in control.GetChildren():
            dx, dy = child.GetSizeTuple()
            
        size = self._adjusted_size_of( dx, dy ) 
        control.SetSize( size )
        
        return size
    
    def _get_best_size ( self ):
        """ Returns the best size of the panel taking into account the
            best size of its current children and the image border.
        """
        control = self.control
        dx, dy  = 0, 0
        for child in control.GetChildren():
            dx, dy = child.GetBestSize()
            
        return self._adjusted_size_of( dx, dy ) 
        
    @cached_property
    def _get_can_show_text ( self ):
        """ Returns whether or not the image panel is capable of displaying
            text.
        """
        tdx, tdy, descent, leading = self.control.GetFullTextExtent( 'Myj' )
        slice = self.theme.image_slice
        tdy  += 4
        return ((tdy <= slice.xtop) or (tdy <= slice.xbottom) or
                (slice.xleft >= 40) or (slice.xright >= 40))
        
    @cached_property
    def _get_text_size ( self ):
        """ Returns the text size information for the window.
        """
        if (self.text == '') or (self.control is None):
            return ZeroTextSize
            
        return self.control.GetFullTextExtent( self.text )
        
    #-- Trait Event Handlers ---------------------------------------------------
    
    def _updated_changed ( self ):
        """ Handles a change that requires the control to be updated.
        """
        if self.control is not None:
            self.control.Refresh()

    def _theme_changed ( self, theme ):
        """ Handles the 'theme' trait being changed.
        """
        super( ImagePanel, self )._theme_changed()
        
        control = self.control
        if (control is not None) and (theme is not None):
            # Attach the image slice to the control:
            control._image_slice = theme.image_slice
            
            # Set the panel's background colour to the image slice bg_color:
            control.SetBackgroundColour( control._image_slice.bg_color )
        
    #-- wx.Python Event Handlers -----------------------------------------------
           
    def _paint ( self, event ):
        """ Paint the background using the associated ImageSlice object.
        """
        dc, slice = super( ImagePanel, self )._paint( event )
        
        # If we have text and have room to draw it, then do so:
        text = self.text
        if (text != '') and self.can_show_text:
            theme = self.theme
            dc.SetBackgroundMode( wx.TRANSPARENT )
            dc.SetTextForeground( theme.label_color )
            dc.SetFont( self.control.GetFont() )
            
            alignment = theme.alignment
            wdx, wdy  = self.control.GetClientSizeTuple()
            tdx, tdy, descent, leading = self.text_size
            tx = None
            if ((tdy + 4) <= slice.xtop) and (slice.xtop >= slice.xbottom):
                ty = (slice.xtop - tdy) / 2
            elif (tdy + 4) <= slice.xbottom:
                ty = wdy - ((slice.xbottom + tdy) / 2)
            else:
                ty = (wdy + slice.xtop - slice.xbottom - tdy) / 2
                if slice.xleft >= slice.xright:
                    if alignment == 'left':
                        tx = 4
                    elif alignment == 'right':
                        tx = slice.xleft - tdx - 4
                    else:
                        tx = (slice.xleft - tdx) / 2
                elif alignment == 'left':
                    tx = wdx - slice.xright + 4
                elif alignment == 'right':
                    tx = wdx - tdx - 4
                else:
                    tx = wdx - ((slice.xright + tdx) / 2)
                    
            if tx is None:
                if alignment == 'left':
                    tx = slice.left + 4
                elif alignment == 'right':
                    tx = wdx - tdx - slice.right - 4
                else:
                    tx = (wdx + slice.left - slice.right - tdx) / 2
                
            # fixme: Might need to set clipping region here...
            ox, oy = theme.label.left, theme.label.top
            dc.DrawText( text, tx + ox, ty + oy )
        
    #-- Private Methods --------------------------------------------------------
    
    def _adjusted_size_of ( self, dx, dy ):
        """ Returns the adjusted size of its children, taking into account the
            image slice border.
        """
        slice = self.theme.image_slice
        sizer = self.control.GetSizer()
        return wx.Size( dx + min( slice.left, slice.xleft )   + 
                             min( slice.right, slice.xright ) + 
                             sizer._left_padding + sizer._right_padding,
                        dy + min( slice.top, slice.xtop )       +
                             min( slice.bottom, slice.xbottom ) +
                             sizer._top_padding + sizer._bottom_padding )
            
#-------------------------------------------------------------------------------
#  'ImageSizer' class:
#-------------------------------------------------------------------------------

class ImageSizer ( wx.PySizer ):
    """ Defines a sizer that correctly sizes a window's children to fit within
        the borders implicitly defined by a background ImageSlice object,
    """

    #---------------------------------------------------------------------------
    #  Initializes the object:
    #---------------------------------------------------------------------------

    def __init__ ( self, theme ):
        """ Initializes the object.
        """
        super( ImageSizer, self ).__init__()
        
        # Save the ImageSlice object which determines the inset border size:
        self._image_slice = theme.image_slice
        
        # Save the padding information:
        content = theme.content
        if content is not None:
            self._left_padding   = content.left
            self._right_padding  = content.right
            self._top_padding    = content.top
            self._bottom_padding = content.bottom
        else:
            self._left_padding   = self._right_padding = self._top_padding = \
            self._bottom_padding = 0

    #---------------------------------------------------------------------------
    #  Calculates the minimum size needed by the sizer:
    #---------------------------------------------------------------------------

    def CalcMin ( self ):
        """ Calculates the minimum size of the control by adding its contents
            minimum size to the ImageSlice object's border size.
        """
        dx, dy = 0, 0
        for item in self.GetChildren():
            if item.IsSizer():
                dx, dy = item.GetSizer().CalcMin()
            else:
                dx, dy = item.GetWindow().GetBestSize()
                
        slice = self._image_slice
        
        return wx.Size( max( slice.left + slice.right,
                             slice.xleft + slice.xright + 
                             self._left_padding + self._right_padding + dx ),
                        max( slice.top + slice.bottom,
                             slice.xtop + slice.xbottom + 
                             self._top_padding + self._bottom_padding + dy ) )

    #---------------------------------------------------------------------------
    #  Layout the contents of the sizer based on the sizer's current size and
    #  position:
    #---------------------------------------------------------------------------

    def RecalcSizes ( self ):
        """ Layout the contents of the sizer based on the sizer's current size
            and position.
        """
        x,   y = self.GetPositionTuple()
        dx, dy = self.GetSizeTuple()
        slice  = self._image_slice
        left   = slice.xleft + self._left_padding
        top    = slice.xtop  + self._top_padding
        ix, iy, idx, idy = ( x + left, 
                             y + top,
                             dx - left - slice.xright  - self._right_padding,
                             dy - top  - slice.xbottom - self._bottom_padding )
                         
        for item in self.GetChildren():
            if item.IsSizer():
                item.GetSizer().SetDimension( ix, iy, idx, idy )
            else:
                item.GetWindow().SetDimensions( ix, iy, idx, idy )

