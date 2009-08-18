#------------------------------------------------------------------------------
# Copyright (c) 2009, Enthought, Inc.
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in enthought/LICENSE.txt and may be redistributed only
# under the conditions described in the aforementioned license.  The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
# Thanks for using Enthought open source!
#
# Author: Evan Patterson
# Date: 08/17/09
#------------------------------------------------------------------------------

# Standard library imports.
import os, sys
import code
import re, string

# Major package imports.
from PyQt4 import QtCore, QtGui
from PyQt4.Qsci import QsciScintilla, QsciScintillaBase as QsciBase, \
    QsciStyle, QsciLexerPython

# Enthought library imports.
from enthought.traits.api import Event, implements

# Local imports.
from enthought.pyface.i_python_shell import IPythonShell, MPythonShell
from enthought.pyface.key_pressed_event import KeyPressedEvent
from widget import Widget

#-------------------------------------------------------------------------------
# 'PythonShell' class:
#-------------------------------------------------------------------------------

class PythonShell(MPythonShell, Widget):
    """ The toolkit specific implementation of a PythonShell.  See the
    IPythonShell interface for the API documentation.
    """

    implements(IPythonShell)

    #### 'IPythonShell' interface #############################################

    command_executed = Event

    key_pressed = Event(KeyPressedEvent)

    #--------------------------------------------------------------------------
    # 'object' interface
    #--------------------------------------------------------------------------

    # FIXME v3: Either make this API consistent with other Widget sub-classes
    # or make it a sub-class of HasTraits.
    def __init__(self, parent, **traits):
        """ Creates a new pager. """

        # Base class constructor.
        super(PythonShell, self).__init__(**traits)

        # Create the toolkit-specific control that represents the widget.
        self.control = self._create_control(parent)

        # Set up to be notified whenever a Python statement is executed:
        self.control.exec_callback = self._on_command_executed

    #--------------------------------------------------------------------------
    # 'IPythonShell' interface
    #--------------------------------------------------------------------------

    def interpreter(self):
        return self.control.interpreter

    def execute_command(self, command, hidden=True):
        self.control.execute(command, hidden=hidden)

    #--------------------------------------------------------------------------
    # Protected 'IWidget' interface.
    #--------------------------------------------------------------------------

    def _create_control(self, parent):
        return QPythonShellWidget(parent)

#-------------------------------------------------------------------------------
# 'QConsoleWidget' class and associated constants:
#-------------------------------------------------------------------------------

# Note: This code was adapted from the wx ConsoleWidget in IPython, and should
# at some point be cleaned up and moved upstream.

# New marker definitions
_INPUT_MARKER = 29
_ERROR_MARKER = 30
_COMPLETE_BUFFER_MARKER = 31

# New style numbers
_STDOUT_STYLE = 15
_STDERR_STYLE = 16
_TRACE_STYLE  = 17

_DEFAULT_STYLES = {
    # Braces
    QsciBase.STYLE_BRACELIGHT : 'fore:#00AA00,back:#000000,bold',
    QsciBase.STYLE_BRACEBAD   : 'fore:#FF0000,back:#000000,bold',

    # Python lexer styles
    QsciLexerPython.Comment                  : 'fore:#007F00',
    QsciLexerPython.Number                   : 'fore:#007F7F',
    QsciLexerPython.DoubleQuotedString       : 'fore:#7F007F,italic',
    QsciLexerPython.SingleQuotedString       : 'fore:#7F007F,italic',
    QsciLexerPython.Keyword                  : 'fore:#00007F,bold',
    QsciLexerPython.TripleSingleQuotedString : 'fore:#7F0000',
    QsciLexerPython.TripleDoubleQuotedString : 'fore:#7F0000',
    QsciLexerPython.ClassName                : 'fore:#0000FF,bold,underline',
    QsciLexerPython.FunctionMethodName       : 'fore:#007F7F,bold',
    QsciLexerPython.Operator                 : 'bold',
    }

_DEFAULT_MARKER_COLORS = {
    _TRACE_STYLE  : '#FAFAF1', # Nice green
    _STDOUT_STYLE : '#FDFFD3', # Nice yellow
    _STDERR_STYLE : '#FFF1F1', # Nice red 
    }

# Translation table from ANSI escape sequences to logical ANSI color index and
# SVG color keywords.
ANSI_COLORS = { '0;30': [0,  'black'],          '0;31': [1,  'red'],
                '0;32': [2,  'green'],          '0;33': [3,  'brown'],
                '0;34': [4,  'blue'],           '0;35': [5,  'purple'],
                '0;36': [6,  'cyan'],           '0;37': [7,  'lightgrey'],
                '1;30': [8,  'darkgrey'],       '1;31': [9,  'red'],
                '1;32': [10, 'seagreen'],       '1;33': [11, 'yellow'],
                '1;34': [12, 'lightblue'],      '1;35': [13, 'mediumvioletred'],
                '1;36': [14, 'lightsteelblue'], '1;37': [15, 'yellow'] }

# The offset from the logical ANSI color index to its corresponding Scintilla
# style number
_ANSI_STYLE_START = 64

# Platform specific fonts
if sys.platform == 'win32':
    _FACES = { 'times': 'Times New Roman',
               'mono' : 'Courier New',
               'helv' : 'Arial',
               'other': 'Comic Sans MS',
               'size' : 10,
               'size2': 8 }
elif sys.platform == 'darwin':
    _FACES = { 'times': 'Times New Roman',
               'mono' : 'Monaco',
               'helv' : 'Arial',
               'other': 'Comic Sans MS',
               'size' : 12,
               'size2': 10 }
else:
    _FACES = { 'times': 'Times',
               'mono' : 'Courier',
               'helv' : 'Helvetica',
               'other': 'new century schoolbook',
               'size' : 10,
               'size2': 8 }

class QConsoleWidget(QsciScintilla):
    """ Specialized styled text control view for console-like workflow.

        This widget is mainly interested in dealing with the prompt and keeping
        the cursor inside the editing line.
    """

    # 

    # Matches ANSI color specification of form:
    # (Possible SOH)ESC[(%color%)m(Possible STX)
    color_pattern = re.compile('\x01?\x1b\[(.*)m\x02?')

    # Matches XTerm title specification of form: ESC]0;(%title%)BEL
    title_pattern = re.compile('\x1b]0;(.*)\x07')

    #--------------------------------------------------------------------------
    # 'object' interface
    #--------------------------------------------------------------------------

    def __init__(self, parent, styles=_DEFAULT_STYLES, 
                 marker_colors=_DEFAULT_MARKER_COLORS, ansi_colors=ANSI_COLORS):
        """ Initialize internal variables and up all the styling options for the
            console.
        """
        QsciScintilla.__init__(self, parent)

        # Initialize internal variables
        self.title = 'Console' # captured from ANSI escape sequences
        self._enter_processing = False
        self._prompt_line, self._prompt_index = 0, 0

        # Define our custom markers
        self.markerDefine(QsciScintilla.Background, _COMPLETE_BUFFER_MARKER)
        self.markerDefine(QsciScintilla.Background, _INPUT_MARKER)
        self.markerDefine(QsciScintilla.Background, _ERROR_MARKER)

        # Indentation configuration
        self.setIndentationWidth(4)
        self.setIndentationsUseTabs(True)
        self.setTabWidth(4)

        # Hide margins
        self.setMarginWidth(0, 0)
        self.setMarginWidth(1, 0)
        self.setMarginWidth(2, 0)

        # Misc. options
        #self.setEolMode(QsciScintilla.EolWindows)
        self.setWrapMode(QsciScintilla.WrapCharacter)

        # Define Scintilla text and marker styles
        self.set_styles(styles)
        self.set_marker_colors(marker_colors)
        self.set_ansi_colors(ansi_colors)        

    #--------------------------------------------------------------------------
    # 'QWidget' interface
    #--------------------------------------------------------------------------

    def keyPressEvent(self, event):
        """ Reimplemented to create a console-like interface.
        """
        #line, index = self.getCursorPosition()
        key = event.key()
        ctrl_down = event.modifiers() & QtCore.Qt.ControlModifier

        intercepted = True
        if (key == QtCore.Qt.Key_L and ctrl_down):
            vb = self.verticalScrollBar()
            vb.setValue(vb.maximum())
        elif (key == QtCore.Qt.Key_K and ctrl_down):
            line, index = self.getCursorPosition()
            index -= len(self._last_prompt)
            self.input_buffer = self.input_buffer[:index]
        elif (key == QtCore.Qt.Key_A and ctrl_down):
            self.setCursorPosition(0, 0)
        elif (key == QtCore.Qt.Key_E and ctrl_down):
            self.setCursorPosition(*self._end_position())
        else:
            intercepted = False
        
        if not self.isListActive():
            if (key in (QtCore.Qt.Key_Return, QtCore.Qt.Key_Enter)):
                intercepted = True
                if not self._enter_processing:
                    self._enter_processing = True
                    try:
                        self.enter_pressed()
                    finally:
                        self._enter_processing = False

        if not intercepted:
            QsciScintilla.keyPressEvent(self, event)
        self._keep_cursor_in_buffer()

    #--------------------------------------------------------------------------
    # 'QConsoleWidget' interface
    #--------------------------------------------------------------------------

    # The buffer being edited:
    def _set_input_buffer(self, string):
        self.setSelection(self._prompt_line, self._prompt_index, 
                          *self._end_position())
        self.removeSelectedText()
        self.insertAt(string, self._prompt_line, self._prompt_index)
        self.setCursorPosition(*self._end_position())

    def _get_input_buffer(self):
        input_buffer = str(self.text(self._prompt_line))[self._prompt_index:]
        return input_buffer.replace(os.linesep, '\n')

    input_buffer = property(_get_input_buffer, _set_input_buffer)

    def write(self, text, refresh=True):
        """ Write given text to buffer, translating ANSI escape sequences as
            appropriate.
        """
        # WARNING: Do not put print statements to sys.stdout/sys.stderr in this
        # method, as print will call this method, creating an infinite loop.
        
        title = self.title_pattern.split(text)
        if len(title) > 1:
            self.title = title[-2]

        text = self.title_pattern.sub('', text)
        segments = self.color_pattern.split(text)
        segment = segments.pop(0)
        #self.setCursorPosition(*self._end_position())
        self.SendScintilla(QsciBase.SCI_STARTSTYLING, self.text().length(), 
                           0xff)
        try:
            self.append(text)
        except UnicodeDecodeError:
            # FIXME: Do I really want to skip the exception?
            pass
        
        for ansi_tag, text in zip(segments[::2], segments[1::2]):
            self.SendScintilla(QsciBase.SCI_STARTSTYLING, 
                               self.text().length(), 0xff)
            try:
                self.append(text)
            except UnicodeDecodeError:
                # FIXME: Do I really want to skip the exception?
                pass
            if ansi_tag in self._ansi_colors:
                style = self._ansi_colors[ansi_tag][0] + _ANSI_STYLE_START
            else:
                style = 0
            self.SendScintilla(QSciBase.SCI_SETSTYLING, len(text), style)
                
        self.setCursorPosition(*self._end_position())
        if refresh:
            self.update()

    def new_prompt(self, prompt):
        """ Prints a prompt at start of line, and move the start of the current
            block there.
        """
        self.write(prompt, refresh=False)
        self._prompt_line, self._prompt_index = self._end_position()
        self.ensureCursorVisible()
        self._last_prompt = prompt

    def enter_pressed(self):
        """ Called when the enter key is pressed. Must be implemented by
            subclasses.
        """
        raise NotImplementedError

    def set_ansi_colors(self, ansi_colors):
        """ Sets the styles of the underlying Scintilla widget that we will use
            for ANSI color codes.
        """
        self._ansi_colors = ansi_colors
        for color_num, color_name in ansi_colors.values():
            style_num = color_num + _ANSI_STYLE_START
            style = QsciStyle(style_num)
            style.setColor(QtGui.QColor(color_name))
            font = QtGui.QFont(_FACES['mono'], _FACES['size'])
            font.setBold(True)
            style.setFont(font)

    def set_styles(self, style_dict):
        """ Sets the styles of the underlying Scintilla widget by parsing a
            style specification a la wx's SetStyleSpec.
        """
        for style_num, style_string in style_dict.items():
            style = QsciStyle(style_num)
            font = QtGui.QFont(_FACES['mono'], _FACES['size'])
            for attr in style_string.split(','):
                attr = attr.strip().split(':')
                name = attr[0].strip()
                if name == 'fore':
                    style.setColor(QtGui.QColor(attr[1]))
                elif name == 'back':
                    style.setPaper(QtGui.QColor(attr[1]))
                elif name == 'face':
                    font.setFamily(attr[1])
                elif name == 'size':
                    font.setPointSize(int(attr[1]))
                elif name == 'bold':
                    font.setBold(True)
                elif name == 'italic':
                    font.setItalic(True)
                elif name == 'underline':
                    font.setUnderline(True)
            style.setFont(font)

    def set_marker_colors(self, colors):
        """ Sets the background color of the console region markers.
        """
        self.setMarkerBackgroundColor(QtGui.QColor(colors[_TRACE_STYLE]),
                                      _COMPLETE_BUFFER_MARKER)
        self.setMarkerBackgroundColor(QtGui.QColor(colors[_STDOUT_STYLE]),
                                      _INPUT_MARKER)
        self.setMarkerBackgroundColor(QtGui.QColor(colors[_STDERR_STYLE]),
                                      _ERROR_MARKER)

    #--------------------------------------------------------------------------
    # Protected interface
    #--------------------------------------------------------------------------

    def _keep_cursor_in_buffer(self):
        """ Ensures that the cursor is inside the editing region. Returns 
            whether the cursor was moved.
        """
        adjusted = False
        line, index = self.getCursorPosition()

        if line != self._prompt_line:
            line = self._prompt_line
            adjusted = True

        if index < self._prompt_index:
            index = self._prompt_index
            adjusted = True

        if adjusted:
            self.setCursorPosition(line, index)
        return adjusted

    def _end_position(self):
        """ Returns the line and index of the last character.
        """
        line = self.lines() - 1
        return line, self.text(line).length()

#-------------------------------------------------------------------------------
# 'QPythonShellWidget' class:
#-------------------------------------------------------------------------------

class QPythonShellWidget(QConsoleWidget):
    """ An embeddable Python shell.
    """

    #--------------------------------------------------------------------------
    # 'object' interface
    #--------------------------------------------------------------------------

    def __init__(self, parent=None):
        """ Initialise the instance.
        """
        QConsoleWidget.__init__(self, parent)

        self.interpreter = code.InteractiveInterpreter()
        self.exec_callback = None

        self._hidden = False
        self._more = False
        self._lines = []
        self._history = []

        # Interpreter banner.
        self.write('Python %s on %s.\n' % (sys.version, sys.platform))
        self.write('Type "copyright", "credits" or "license" for more information.\n')
        self.new_prompt()

    #--------------------------------------------------------------------------
    # file-like object interface
    #--------------------------------------------------------------------------    

    def flush(self):
        """ Emulate a file.
        """
        pass

    def write(self, text, refresh=True):
        """ Emulate a file. Write only if hidden is False.
        """
        if not self._hidden:
            QConsoleWidget.write(self, text, refresh)

    #---------------------------------------------------------------------------
    # 'QConsoleWidget' interface
    #---------------------------------------------------------------------------

    def enter_pressed(self):
        self.write(os.linesep, refresh=False)
        text = self.input_buffer.rstrip()
        if text:
            self.execute(text)
        else:
            self.new_prompt()

    #--------------------------------------------------------------------------
    # 'QPythonShellWidget' interface
    #--------------------------------------------------------------------------

    def new_prompt(self, prompt='>>> '):
        """ Convenience method because regular prompt is always the same.
        """
        QConsoleWidget.new_prompt(self, prompt)

    def execute(self, command, hidden=False):
        """ Execute a (possibly partial) Python string.
        """
        self._lines.append(command)
        source = os.linesep.join(self._lines)

        # Save the current std* and point them here.
        old_stdin, old_stdout, old_stderr = sys.stdin, sys.stdout, sys.stderr
        sys.stdin = sys.stdout = sys.stderr = self

        # Run the source code in the interpeter
        self._hidden = hidden
        try:
            self._more = self.interpreter.runsource(source)
        finally:
            self._hidden = False
            # Restore std* unless the executed changed them.
            if sys.stdin is self:
                sys.stdin = old_stdin
            if sys.stdout is self:
                sys.stdout = old_stdout
            if sys.stderr is self:
                sys.stderr = old_stderr

        if not self._more:
            self._lines = []
            if self.exec_callback:
                self.exec_callback()

        if not hidden:
            self._history.append(QtCore.QString(command))
            if self._more:
                prompt = '.' * (len(self._last_prompt) - 1) + ' '
                self.new_prompt(prompt)
            else:
                self.new_prompt()
