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
#  Date:   10/21/2004
#
#------------------------------------------------------------------------------

""" Defines the various editors for multi-selection enumerations, for the
wxPython user interface toolkit.
"""

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

import logging

import wx

from traits.api \
    import List, Str, TraitError

# FIXME: ToolkitEditorFactory is a proxy class defined here just for backward
# compatibility. The class has been moved to the
# traitsui.editors.check_list_editor file.
from traitsui.editors.check_list_editor \
    import ToolkitEditorFactory

from editor_factory \
    import TextEditor as BaseTextEditor

from editor \
    import EditorWithList

from helper \
    import TraitsUIPanel

logger = logging.getLogger(__name__)


# default formatting function (would import from string, but not in Python 3)
capitalize = lambda s: s.capitalize()


#-------------------------------------------------------------------------------
#  'SimpleEditor' class:
#-------------------------------------------------------------------------------

class SimpleEditor ( EditorWithList ):
    """ Simple style of editor for checklists, which displays a combo box.
    """

    #---------------------------------------------------------------------------
    #  Trait definitions:
    #---------------------------------------------------------------------------

    # Checklist item names
    names = List( Str )

    # Checklist item values
    values = List

    #---------------------------------------------------------------------------
    #  Finishes initializing the editor by creating the underlying toolkit
    #  widget:
    #---------------------------------------------------------------------------

    def init ( self, parent ):
        """ Finishes initializing the editor by creating the underlying toolkit
            widget.
        """
        self.create_control( parent )
        super( SimpleEditor, self ).init( parent )
        self.set_tooltip()

    #---------------------------------------------------------------------------
    #  Creates the initial editor control:
    #---------------------------------------------------------------------------

    def create_control ( self, parent ):
        """ Creates the initial editor control.
        """
        self.control = wx.Choice( parent, -1,
                                  wx.Point( 0, 0 ), wx.Size( 100, 20 ), [] )
        wx.EVT_CHOICE( parent, self.control.GetId(), self.update_object )

    #---------------------------------------------------------------------------
    #  Handles the list of legal check list values being updated:
    #---------------------------------------------------------------------------

    def list_updated ( self, values ):
        """ Handles updates to the list of legal checklist values.
        """
        sv = self.string_value
        if (len( values ) > 0) and isinstance( values[0], basestring ):
           values = [ ( x, sv( x, capitalize ) ) for x in values ]
        self.values = valid_values = [ x[0] for x in values ]
        self.names  =                [ x[1] for x in values ]

        # Make sure the current value is still legal:
        modified  = False
        cur_value = parse_value( self.value )
        for i in range( len( cur_value ) - 1, -1, -1 ):
            if cur_value[i] not in valid_values:
                try:
                    del cur_value[i]
                    modified = True
                except TypeError as e:
                    logger.warn('Unable to remove non-current value [%s] from '
                        'values %s', cur_value[i], values)
        if modified:
            if isinstance( self.value, basestring ):
                cur_value = ','.join( cur_value )
            self.value = cur_value

        self.rebuild_editor()

    #---------------------------------------------------------------------------
    #  Rebuilds the editor after its definition is modified:
    #---------------------------------------------------------------------------

    def rebuild_editor ( self ):
        """ Rebuilds the editor after its definition is modified.
        """
        control = self.control
        control.Clear()
        for name in self.names:
            control.Append( name )

        self.update_editor()

    #----------------------------------------------------------------------------
    #  Handles the user selecting a new value from the combo box:
    #----------------------------------------------------------------------------

    def update_object ( self, event ):
        """ Handles the user selecting a new value from the combo box.
        """
        value = self.values[ self.names.index( event.GetString() ) ]
        if type( self.value ) is not str:
           value = [ value ]

        self.value = value

    #---------------------------------------------------------------------------
    #  Updates the editor when the object trait changes external to the editor:
    #---------------------------------------------------------------------------

    def update_editor ( self ):
        """ Updates the editor when the object trait changes externally to the
            editor.
        """
        try:
            self.control.SetSelection(
                             self.values.index( parse_value( self.value )[0] ) )
        except:
            pass

#-------------------------------------------------------------------------------
#  'CustomEditor' class:
#-------------------------------------------------------------------------------

class CustomEditor ( SimpleEditor ):
    """ Custom style of editor for checklists, which displays a set of check
        boxes.
    """

    #---------------------------------------------------------------------------
    #  Creates the initial editor control:
    #---------------------------------------------------------------------------

    def create_control ( self, parent ):
        """ Creates the initial editor control.
        """
        # Create a panel to hold all of the check boxes
        self.control = panel = TraitsUIPanel( parent, -1 )

    #---------------------------------------------------------------------------
    #  Rebuilds the editor after its definition is modified:
    #---------------------------------------------------------------------------

    def rebuild_editor ( self ):
        """ Rebuilds the editor after its definition is modified.
        """
        panel = self.control
        panel.SetSizer( None )
        panel.DestroyChildren()

        cur_value = parse_value( self.value )

        # Create a sizer to manage the radio buttons:
        labels = self.names
        values = self.values
        n      = len( labels )
        cols   = self.factory.cols
        rows   = (n + cols - 1) / cols
        incr   = [ n / cols ] * cols
        rem    = n % cols

        for i in range( cols ):
            incr[i] += (rem > i)
        incr[-1] = -(reduce( lambda x, y: x + y, incr[:-1], 0 ) - 1)

        if cols > 1:
           sizer = wx.GridSizer( 0, cols, 2, 4 )
        else:
           sizer = wx.BoxSizer( wx.VERTICAL )

        # Add the set of all possible choices:
        index = 0
        for i in range( rows ):
            for j in range( cols ):
                if n > 0:
                    label   = labels[ index ]
                    control = wx.CheckBox( panel, -1, label )
                    control.value = value = values[ index ]
                    control.SetValue( value in cur_value )
                    wx.EVT_CHECKBOX( panel, control.GetId(), self.update_object)
                    index += incr[j]
                    n     -= 1
                else:
                    control = wx.CheckBox( panel, -1, '' )
                    control.Show( False )

                sizer.Add( control, 0, wx.NORTH, 5 )

        # Lay out the controls:
        panel.SetSizerAndFit( sizer )

        # FIXME: There are cases where one of the parent panel's of the check
        # list editor has a fixed 'min size' which prevents the check list
        # editor from expanding correctly, so we currently are making sure
        # that all of the parent panels do not have a fixed min size before
        # doing the layout/refresh:
        parent = panel.GetParent()
        while isinstance( parent, wx.Panel ):
            parent.SetMinSize( wx.Size( -1, -1 ) )
            panel  = parent
            parent = parent.GetParent()

        panel.Layout()
        panel.Refresh()

    #---------------------------------------------------------------------------
    #  Handles the user clicking one of the 'custom' check boxes:
    #---------------------------------------------------------------------------

    def update_object ( self, event ):
        """ Handles the user clicking one of the custom check boxes.
        """
        control   = event.GetEventObject()
        cur_value = parse_value( self.value )
        if control.GetValue():
            cur_value.append( control.value )
        else:
            cur_value.remove( control.value )
        if isinstance(self.value, basestring):
            cur_value = ','.join( cur_value )
        self.value = cur_value

    #---------------------------------------------------------------------------
    #  Updates the editor when the object trait changes external to the editor:
    #---------------------------------------------------------------------------

    def update_editor ( self ):
        """ Updates the editor when the object trait changes externally to the
            editor.
        """
        new_values = parse_value( self.value )
        for control in self.control.GetChildren():
            if control.IsShown():
               control.SetValue( control.value in new_values )

#-------------------------------------------------------------------------------
#  'TextEditor' class:
#-------------------------------------------------------------------------------

class TextEditor ( BaseTextEditor ):
    """ Text style of editor for checklists, which displays a text field.
    """

    #---------------------------------------------------------------------------
    #  Handles the user changing the contents of the edit control:
    #---------------------------------------------------------------------------

    def update_object ( self, event ):
        """ Handles the user changing the contents of the edit control.
        """
        try:
            value = self.control.GetValue()
            value = eval( value )
        except:
            pass
        try:
            self.value = value
        except TraitError as excp:
            pass

#-------------------------------------------------------------------------------
#  Parse a value into a list:
#-------------------------------------------------------------------------------

def parse_value ( value ):
    """ Parses a value into a list.
    """
    if value is None:
       return []

    if type( value ) is not str:
       return value[:]

    return [ x.strip() for x in value.split( ',' ) ]

### EOF ########################################################################
