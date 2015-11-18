#------------------------------------------------------------------------------
#
#  Copyright (c) 2006, Enthought, Inc.
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
#  Date:   01/27/2006
#
#------------------------------------------------------------------------------

""" Defines a source code editor for the wxPython user interface toolkit,
    useful for tools such as debuggers.
"""

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

import wx
import wx.stc as stc

from traits.api \
    import Str, List, Int, Event, Bool, TraitError, on_trait_change

from traits.trait_base \
    import SequenceTypes

# FIXME: ToolkitEditorFactory is a proxy class defined here just for backward
# compatibility. The class has been moved to the
# traitsui.editors.code_editor file.
from traitsui.editors.code_editor \
    import ToolkitEditorFactory

from pyface.api \
    import PythonEditor

from pyface.util.python_stc \
    import faces

from editor \
    import Editor

from constants \
    import OKColor, ErrorColor

#-------------------------------------------------------------------------------
#  Constants:
#-------------------------------------------------------------------------------

# Marker line constants:

# Marks a marked line
MARK_MARKER = 0

# Marks a line matching the current search
SEARCH_MARKER = 1

# Marks the currently selected line
SELECTED_MARKER = 2

#-------------------------------------------------------------------------------
#  'SourceEditor' class:
#-------------------------------------------------------------------------------

class SourceEditor ( Editor ):
    """ Editor for source code, which displays a PyFace PythonEditor.
    """

    #---------------------------------------------------------------------------
    #  Trait definitions:
    #---------------------------------------------------------------------------

    # The code editor is scrollable. This value overrides the default.
    scrollable = True

    # Is the editor read only?
    readonly = Bool( False )

    # The currently selected line
    selected_line = Int

    # The currently selected text
    selected_text = Str

    # The list of line numbers to mark
    mark_lines = List( Int )

    # The current line number
    line = Event

    # The current column
    column = Event

    # calltip clicked event
    calltip_clicked = Event

    # The STC lexer use
    lexer = Int

    # The lines to be dimmed
    dim_lines = List(Int)
    dim_color = Str
    _dim_style_number = Int(16) # 0-15 are reserved for the python lexer

    # The lines to have squiggles drawn under them
    squiggle_lines = List(Int)
    squiggle_color = Str

    #---------------------------------------------------------------------------
    #  Finishes initializing the editor by creating the underlying toolkit
    #  widget:
    #---------------------------------------------------------------------------

    def init ( self, parent ):
        """ Finishes initializing the editor by creating the underlying toolkit
            widget.
        """
        factory      = self.factory
        self._editor = editor  = PythonEditor( parent,
                                 show_line_numbers = factory.show_line_numbers )
        self.control = control = editor.control

        # There are a number of events which aren't well documented that look
        # to be useful in future implmentations, below are a subset of the
        # events that look interesting:
        #    EVT_STC_AUTOCOMP_SELECTION
        #    EVT_STC_HOTSPOT_CLICK
        #    EVT_STC_HOTSPOT_DCLICK
        #    EVT_STC_DOUBLECLICK
        #    EVT_STC_MARGINCLICK

        control.SetSize( wx.Size( 300, 124 ) )

        # Clear out the goofy hotkeys for zooming text
        control.CmdKeyClear(ord('B'), stc.STC_SCMOD_CTRL)
        control.CmdKeyClear(ord('N'), stc.STC_SCMOD_CTRL)

        # Set up the events
        wx.EVT_KILL_FOCUS( control, self.wx_update_object )
        stc.EVT_STC_CALLTIP_CLICK( control, control.GetId(),
                                   self._calltip_clicked )

        if factory.auto_scroll and (factory.selected_line != ''):
            wx.EVT_SIZE( control, self._update_selected_line )

        if factory.auto_set:
            editor.on_trait_change( self.update_object, 'changed',
                                    dispatch = 'ui' )

        if factory.key_bindings is not None:
            editor.on_trait_change( self.key_pressed, 'key_pressed',
                                    dispatch = 'ui' )

        if self.readonly:
            control.SetReadOnly( True )

        # Set up the lexer
        control.SetLexer(stc.STC_LEX_CONTAINER)
        control.Bind(stc.EVT_STC_STYLENEEDED, self._style_needed)
        try:
            self.lexer = getattr(stc, 'STC_LEX_' + self.factory.lexer.upper())
        except AttributeError:
            self.lexer = stc.STC_LEX_NULL

        # Define the markers we use:
        control.MarkerDefine( MARK_MARKER, stc.STC_MARK_BACKGROUND,
                              background = factory.mark_color_ )
        control.MarkerDefine( SEARCH_MARKER, stc.STC_MARK_BACKGROUND,
                              background = factory.search_color_ )
        control.MarkerDefine( SELECTED_MARKER, stc.STC_MARK_BACKGROUND,
                              background = factory.selected_color_ )

        # Make sure the editor has been initialized:
        self.update_editor()

        # Set up any event listeners:
        self.sync_value( factory.mark_lines, 'mark_lines', 'from',
                         is_list = True )
        self.sync_value( factory.selected_line, 'selected_line', 'from' )
        self.sync_value( factory.selected_text, 'selected_text', 'to' )
        self.sync_value( factory.line, 'line' )
        self.sync_value( factory.column, 'column' )
        self.sync_value( factory.calltip_clicked, 'calltip_clicked')

        self.sync_value(factory.dim_lines, 'dim_lines', 'from', is_list=True)
        if self.factory.dim_color == '':
            self.dim_color = 'dark grey'
        else:
            self.sync_value(factory.dim_color, 'dim_color', 'from')

        self.sync_value(factory.squiggle_lines, 'squiggle_lines', 'from',
                        is_list=True)
        if factory.squiggle_color == '':
            self.squiggle_color = 'red'
        else:
            self.sync_value(factory.squiggle_color, 'squiggle_color', 'from')

        # Check if we need to monitor the line or column position being changed:
        if (factory.line != '') or (factory.column != '') or \
                (factory.selected_text != ''):
            stc.EVT_STC_UPDATEUI( control, control.GetId(),
                                  self._position_changed )
        self.set_tooltip()

    #---------------------------------------------------------------------------
    #  Handles the user entering input data in the edit control:
    #---------------------------------------------------------------------------

    def wx_update_object ( self, event ):
        """ Handles the user entering input data in the edit control.
        """
        self.update_object()
        event.Skip()

    def update_object ( self ):
        """ Handles the user entering input data in the edit control.
        """
        if not self._locked:
            try:
                value = self.control.GetText()
                if isinstance( self.value, SequenceTypes ):
                    value = value.split()
                self.value = value
                self.control.SetBackgroundColour( OKColor )
                self.control.Refresh()
            except TraitError as excp:
                pass

    #---------------------------------------------------------------------------
    #  Updates the editor when the object trait changes external to the editor:
    #---------------------------------------------------------------------------

    def update_editor ( self ):
        """ Updates the editor when the object trait changes externally to the
            editor.
        """
        self._locked = True
        new_value    = self.value
        if isinstance( new_value, SequenceTypes ):
            new_value = '\n'.join( [ line.rstrip() for line in new_value ] )
        control = self.control
        if control.GetText() != new_value:
            readonly = control.GetReadOnly()
            control.SetReadOnly( False )
            l1  = control.GetFirstVisibleLine()
            pos = control.GetCurrentPos()
            control.SetText( new_value )
            control.GotoPos( pos )
            control.ScrollToLine( l1 )
            control.SetReadOnly( readonly )
            self._mark_lines_changed()
            self._selected_line_changed()
            self._style_document()

        self._locked = False

    #---------------------------------------------------------------------------
    #  Handles the calltip being clicked:
    #---------------------------------------------------------------------------

    def _calltip_clicked ( self, event ):
        self.calltip_clicked = True

    #---------------------------------------------------------------------------
    #  Handles the set of 'marked lines' being changed:
    #---------------------------------------------------------------------------

    def _mark_lines_changed ( self ):
        """ Handles the set of marked lines being changed.
        """
        lines   = self.mark_lines
        control = self.control
        lc      = control.GetLineCount()
        control.MarkerDeleteAll( MARK_MARKER )

        for line in lines:
            if 0 < line <= lc:
                control.MarkerAdd( line - 1, MARK_MARKER )

        control.Refresh()

    def _mark_lines_items_changed ( self ):
        self._mark_lines_changed()

    #---------------------------------------------------------------------------
    #  Handles the currently 'selected line' being changed:
    #---------------------------------------------------------------------------

    def _selected_line_changed ( self ):
        """ Handles a change in which line is currently selected.
        """
        line    = self.selected_line
        control = self.control
        line    = max( 1, min( control.GetLineCount(), line ) ) - 1
        control.MarkerDeleteAll( SELECTED_MARKER )
        control.MarkerAdd( line, SELECTED_MARKER )
        control.GotoLine( line )
        if self.factory.auto_scroll:
            control.ScrollToLine( line - (control.LinesOnScreen() / 2) )

        control.Refresh()

    #---------------------------------------------------------------------------
    #  Handles the 'line' trait being changed:
    #---------------------------------------------------------------------------

    def _line_changed ( self, line ):
        if not self._locked:
            self.control.GotoLine( line - 1 )

    #---------------------------------------------------------------------------
    #  Handles the 'column' trait being changed:
    #---------------------------------------------------------------------------

    def _column_changed ( self, column ):
        if not self._locked:
            control = self.control
            line    = control.LineFromPosition( control.GetCurrentPos() )
            control.GotoPos( control.PositionFromLine( line ) + column - 1 )

    #---------------------------------------------------------------------------
    #  Handles the cursor position being changed:
    #---------------------------------------------------------------------------

    def _position_changed ( self, event ):
        """ Handles the cursor position being changed.
        """
        control      = self.control
        pos          = control.GetCurrentPos()
        line         = control.LineFromPosition( pos )
        self._locked = True
        self.line    = line + 1
        self.column  = pos - control.PositionFromLine( line ) + 1
        self._locked = False
        self.selected_text = control.GetSelectedText()

    #---------------------------------------------------------------------------
    #  Handles a key being pressed within the editor:
    #---------------------------------------------------------------------------

    def key_pressed ( self, event ):
        """ Handles a key being pressed within the editor.
        """
        self.factory.key_bindings.do( event.event, self.ui.handler,
                                      self.ui.info )

    #---------------------------------------------------------------------------
    #  Handles the styling of the editor:
    #---------------------------------------------------------------------------

    def _dim_color_changed(self):
        self.control.StyleSetForeground(self._dim_style_number, self.dim_color)
        self.control.StyleSetFaceName(self._dim_style_number, "courier new")
        self.control.StyleSetSize(self._dim_style_number, faces['size'])
        self.control.Refresh()

    def _squiggle_color_changed(self):
        self.control.IndicatorSetStyle(2, stc.STC_INDIC_SQUIGGLE)
        self.control.IndicatorSetForeground(2, self.squiggle_color)
        self.control.Refresh()

    @on_trait_change('dim_lines, squiggle_lines')
    def _style_document(self):
        """ Force the STC to fire a STC_STYLENEEDED event for the entire
            document.
        """
        self.control.ClearDocumentStyle()
        self.control.Colourise(0, -1)
        self.control.Refresh()

    def _style_needed(self, event):
        """ Handles an STC request for styling for some area.
        """
        position = self.control.GetEndStyled()
        start_line = self.control.LineFromPosition(position)
        end = event.GetPosition()
        end_line = self.control.LineFromPosition(end)

        # Fixes a strange a bug with the STC widget where creating a new line
        # after a dimmed line causes it to mysteriously lose its styling
        if start_line in self.dim_lines:
            start_line -= 1

        # Trying to Colourise only the lines that we want does not seem to work
        # so we do the whole area and then override the styling on certain lines
        if self.lexer != stc.STC_LEX_NULL:
            self.control.SetLexer(self.lexer)
            self.control.Colourise(position, end)
            self.control.SetLexer(stc.STC_LEX_CONTAINER)

        for line in xrange(start_line, end_line+1):
            # We don't use LineLength here because it includes newline
            # characters. Styling these leads to strange behavior.
            position = self.control.PositionFromLine(line)
            style_length = self.control.GetLineEndPosition(line) - position

            if line+1 in self.dim_lines:
                # Set styling mask to only style text bits, not indicator bits
                self.control.StartStyling(position, 0x1f)
                self.control.SetStyling(style_length, self._dim_style_number)
            elif self.lexer == stc.STC_LEX_NULL:
                self.control.StartStyling(position, 0x1f)
                self.control.SetStyling(style_length, stc.STC_STYLE_DEFAULT)

            if line+1 in self.squiggle_lines:
                self.control.StartStyling(position, stc.STC_INDIC2_MASK)
                self.control.SetStyling(style_length, stc.STC_INDIC2_MASK)
            else:
                self.control.StartStyling(position, stc.STC_INDIC2_MASK)
                self.control.SetStyling(style_length, stc.STC_STYLE_DEFAULT)

    #---------------------------------------------------------------------------
    #  Handles an error that occurs while setting the object's trait value:
    #---------------------------------------------------------------------------

    def error ( self, excp ):
        """ Handles an error that occurs while setting the object's trait value.
        """
        self.control.SetBackgroundColour( ErrorColor )
        self.control.Refresh()

    #---------------------------------------------------------------------------
    #  Disposes of the contents of an editor:
    #---------------------------------------------------------------------------

    def dispose ( self ):
        """ Disposes of the contents of an editor.
        """
        if self.factory.auto_set:
            self._editor.on_trait_change( self.update_object, 'changed',
                                          remove = True )
        if self.factory.key_bindings is not None:
            self._editor.on_trait_change( self.key_pressed, 'key_pressed',
                                          remove = True )

        wx.EVT_KILL_FOCUS( self.control, None )

        super( SourceEditor, self ).dispose()

    #-- UI preference save/restore interface -----------------------------------

    #---------------------------------------------------------------------------
    #  Restores any saved user preference information associated with the
    #  editor:
    #---------------------------------------------------------------------------

    def restore_prefs ( self, prefs ):
        """ Restores any saved user preference information associated with the
            editor.
        """
        if self.factory.key_bindings is not None:
            key_bindings = prefs.get( 'key_bindings' )
            if key_bindings is not None:
                self.factory.key_bindings.merge( key_bindings )

    #---------------------------------------------------------------------------
    #  Returns any user preference information associated with the editor:
    #---------------------------------------------------------------------------

    def save_prefs ( self ):
        """ Returns any user preference information associated with the editor.
        """
        return { 'key_bindings': self.factory.key_bindings }

# Define the simple, custom, text and readonly editors, which will be accessed
# by the editor factory for code editors.

CustomEditor = SimpleEditor = TextEditor = SourceEditor

class ReadonlyEditor(SourceEditor):

    # Set the value of the readonly trait.
    readonly = True

### EOF ########################################################################
