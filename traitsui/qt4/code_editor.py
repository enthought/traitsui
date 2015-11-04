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

from pyface.qt import QtCore, QtGui

from pyface.ui.qt4.code_editor.code_widget import AdvancedCodeWidget
from traits.api import Str, Unicode, List, Int, Event, Bool, \
    TraitError, on_trait_change
from traits.trait_base import SequenceTypes

# FIXME: ToolkitEditorFactory is a proxy class defined here just for backward
# compatibility. The class has been moved to the
# traitsui.editors.code_editor file.
from traitsui.editors.code_editor import ToolkitEditorFactory

from pyface.key_pressed_event import KeyPressedEvent

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

class SourceEditor ( Editor ):
    """ Editor for source code which uses the advanced code widget.
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

    # The start position of the selected
    selected_start_pos = Int

    # The end position of the selected
    selected_end_pos = Int

    # The currently selected text
    selected_text = Unicode

    # The list of line numbers to mark
    mark_lines = List( Int )

    # The current line number
    line = Event

    # The current column
    column = Event

    # The lines to be dimmed
    dim_lines = List(Int)
    dim_color = Str
    dim_style_number = Int(16) # 0-15 are reserved for the python lexer

    # The lines to have squiggles drawn under them
    squiggle_lines = List(Int)
    squiggle_color = Str

    # The lexer to use.
    lexer = Str

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
        layout.setContentsMargins(0, 0, 0, 0)

        self._widget = control = AdvancedCodeWidget(None, lexer=self.factory.lexer)
        layout.addWidget(control)

        factory = self.factory

        # Set up listeners for the signals we care about
        code_editor = self._widget.code

        if self.readonly:
            code_editor.setReadOnly(True)
        else:
            if factory.auto_set:
                code_editor.textChanged.connect(self.update_object)
            else:
                code_editor.focus_lost.connect(self.update_object)

        if factory.selected_text != '':
            code_editor.selectionChanged.connect(self._selection_changed)
        if (factory.line != '') or (factory.column != ''):
            code_editor.cursorPositionChanged.connect(self._position_changed)

        code_editor.line_number_widget.setVisible(factory.show_line_numbers)

        # Make sure the editor has been initialized:
        self.update_editor()

        # Set up any event listeners:
        self.sync_value( factory.mark_lines, 'mark_lines', 'from',
                         is_list = True )
        self.sync_value( factory.selected_line, 'selected_line', 'from' )
        self.sync_value( factory.selected_text, 'selected_text', 'to' )
        self.sync_value( factory.line, 'line' )
        self.sync_value( factory.column, 'column' )

        self.sync_value( factory.selected_start_pos, 'selected_start_pos', 'to')
        self.sync_value( factory.selected_end_pos, 'selected_end_pos', 'to')

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
        QtCore.QObject.disconnect(self._widget, QtCore.SIGNAL('lostFocus'),
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
                value = unicode(self._widget.code.toPlainText())
                if isinstance( self.value, SequenceTypes ):
                    value = value.split()
                self.value = value
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
        new_value = self.value
        if isinstance( new_value, SequenceTypes ):
            new_value = '\n'.join( [ line.rstrip() for line in new_value ] )
        control = self._widget
        if control.code.toPlainText() != new_value:
            control.code.setPlainText(new_value)

            if self.factory.selected_line:
                # TODO: update the factory selected line
                pass

            # TODO: put the cursor somewhere

        self._locked = False

    #---------------------------------------------------------------------------
    #  Handles an error that occurs while setting the object's trait value:
    #---------------------------------------------------------------------------

    def error ( self, excp ):
        """ Handles an error that occurs while setting the object's trait value.
        """
        pass

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
        # FIXME: Not implemented at this time.
        return

    def _mark_lines_items_changed ( self ):
        self._mark_lines_changed()

    #---------------------------------------------------------------------------
    #  Handles the currently 'selected line' being changed:
    #---------------------------------------------------------------------------

    def _selection_changed(self):
        self.selected_text = unicode(self._widget.code.textCursor().selectedText())
        start = self._widget.code.textCursor().selectionStart()
        end = self._widget.code.textCursor().selectionEnd()

        if start > end:
            start, end = end, start

        self.selected_start_pos = start
        self.selected_end_pos = end

    def _selected_line_changed ( self ):
        """ Handles a change in which line is currently selected.
        """
        control = self._widget
        line = max(1, min(control.lines(), self.selected_line))
        _, column = control.get_line_column()
        control.set_line_column(line, column)
        if self.factory.auto_scroll:
            control.centerCursor()

    #---------------------------------------------------------------------------
    #  Handles the 'line' trait being changed:
    #---------------------------------------------------------------------------

    def _line_changed ( self, line ):
        if not self._locked:
            _, column = self._widget.get_line_column()
            self._widget.set_line_column(line, column)
            if self.factory.auto_scroll:
                self._widget.centerCursor()

    #---------------------------------------------------------------------------
    #  Handles the 'column' trait being changed:
    #---------------------------------------------------------------------------

    def _column_changed ( self, column ):
        if not self._locked:
            line, _ = self._widget.get_line_column()
            self._widget.set_line_column(line, column)

    #---------------------------------------------------------------------------
    #  Handles the cursor position being changed:
    #---------------------------------------------------------------------------

    def _position_changed(self):
        """ Handles the cursor position being changed.
        """
        control = self._widget
        self._locked = True
        self.line, self.column = control.get_line_column()
        self._locked = False
        self.selected_text = control.get_selected_text()
        if self.factory.auto_scroll:
            self._widget.centerCursor()

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
        pass

    def _squiggle_color_changed(self):
        pass

    @on_trait_change('dim_lines, squiggle_lines')
    def _style_document(self):
        self._widget.set_warn_lines(self.squiggle_lines)



# Define the simple, custom, text and readonly editors, which will be accessed
# by the editor factory for code editors.

CustomEditor = SimpleEditor = TextEditor = SourceEditor

class ReadonlyEditor(SourceEditor):

    # Set the value of the readonly trait.
    readonly = True
