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
#  Date:   07/04/2007
#
#-------------------------------------------------------------------------------

""" Traits UI themed checkbox editor.
"""

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

import wx

from traits.api \
    import Instance, Str

from traitsui.ui_traits \
    import ATheme, Image, Position, Spacing

from traitsui.wx.editor \
    import Editor

from traitsui.basic_editor_factory \
    import BasicEditorFactory

from themed_control \
    import ThemedControl

#-------------------------------------------------------------------------------
#  '_ThemedCheckboxEditor' class:
#-------------------------------------------------------------------------------

class _ThemedCheckboxEditor ( Editor ):
    """ Traits UI themed checkbox editor.
    """

    # The ThemedControl used for the checkbox:
    checkbox = Instance( ThemedControl )

    #---------------------------------------------------------------------------
    #  Finishes initializing the editor by creating the underlying toolkit
    #  widget:
    #---------------------------------------------------------------------------

    def init ( self, parent ):
        """ Finishes initializing the editor by creating the underlying toolkit
            widget.
        """
        # Create the checkbox and its control:
        item      = self.item
        factory   = self.factory
        label     = self.string_value( factory.label or item.label )
        min_size  = ( 0, 0 )
        if factory.theme is not None:
            min_size  = ( 80, 0 )

        self.checkbox = checkbox = ThemedControl( **factory.get(
            'image', 'position', 'spacing', 'theme' ) ).set(
            text       = label,
            controller = self,
            min_size   = min_size )
        self.control = checkbox.create_control( parent )

        # Set the tooltip:
        self.set_tooltip()

    #---------------------------------------------------------------------------
    #  Updates the editor when the object trait changes external to the editor:
    #---------------------------------------------------------------------------

    def update_editor ( self ):
        """ Updates the editor when the object trait changes externally to the
            editor.
        """
        if self.checkbox.state == 'hover':
            self._set_hover_theme()
        else:
            self._set_theme()

    #-- ThemedControl Event Handlers -------------------------------------------

    def normal_motion ( self, x, y, event ):
        self._set_hover_theme( 'hover' )
        self.control.CaptureMouse()

    def hover_left_down ( self, x, y, event ):
        self.control.ReleaseMouse()
        self._set_hover_theme( 'down', not self.value )

    def hover_motion ( self, x, y, event ):
        if not self.checkbox.in_control( x, y ):
            self.control.ReleaseMouse()
            self._set_theme( 'normal' )

    def down_left_up ( self, x, y, event ):
        if self.checkbox.in_control( x, y ):
            self.value = not self.value
            self.normal_motion( x, y, event )
        else:
            self._set_theme( 'normal' )

    def down_motion ( self, x, y, event ):
        if not self.checkbox.in_control( x, y ):
            self._set_theme()
        else:
            self._set_hover_theme( value = not self.value )

    #-- Private Methods --------------------------------------------------------

    def _set_theme ( self, state = None, value = None ):
        """ Sets the theme, image, offset and optional checkbox state to use for
            a specified checkbox state value.
        """
        if value is None:
            value = self.value

        factory      = self.factory
        theme, image = factory.theme, factory.image
        if value:
            theme, image = factory.on_theme, factory.on_image

        n = (1 * value) * (theme is not None)
        self.checkbox.set( offset = ( n, n ),
                           theme  = theme or factory.theme,
                           image  = image or factory.image,
                           state  = state or self.checkbox.state )

    def _set_hover_theme ( self, state = None, value = None ):
        """ Sets the theme, image, offset and optional checkbox state to use for
            a specified checkbox state value while in hover mode.
        """
        if value is None:
            value = self.value

        factory      = self.factory
        theme, image = factory.hover_off_theme, factory.hover_off_image
        if value:
            theme = factory.hover_on_theme or factory.on_theme
            image = factory.hover_on_image or factory.on_image

        n = (1 * value) * (theme is not None)
        self.checkbox.set( offset = ( n, n ),
                           theme  = theme or factory.theme,
                           image  = image or factory.image,
                           state  = state or self.checkbox.state )

#-------------------------------------------------------------------------------
#  Create the editor factory object:
#-------------------------------------------------------------------------------

# wxPython editor factory for themed checkbox editors:
class ThemedCheckboxEditor ( BasicEditorFactory ):

    # The editor class to be created:
    klass = _ThemedCheckboxEditor

    # The checkbox label:
    label = Str

    # The basic theme for the checkbox (i.e. the 'off' state):
    theme = ATheme

    # The optional 'on' state theme for the checkbox:
    on_theme = ATheme

    # The optional 'hover off' state theme for the checkbox:
    hover_off_theme = ATheme

    # The optional 'hover on' state theme for the checbox:
    hover_on_theme = ATheme

    # The optional image to display in the checkbox (i.e. the 'off' state):
    image = Image( 'cb_off' )

    # The optional 'on' state image to display in the checkbox:
    on_image = Image( 'cb_on' )

    # The optional 'hover off' state image to display in the checkbox:
    hover_off_image = Image( 'cb_hover_off' )

    # The optional 'hover on' state image to display in the checkbox:
    hover_on_image = Image( 'cb_hover_on' )

    # The position of the image relative to the text:
    position = Position

    # The amount of space between the image and the text:
    spacing = Spacing

#-------------------------------------------------------------------------------
#  Helper function for creating themed checkboxes:
#-------------------------------------------------------------------------------

def themed_checkbox_editor ( style = None, show_checkbox = True, **traits ):
    """ Simplifies creation of a ThemedCheckboxEditor by setting up the
        themes and images automatically based on the value of the *style* and
        *show_checkbox* arguments.
    """
    tce = ThemedCheckboxEditor( **traits )

    if not show_checkbox:
        tce.set( image           = None,
                 on_image        = None,
                 hover_off_image = None,
                 hover_on_image  = None )

    if isinstance( style, basestring ):
        group = style[0:1].upper()
        if (len( group ) == 0) or (group not in 'BCGJTY'):
            group = 'B'

        row      = style[1:2].upper()
        all_rows = '0123456789ABCDEFGHIJKL'
        if (len( row ) == 0) or (row not in all_rows):
            row = 'H'

        column      = style[2:3].upper()
        all_columns = '12345789AB'
        if (len( column ) == 0) or (column not in all_columns):
            column = '5'

        tce.theme = '@%s%s%s' % ( group, row, column )

        if style[-1:] == '.':
            return tce

        alt_row    = '44456349A78FFFGHEFKLIJ'[ all_rows.index( row ) ]
        alt_column = '66666CCCCC'[ all_columns.index( column ) ]

        tce.set( on_theme        = '@%s%s%s' % ( group, alt_row, column ),
                 hover_on_theme  = '@%s%s%s' % ( group, alt_row, alt_column ),
                 hover_off_theme = '@%s%s%s' % ( group, row, alt_column ) )

    return tce
