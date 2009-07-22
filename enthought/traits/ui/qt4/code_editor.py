#------------------------------------------------------------------------------
# Copyright (c) 2007, Riverbank Computing Limited
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD license.
# However, when used with the GPL version of PyQt the additional terms described in the PyQt GPL exception also apply

#
# Author: Riverbank Computing Limited
#------------------------------------------------------------------------------

""" Defines a source code editor and code editor factory, for the PyQt user
interface toolkit, useful for tools such as debuggers.
"""

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from PyQt4 import QtCore, QtGui, Qsci
from PyQt4.Qsci import QsciScintillaBase as QsciBase

# Only QScintilla version 2.3+ has support for custom lexing
if Qsci.QSCINTILLA_VERSION < 0x20300:
    raise RuntimeError, "QScintilla version 2.3 or higher needed for CodeEditor"

from enthought.traits.api \
    import Str, Unicode, List, Int, Event, Bool, TraitError, on_trait_change

from enthought.traits.trait_base \
    import SequenceTypes

# FIXME: ToolkitEditorFactory is a proxy class defined here just for backward
# compatibility. The class has been moved to the 
# enthought.traits.ui.editors.code_editor file.
from enthought.traits.ui.editors.code_editor \
    import ToolkitEditorFactory

from enthought.pyface.api \
    import PythonEditor
    
from editor \
    import Editor
    
from constants \
    import OKColor, ErrorColor

#-------------------------------------------------------------------------------
#  Constants:  
#-------------------------------------------------------------------------------
        
# Marker line constants:
MARK_MARKER = 0 # Marks a marked line
SEARCH_MARKER = 1 # Marks a line matching the current search
SELECTED_MARKER = 2 # Marks the currently selected line

# A map from Qt lexer constants to the corresponding concrete lexer:
LEXER_MAP = { QsciBase.SCLEX_BASH: Qsci.QsciLexerBash, 
              QsciBase.SCLEX_BATCH: Qsci.QsciLexerBatch, 
              QsciBase.SCLEX_CMAKE: Qsci.QsciLexerCMake, 
              QsciBase.SCLEX_CPP: Qsci.QsciLexerCPP, 
              QsciBase.SCLEX_CSS: Qsci.QsciLexerCSS, 
              QsciBase.SCLEX_D: Qsci.QsciLexerD, 
              QsciBase.SCLEX_DIFF: Qsci.QsciLexerDiff, 
              QsciBase.SCLEX_FORTRAN: Qsci.QsciLexerFortran, 
              QsciBase.SCLEX_HTML: Qsci.QsciLexerHTML, 
              QsciBase.SCLEX_LUA: Qsci.QsciLexerLua, 
              QsciBase.SCLEX_MAKEFILE: Qsci.QsciLexerMakefile, 
              QsciBase.SCLEX_PASCAL: Qsci.QsciLexerPascal, 
              QsciBase.SCLEX_PERL: Qsci.QsciLexerPerl, 
              QsciBase.SCLEX_POV: Qsci.QsciLexerPOV, 
              QsciBase.SCLEX_PROPERTIES: Qsci.QsciLexerProperties, 
              QsciBase.SCLEX_PYTHON: Qsci.QsciLexerPython, 
              QsciBase.SCLEX_RUBY: Qsci.QsciLexerRuby, 
              QsciBase.SCLEX_SQL: Qsci.QsciLexerSQL, 
              QsciBase.SCLEX_TCL: Qsci.QsciLexerTCL, 
              QsciBase.SCLEX_TEX: Qsci.QsciLexerTeX, 
              QsciBase.SCLEX_VHDL: Qsci.QsciLexerVHDL, 
              QsciBase.SCLEX_XML: Qsci.QsciLexerXML, 
              QsciBase.SCLEX_YAML: Qsci.QsciLexerYAML }

#-------------------------------------------------------------------------------
#  'SourceLexer' class:
#-------------------------------------------------------------------------------

class SourceLexer ( Qsci.QsciLexerCustom ):
    """ A custom lexer that first lexes according to an existing lexer (by 
        default the Python lexer), then dim and underlines lines as appropriate.
    """
    
    def __init__(self, editor):
        """ Store the editor.
        """
        Qsci.QsciLexerCustom.__init__(self, editor.control)
        self._editor = editor
    
    def description(self, style):
        """ Overriden because Qt balks if it is not. This is indended to be used
            to store style preferences, but we don't care about that.
        """
        return QtCore.QString()

    def styleText(self, start, end):
        """ Overriden to perform custom styling.
        """
        control = self._editor.control
        start_line = control.lineIndexFromPosition(start)[0]
        end_line = control.lineIndexFromPosition(end)[0]

        # Fixes a strange a bug with the STC widget where creating a new line
        # after a dimmed line causes it to mysteriously lose its styling
        if start_line in self._editor.dim_lines:
            start_line -= 1

        # Trying to Colourise only the lines that we want does not seem to work
        # so we do the whole area and then override the styling on certain lines
        if self._editor.lexer != QsciBase.SCLEX_NULL:
            control.SendScintilla(QsciBase.SCI_SETLEXER, self._editor.lexer)
            control.SendScintilla(QsciBase.SCI_COLOURISE, start, end)
            control.SendScintilla(QsciBase.SCI_SETLEXER, QsciBase.SCLEX_CONTAINER)

        for line in xrange(start_line, end_line+1):
            # We don't use lineLength here because it includes newline 
            # characters. Styling these leads to strange behavior.
            position = control.positionFromLineIndex(line, 0)
            style_length = control.SendScintilla(QsciBase.SCI_GETLINEENDPOSITION,
                                                 line) - position

            if line+1 in self._editor.dim_lines:
                # Set styling mask to only style text bits, not indicator bits
                self.startStyling(position, 0x1f)
                self.setStyling(style_length, self._editor.dim_style_number)
            elif self._editor.lexer == QsciBase.SCLEX_NULL:
                self.startStyling(position, 0x1f)
                self.setStyling(style_length, QsciBase.STYLE_DEFAULT)
                
            if line+1 in self._editor.squiggle_lines:
                self.startStyling(position, QsciBase.INDIC2_MASK)
                self.setStyling(style_length, QsciBase.INDIC2_MASK)
            else:
                self.startStyling(position, QsciBase.INDIC2_MASK)
                self.setStyling(style_length, QsciBase.STYLE_DEFAULT)

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
    selected_text = Unicode
    
    # The list of line numbers to mark
    mark_lines = List( Int )
    
    # The current line number
    line = Event
    
    # The current column
    column = Event

    # The Scintilla lexer use
    lexer = Int

    # The lines to be dimmed
    dim_lines = List(Int)
    dim_color = Str
    dim_style_number = Int(16) # 0-15 are reserved for the python lexer
    
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
        factory = self.factory
        self._editor = editor = PythonEditor(None,
                show_line_numbers = factory.show_line_numbers)
        self.control = control = editor.control

        control.connect(control, QtCore.SIGNAL('lostFocus'), self.update_object)

        if factory.auto_set:
            editor.on_trait_change( self.update_object, 'changed', 
                                    dispatch = 'ui' )
        if factory.key_bindings is not None:
            editor.on_trait_change( self.key_pressed, 'key_pressed', 
                                    dispatch = 'ui' )
        if self.readonly:
            control.setReadOnly(True)

        # Set up the lexer. Before we set our custom lexer, we call setLexer
        # with the QSciLexer that will set the keywords and styles for our
        # basic syntax lexing. We save and then restore these keywords/styles 
        # because they get nuked when call setLexer again.
        self.lexer = getattr(QsciBase, 'SCLEX_' + self.factory.lexer.upper(),
                             QsciBase.SCLEX_NULL)
        lexer_class = LEXER_MAP.get(self.lexer)
        if lexer_class:
            control.setLexer(lexer_class(control))
            keywords = control.lexer().keywords(1)
            styles = []
            # FIXME: Ideally we want to use 'FONT' too, but this is causing
            #        segfaults. Why?
            attr_names = [ 'FORE', 'BACK', 'BOLD', 'ITALIC', 'SIZE', 
                           'EOLFILLED', 'UNDERLINE' ]
            for style in xrange(128):
                attrs = [ control.SendScintilla(getattr(QsciBase,'SCI_STYLEGET'+a), 
                                                style)
                          for a in attr_names ]
                styles.append(attrs)
        control.setLexer(SourceLexer(self))
        if lexer_class:
            if keywords:
                control.SendScintilla(QsciBase.SCI_SETKEYWORDS, 0, keywords)
            for style, attrs in enumerate(styles):
                for attr_num, attr in enumerate(attrs):
                    msg = getattr(QsciBase, 'SCI_STYLESET' + attr_names[attr_num])
                    control.SendScintilla(msg, style, attr)
                                      
        # Define the markers we use:
        control.markerDefine(Qsci.QsciScintilla.Background, MARK_MARKER)
        control.setMarkerBackgroundColor(factory.mark_color_, MARK_MARKER)

        control.markerDefine(Qsci.QsciScintilla.Background, SEARCH_MARKER)
        control.setMarkerBackgroundColor(factory.search_color_, SEARCH_MARKER)

        control.markerDefine(Qsci.QsciScintilla.Background, SELECTED_MARKER)
        control.setMarkerBackgroundColor(factory.selected_color_, SELECTED_MARKER)

        # Make sure the editor has been initialized:
        self.update_editor()
        
        # Set up any event listeners:
        self.sync_value( factory.mark_lines, 'mark_lines', 'from',
                         is_list = True )
        self.sync_value( factory.selected_line, 'selected_line', 'from' )
        self.sync_value( factory.selected_text, 'selected_text', 'to' )
        self.sync_value( factory.line, 'line' )
        self.sync_value( factory.column, 'column' )

        self.sync_value(factory.dim_lines, 'dim_lines', 'from', is_list=True)
        if self.factory.dim_color == '':
            self.dim_color = 'grey'
        else:
            self.sync_value(factory.dim_color, 'dim_color', 'from')

        self.sync_value(factory.squiggle_lines, 'squiggle_lines', 'from',
                        is_list=True)
        if factory.squiggle_color == '':
            self.squiggle_color = 'red'
        else:
            self.sync_value(factory.squiggle_color, 'squiggle_color', 'from')

        # Check if we need to monitor the line or column position being changed:
        if (factory.line != '') or (factory.column != ''):
            control.connect(control,
                    QtCore.SIGNAL('cursorPositionChanged(int, int)'),
                    self._position_changed)
        self.set_tooltip()
    
    #---------------------------------------------------------------------------
    #  Handles the user entering input data in the edit control:
    #---------------------------------------------------------------------------

    def update_object ( self ):
        """ Handles the user entering input data in the edit control.
        """
        if not self._locked:
            try:
                value = unicode(self.control.text())
                if isinstance( self.value, SequenceTypes ):
                    value = value.split()
                self.value = value
                self.control.lexer().setPaper(OKColor)
            except TraitError, excp:
                pass
        
    #---------------------------------------------------------------------------
    #  Updates the editor when the object trait changes external to the editor:
    #---------------------------------------------------------------------------
        
    def update_editor ( self ):
        """ Updates the editor when the object trait changes externally to the 
            editor.
        """
        self._locked = True
        new_value = self.value
        if isinstance( new_value, SequenceTypes ):
            new_value = '\n'.join( [ line.rstrip() for line in new_value ] )
        control = self.control
        if control.text() != new_value:
            readonly = control.isReadOnly()
            control.setReadOnly(False)
            vsb = control.verticalScrollBar()
            l1 = vsb.value()
            line, column = control.getCursorPosition()
            control.setText(new_value)
            control.setCursorPosition(line, column)
            vsb.setValue(l1)
            control.setReadOnly(readonly)
            self._mark_lines_changed()
            self._selected_line_changed()
        self._locked = False
        
    #---------------------------------------------------------------------------
    #  Handles the set of 'marked lines' being changed:  
    #---------------------------------------------------------------------------
                
    def _mark_lines_changed ( self ):
        """ Handles the set of marked lines being changed.
        """
        lines   = self.mark_lines
        control = self.control
        lc      = control.lines()
        control.markerDeleteAll(MARK_MARKER)
        for line in lines:
            if 0 < line <= lc:
                control.markerAdd(line - 1, MARK_MARKER)

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
        line    = max(1, min(control.lines(), line)) - 1
        control.markerDeleteAll(SELECTED_MARKER)
        control.markerAdd(line, SELECTED_MARKER)
        _, column = control.getCursorPosition()
        control.setCursorPosition(line, column)
        if self.factory.auto_scroll:
            control.ensureLineVisible(line)

    #---------------------------------------------------------------------------
    #  Handles the 'line' trait being changed:  
    #---------------------------------------------------------------------------
                                              
    def _line_changed ( self, line ):
        if not self._locked:
            _, column = control.getCursorPosition()
            self.control.setCursorPosition(line - 1, column)
                                  
    #---------------------------------------------------------------------------
    #  Handles the 'column' trait being changed:  
    #---------------------------------------------------------------------------
                                              
    def _column_changed ( self, column ):
        if not self._locked:
            line, _ = control.getCursorPosition()
            self.control.setCursorPosition(line, column - 1)

    #---------------------------------------------------------------------------
    #  Handles the cursor position being changed:  
    #---------------------------------------------------------------------------
                        
    def _position_changed(self, line, column):
        """ Handles the cursor position being changed.
        """
        self._locked = True
        self.line = line
        self.column = column
        self._locked = False
        self.selected_text = unicode(control.selectedText())
        
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
        self.control.SendScintilla(QsciBase.SCI_STYLESETFORE, 
                                   self.dim_style_number,
                                   QtGui.QColor(self.dim_color))

    def _squiggle_color_changed(self):
        self.control.SendScintilla(QsciBase.SCI_INDICSETSTYLE, 2,
                                   QsciBase.INDIC_SQUIGGLE)
        self.control.SendScintilla(QsciBase.SCI_INDICSETFORE, 2,
                                   QtGui.QColor(self.squiggle_color))

    @on_trait_change('dim_lines, squiggle_lines')
    def _style_document(self):
        self.control.recolor()
        
    #---------------------------------------------------------------------------
    #  Handles an error that occurs while setting the object's trait value:
    #---------------------------------------------------------------------------
        
    def error ( self, excp ):
        """ Handles an error that occurs while setting the object's trait value.
        """
        self.control.lexer().setPaper(ErrorColor)

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
