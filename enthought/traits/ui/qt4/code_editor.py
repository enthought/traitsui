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

from enthought.traits.api import Str, Unicode, List, Int, Event, Bool, \
    TraitError, on_trait_change
from enthought.traits.trait_base import SequenceTypes

# FIXME: ToolkitEditorFactory is a proxy class defined here just for backward
# compatibility. The class has been moved to the 
# enthought.traits.ui.editors.code_editor file.
from enthought.traits.ui.editors.code_editor import ToolkitEditorFactory

from enthought.pyface.key_pressed_event import KeyPressedEvent
from enthought.pyface.ui.qt4.python_editor import _Scintilla

from constants import OKColor, ErrorColor    
from editor import Editor
from helper import pixmap_cache

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
#  'FindWidget' class:
#-------------------------------------------------------------------------------

class FindWidget ( QtGui.QWidget ):
    """ A find widget a la the find bar in Firefox.
    """

    def __init__(self, callback, parent=None):
        """ Creates a FindWidget. 'callback' should be function of signature: 
            (string text, bool forward, bool match_case).
        """
        QtGui.QWidget.__init__(self, parent)
        self._callback = callback
        
        layout = QtGui.QHBoxLayout(self)
        layout.setSpacing(5)
        layout.setMargin(0)

        self.close_button = QtGui.QToolButton(self)
        self.close_button.setAutoRaise(True)
        self.close_button.setIcon(QtGui.QIcon(pixmap_cache('closetab.png')))
        QtCore.QObject.connect(self.close_button, QtCore.SIGNAL('clicked()'),
                               self, QtCore.SLOT('hide()'))
        layout.addWidget(self.close_button)

        self.find_edit = QtGui.QLineEdit(self)
        self.find_edit.setMinimumSize(QtCore.QSize(100, 0))
        signal = QtCore.SIGNAL('textChanged(QString)')
        QtCore.QObject.connect(self.find_edit, signal, self.update_buttons)
        signal = QtCore.SIGNAL('returnPressed()')
        QtCore.QObject.connect(self.find_edit, signal, self._next_clicked)
        layout.addWidget(self.find_edit)

        self.previous_button = QtGui.QToolButton(self)
        self.previous_button.setAutoRaise(True)
        self.previous_button.setIcon(QtGui.QIcon(pixmap_cache('previous.png')))
        self.previous_button.setText('Previous')
        self.previous_button.setToolButtonStyle(QtCore.Qt.ToolButtonTextBesideIcon)
        signal = QtCore.SIGNAL('clicked()')
        QtCore.QObject.connect(self.previous_button, signal, self._previous_clicked)
        layout.addWidget(self.previous_button)

        self.next_button = QtGui.QToolButton(self)
        self.next_button.setAutoRaise(True)
        self.next_button.setIcon(QtGui.QIcon(pixmap_cache('next.png')))
        self.next_button.setText('Next')
        self.next_button.setToolButtonStyle(QtCore.Qt.ToolButtonTextBesideIcon)
        signal = QtCore.SIGNAL('clicked()')
        QtCore.QObject.connect(self.next_button, signal, self._next_clicked)
        layout.addWidget(self.next_button)

        self.case_box = QtGui.QCheckBox('Match case', self)
        layout.addWidget(self.case_box)

        # Align items to left and prevent text field from growing too large
        layout.addItem(QtGui.QSpacerItem(20, 20, QtGui.QSizePolicy.Expanding,
                                         QtGui.QSizePolicy.Minimum))

        self.update_buttons()
    
    #---------------------------------------------------------------------------
    #  QWidget interface:  
    #---------------------------------------------------------------------------

    def keyPressEvent(self, event):
        """ Reimplemented to process Escape key.
        """
        if event.key() == QtCore.Qt.Key_Escape:
            event.accept()
            self.emit(QtCore.SIGNAL('hidden()'))
            self.hide()
        else:
            QtGui.QWidget.keyPressEvent(self, event)

    def showEvent(self, event):
        """ Reimplemented to select all in text field and grab focus.
        """
        QtGui.QWidget.showEvent(self, event)

        self.find_edit.selectAll()
        self.find_edit.setFocus()

    #---------------------------------------------------------------------------
    #  FindWidget interface:
    #---------------------------------------------------------------------------

    def update_buttons(self, event=None):
        """ Enable or disable buttons depending on state of text field.
        """
        if self.find_edit.text() == '':
            self.previous_button.setEnabled(False)
            self.next_button.setEnabled(False)
        else:
            self.previous_button.setEnabled(True)
            self.next_button.setEnabled(True)

    def _previous_clicked(self):
        """ Handle the previous button being clicked.
        """
        self._callback(self.find_edit.text(), False, self.case_box.isChecked())

    def _next_clicked(self):
        """ Handle the previous button being clicked.
        """
        self._callback(self.find_edit.text(), True, self.case_box.isChecked())

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
        control = self._editor._scintilla
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
            control.SendScintilla(QsciBase.SCI_SETLEXER, 
                                  QsciBase.SCLEX_CONTAINER)

        for line in xrange(start_line, end_line+1):
            # We don't use lineLength here because it includes newline
            # characters. Styling these leads to strange behavior.
            position = control.positionFromLineIndex(line, 0)
            style_length = control.SendScintilla(
                QsciBase.SCI_GETLINEENDPOSITION, line) - position

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
    """ Editor for source code which uses the QScintilla widget.
    """

    #---------------------------------------------------------------------------
    #  PyFace PythonEditor interface:
    #---------------------------------------------------------------------------

    # Event that is fired on keypresses:
    key_pressed = Event(KeyPressedEvent)

    #---------------------------------------------------------------------------
    #  Editor interface:
    #---------------------------------------------------------------------------

    # The code editor is scrollable. This value overrides the default.
    scrollable = True
    
    #---------------------------------------------------------------------------
    #  SoureEditor interface:
    #---------------------------------------------------------------------------
    
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

    # The Scintilla lexer to use
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
        self.control = QtGui.QWidget()
        layout = QtGui.QVBoxLayout(self.control)
        layout.setMargin(0)

        # Create the QScintilla widget
        factory = self.factory
        self._scintilla = control = _Scintilla(self, None)
        layout.addWidget(control)

        # Connect to the QScintilla signals that we care about
        if not self.readonly:
            QtCore.QObject.connect(control, QtCore.SIGNAL('lostFocus'), 
                                   self.update_object)
            if factory.auto_set:
                control.connect(control, QtCore.SIGNAL('textChanged()'),
                                self.update_object)
        if (factory.line != '') or (factory.column != ''):
            # We need to monitor the line or column position being changed
            control.connect(control,
                    QtCore.SIGNAL('cursorPositionChanged(int, int)'),
                    self._position_changed)

        # Create the find bar
        self._find_widget = FindWidget(self.find, self.control)
        self._find_widget.hide()
        layout.addWidget(self._find_widget)
        
        # Make sure that the find bar will fit in the editor
        min_width = self._find_widget.minimumSizeHint().width()
        self.control.setMinimumWidth(min_width)

        # Grab keyboard focus whenever the find bar is closed
        QtCore.QObject.connect(self._find_widget, QtCore.SIGNAL('hidden()'),
                               self._scintilla, QtCore.SLOT('setFocus()'))
        
        # Set up the lexer. Before we set our custom lexer, we call setLexer
        # with the QSciLexer that will set the keywords and styles for the
        # basic syntax lexing. We save and then restore these keywords/styles 
        # because they get nuked when we call setLexer again.
        self.lexer = getattr(QsciBase, 'SCLEX_' + self.factory.lexer.upper(),
                             QsciBase.SCLEX_NULL)
        base_lexer_class = LEXER_MAP.get(self.lexer)
        if base_lexer_class:
            lexer = base_lexer_class(control)
            control.setLexer(lexer)
            keywords = lexer.keywords(1)
            styles = []
            attr_names = ['FORE', 'BACK', 'BOLD', 'ITALIC', 'SIZE', 'UNDERLINE']
            for style in xrange(128):
                attrs = [ control.SendScintilla(getattr(QsciBase,'SCI_STYLEGET'+a), style)
                          for a in attr_names ]
                styles.append(attrs)
        lexer = SourceLexer(self)
        control.setLexer(lexer)
        if base_lexer_class:
            if keywords:
                control.SendScintilla(QsciBase.SCI_SETKEYWORDS, 0, keywords)
            for style, attrs in enumerate(styles):
                for attr_num, attr in enumerate(attrs):
                    msg = getattr(QsciBase, 'SCI_STYLESET' + attr_names[attr_num])
                    control.SendScintilla(msg, style, attr)

        # Set a monspaced font. Use the (supposedly) same font and size as the
        # wx version.
        for style in xrange(128):
            f = lexer.font(style)
            f.setFamily('courier new')
            f.setPointSize(10)
            lexer.setFont(f, style)

        # Mark the maximum line size.
        control.setEdgeMode(Qsci.QsciScintilla.EdgeLine)
        control.setEdgeColumn(79)

        # Display line numbers in the margin.
        if factory.show_line_numbers:
            control.setMarginLineNumbers(1, True)
            control.setMarginWidth(1, 45)
        else:
            control.setMarginWidth(1, 4)
            control.setMarginsBackgroundColor(QtCore.Qt.white)

        # Configure indentation and tabs.
        control.setIndentationsUseTabs(False)
        control.setTabWidth(4)

        # Configure miscellaneous control settings:
        control.setEolMode(Qsci.QsciScintilla.EolUnix)

        if self.readonly:
            control.setReadOnly(True)
                                      
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

        # Set the control tooltip:
        self.set_tooltip()

    #---------------------------------------------------------------------------
    #  Disposes of the contents of an editor:    
    #---------------------------------------------------------------------------
                
    def dispose ( self ):
        """ Disposes of the contents of an editor.
        """
        # Make sure that the editor does not try to update as the control is
        # being destroyed:
        QtCore.QObject.disconnect(self._scintilla, QtCore.SIGNAL('lostFocus'),
                                  self.update_object)

        super( SourceEditor, self ).dispose()
    
    #---------------------------------------------------------------------------
    #  Handles the user entering input data in the edit control:
    #---------------------------------------------------------------------------

    def update_object ( self ):
        """ Handles the user entering input data in the edit control.
        """
        if not self._locked:
            try:
                value = unicode(self._scintilla.text())
                if isinstance( self.value, SequenceTypes ):
                    value = value.split()
                self.value = value
                self._scintilla.lexer().setPaper(OKColor)
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
        control = self._scintilla
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
            if self.factory.selected_line:
                self._selected_line_changed()
        self._locked = False

    #---------------------------------------------------------------------------
    #  Handles an error that occurs while setting the object's trait value:
    #---------------------------------------------------------------------------
        
    def error ( self, excp ):
        """ Handles an error that occurs while setting the object's trait value.
        """
        self._scintilla.lexer().setPaper(ErrorColor)

    #---------------------------------------------------------------------------
    #  Finds and selects the next or previous match of text:
    #---------------------------------------------------------------------------
        
    def find ( self, text, forward, match_case ):
        """ Finds and selects the next or previous match of text.
        """
        line, index = self._scintilla.getCursorPosition()
        if not forward:
            index -= len(self._scintilla.selectedText())

        # Arguments: expr, is regex, case_sensitive, whole words only, wrap
        #            around, is forward, line, index in line
        self._scintilla.findFirst(text, False, match_case, False, True, forward,
                                  line, index)

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
        
    #---------------------------------------------------------------------------
    #  Handles the set of 'marked lines' being changed:  
    #---------------------------------------------------------------------------
                
    def _mark_lines_changed ( self ):
        """ Handles the set of marked lines being changed.
        """
        lines   = self.mark_lines
        control = self._scintilla
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
        control = self._scintilla
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
            control = self._scintilla
            _, column = control.getCursorPosition()
            self._scintilla.setCursorPosition(line - 1, column)
                                  
    #---------------------------------------------------------------------------
    #  Handles the 'column' trait being changed:  
    #---------------------------------------------------------------------------
                                              
    def _column_changed ( self, column ):
        if not self._locked:
            control = self._scintilla
            line, _ = control.getCursorPosition()
            self._scintilla.setCursorPosition(line, column - 1)

    #---------------------------------------------------------------------------
    #  Handles the cursor position being changed:  
    #---------------------------------------------------------------------------
                        
    def _position_changed(self, line, column):
        """ Handles the cursor position being changed.
        """
        control = self._scintilla
        self._locked = True
        self.line = line
        self.column = column
        self._locked = False
        self.selected_text = unicode(control.selectedText())
        
    #---------------------------------------------------------------------------
    #  Handles a key being pressed within the editor:    
    #---------------------------------------------------------------------------
                
    def _key_pressed_changed ( self, event ):
        """ Handles a key being pressed within the editor.
        """
        key_bindings = self.factory.key_bindings
        if key_bindings:
            processed = key_bindings.do(event.event, self.ui.handler, 
                                        self.ui.info)
        else:
            processed = False
        if not processed and event.event.matches(QtGui.QKeySequence.Find):
            self._find_widget.show()

    #---------------------------------------------------------------------------
    #  Handles the styling of the editor:
    #---------------------------------------------------------------------------

    def _dim_color_changed(self):
        self._scintilla.SendScintilla(QsciBase.SCI_STYLESETFORE, 
                                      self.dim_style_number,
                                      QtGui.QColor(self.dim_color))

    def _squiggle_color_changed(self):
        self._scintilla.SendScintilla(QsciBase.SCI_INDICSETSTYLE, 2,
                                      QsciBase.INDIC_SQUIGGLE)
        self._scintilla.SendScintilla(QsciBase.SCI_INDICSETFORE, 2,
                                      QtGui.QColor(self.squiggle_color))

    @on_trait_change('dim_lines, squiggle_lines')
    def _style_document(self):
        self._scintilla.recolor()


# Define the simple, custom, text and readonly editors, which will be accessed
# by the editor factory for code editors.

CustomEditor = SimpleEditor = TextEditor = SourceEditor

class ReadonlyEditor(SourceEditor):

    # Set the value of the readonly trait.
    readonly = True
