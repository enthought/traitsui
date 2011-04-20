#-------------------------------------------------------------------------------
#
#  Copyright (c) 2007, Enthought, Inc.
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
#  Date:   08/11/2007
#
#-------------------------------------------------------------------------------

""" Defines a themed panel that wraps itself around a single child widget.
"""

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

import wx

from traits.api \
    import Str, Property, Instance, Bool, cached_property

from themed_window \
    import ThemedWindow

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

    # Can the application change the theme contents?
    mutable_theme = Bool( False )

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

    def layout ( self ):
        """ Lays out the contents of the image panel.
        """
        self.control.Layout()
        self.control.Refresh()

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

    def _mutable_theme_changed ( self, state ):
        """ Handles a change to the 'mutable_theme' trait.
        """
        self.on_trait_change( self._theme_modified,
            'theme.[border.-,content.-,label.-,alignment,content_color,'
            'label_color]', remove = not state )

    def _theme_modified ( self ):
        if self.control is not None:
            self.layout()

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

    def _paint_fg ( self, dc ):
        """ Paints the foreground into the specified device context.
        """
        # If we have text and have room to draw it, then do so:
        text = self.text
        if (text != '') and self.can_show_text:
            theme = self.theme
            dc.SetBackgroundMode( wx.TRANSPARENT )
            dc.SetTextForeground( theme.label_color )
            dc.SetFont( self.control.GetFont() )

            alignment = theme.alignment
            label     = theme.label
            wdx, wdy  = self.control.GetClientSizeTuple()
            tdx, tdy, descent, leading = self.text_size
            tx      = None
            slice   = theme.image_slice
            xleft   = slice.xleft
            xright  = slice.xright
            xtop    = slice.xtop
            xbottom = slice.xbottom
            ltop    = label.top
            lbottom = label.bottom
            tdyp    = tdy + ltop + lbottom
            cl      = xleft + label.left
            cr      = wdx - xright - label.right
            if (tdyp <= xtop) and (xtop >= xbottom):
                ty = ((ltop + xtop - lbottom - tdy) / 2) + 1
            elif tdy <= xbottom:
                ty = wdy + ((ltop - xbottom - lbottom - tdy) / 2)
            else:
                ty = (wdy + xtop + label.top - xbottom - label.bottom - tdy) / 2
                if xleft >= xright:
                    cl = label.left
                    cr = xleft - label.right
                else:
                    cl = wdx - xright + label.left
                    cr = wdx - label.right

            # Calculate the x coordinate for the specified alignment type:
            if alignment == 'left':
                tx = cl
            elif alignment == 'right':
                tx = cr - tdx
            else:
                tx = (cl + cr - tdx) / 2

            # Draw the (clipped) text string:
            dc.SetClippingRegion( cl, ty, cr - cl, tdy )
            dc.DrawText( text, tx, ty )
            dc.DestroyClippingRegion()

    #-- Private Methods --------------------------------------------------------

    def _adjusted_size_of ( self, dx, dy ):
        """ Returns the adjusted size of its children, taking into account the
            image slice border.
        """
        slice   = self.theme.image_slice
        content = self.theme.content
        sizer   = self.control.GetSizer()
        return wx.Size( dx + min( slice.left, slice.xleft )   +
                             min( slice.right, slice.xright ) +
                             content.left + content.right,
                        dy + min( slice.top, slice.xtop )       +
                             min( slice.bottom, slice.xbottom ) +
                             content.top + content.bottom )

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

        # Save a reference to the theme:
        self._theme = theme

        # Save the ImageSlice object which determines the inset border size:
        self._image_slice = theme.image_slice

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

        slice   = self._image_slice
        content = self._theme.content

        return wx.Size( max( slice.left + slice.right,
                             slice.xleft + slice.xright +
                             content.left + content.right + dx ),
                        max( slice.top + slice.bottom,
                             slice.xtop + slice.xbottom +
                             content.top + content.bottom + dy ) )

    #---------------------------------------------------------------------------
    #  Layout the contents of the sizer based on the sizer's current size and
    #  position:
    #---------------------------------------------------------------------------

    def RecalcSizes ( self ):
        """ Layout the contents of the sizer based on the sizer's current size
            and position.
        """
        x,   y  = self.GetPositionTuple()
        dx, dy  = self.GetSizeTuple()
        slice   = self._image_slice
        content = self._theme.content
        left    = slice.xleft + content.left
        top     = slice.xtop  + content.top
        ix, iy, idx, idy = ( x + left,
                             y + top,
                             dx - left - slice.xright  - content.right,
                             dy - top  - slice.xbottom - content.bottom )

        for item in self.GetChildren():
            if item.IsSizer():
                item.GetSizer().SetDimension( ix, iy, idx, idy )
            else:
                item.GetWindow().SetDimensions( ix, iy, idx, idy )

