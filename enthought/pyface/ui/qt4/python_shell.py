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
import __builtin__
from code import InteractiveInterpreter
import keyword
from math import ceil, floor
import re
import sys
from time import time

# Major package imports.
from PyQt4 import QtCore, QtGui
from PyQt4.Qsci import QsciScintilla, QsciScintillaBase as QsciBase, \
    QsciAbstractAPIs, QsciLexerPython, QsciStyle

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
        if not hidden:
            self.control.input_buffer = command
        self.control.execute(command, hidden=hidden)

    #--------------------------------------------------------------------------
    # 'MPythonShell' interface
    #--------------------------------------------------------------------------

    def _new_prompt(self):
        self.control.write('\n')
        self.control.new_prompt()

    def _set_input_buffer(self, command):
        self.control.input_buffer = command

    #--------------------------------------------------------------------------
    # 'IWidget' interface.
    #--------------------------------------------------------------------------

    def _create_control(self, parent):
        return QPyfacePythonShellWidget(self, parent)

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
    _FONT = 'Courier New'
    _FONT_SIZE = 10
elif sys.platform == 'darwin':
    _FONT = 'Monaco'
    _FONT_SIZE = 12
else:
    _FONT = 'Courier'
    _FONT_SIZE = 10

class QConsoleWidget(QsciScintilla):
    """ Specialized styled text control view for console-like workflow.

        This widget is mainly interested in dealing with the prompt and keeping
        the cursor inside the editing line.
    """

    # Matches ANSI color specification of form:
    # (Possible SOH)ESC[%color%m(Possible STX)
    color_pattern = re.compile('\x01?\x1b\[(.*)m\x02?')

    # Matches XTerm title specification of form: ESC]0;%title%BEL
    title_pattern = re.compile('\x1b]0;(.*)\x07')

    # When ctrl is pressed, map certain keys to other keys (without the ctrl):
    _ctrl_down_remap = { QtCore.Qt.Key_B : QtCore.Qt.Key_Left,
                         QtCore.Qt.Key_F : QtCore.Qt.Key_Right,
                         QtCore.Qt.Key_A : QtCore.Qt.Key_Home,
                         QtCore.Qt.Key_E : QtCore.Qt.Key_End,
                         QtCore.Qt.Key_P : QtCore.Qt.Key_Up,
                         QtCore.Qt.Key_N : QtCore.Qt.Key_Down,
                         QtCore.Qt.Key_D : QtCore.Qt.Key_Delete, }

    #--------------------------------------------------------------------------
    # 'object' interface
    #--------------------------------------------------------------------------

    def __init__(self, parent, styles=_DEFAULT_STYLES, 
                 marker_colors=_DEFAULT_MARKER_COLORS, ansi_colors=ANSI_COLORS,
                 _base_init=True):
        """ Initialize internal variables and up all the styling options for the
            console.
        """
        # Hack for QPythonShellWidget subclass (see __init__ for info)
        if _base_init:
            QsciScintilla.__init__(self, parent)

        # Initialize internal variables
        self.title = 'Console' # captured from ANSI escape sequences
        self._console_inited = False
        self._enter_processing = False
        self._last_refresh_time = 0
        self._line_width = 80 # initialize just to be safe
        self._prompt_line, self._prompt_index = 0, 0
        self._reading = False

        # Define our custom context menu
        self._context_menu = QtGui.QMenu(self)

        self._undo_action = QtGui.QAction('Undo', self)
        QtCore.QObject.connect(self._undo_action, QtCore.SIGNAL('triggered()'),
                               self, QtCore.SLOT('undo()'))
        self._context_menu.addAction(self._undo_action)

        self._redo_action = QtGui.QAction('Redo', self._context_menu)
        QtCore.QObject.connect(self._redo_action, QtCore.SIGNAL('triggered()'),
                               self, QtCore.SLOT('redo()'))
        self._context_menu.addAction(self._redo_action)
        self._context_menu.addSeparator()

        copy_action = QtGui.QAction('Copy', self)
        QtCore.QObject.connect(copy_action, QtCore.SIGNAL('triggered()'),
                               self, QtCore.SLOT('copy()'))
        QtCore.QObject.connect(self, QtCore.SIGNAL('copyAvailable(bool)'),
                               copy_action, QtCore.SLOT('setEnabled(bool)'))
        self._context_menu.addAction(copy_action)

        self._paste_action = QtGui.QAction('Paste', self)
        QtCore.QObject.connect(self._paste_action, QtCore.SIGNAL('triggered()'),
                               self, QtCore.SLOT('paste()'))
        self._context_menu.addAction(self._paste_action)
        self._context_menu.addSeparator()

        select_all_action = QtGui.QAction('Select All', self)
        QtCore.QObject.connect(select_all_action, QtCore.SIGNAL('triggered()'),
                               self, QtCore.SLOT('selectAll()'))
        self._context_menu.addAction(select_all_action)

        # Define our custom markers
        self.markerDefine(QsciScintilla.Background, _COMPLETE_BUFFER_MARKER)
        self.markerDefine(QsciScintilla.Background, _INPUT_MARKER)
        self.markerDefine(QsciScintilla.Background, _ERROR_MARKER)

        # Configure indentation
        self.setIndentationWidth(4)
        self.setIndentationsUseTabs(True)
        self.setTabWidth(4)

        # Do not wrap text--we will do it ourselves.
        self.setWrapMode(QsciScintilla.WrapNone)
        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)

        # Configure misc. options
        self.SendScintilla(QsciBase.SCI_SETLAYOUTCACHE, QsciBase.SC_CACHE_PAGE)
        self.setMarginWidth(1, 0)

        # Define Scintilla text and marker styles
        self.set_styles(styles)
        self.set_marker_colors(marker_colors)
        self.set_ansi_colors(ansi_colors)

    #--------------------------------------------------------------------------
    # file-like object interface
    #--------------------------------------------------------------------------    

    def flush(self):
        """ This buffer does not need to be flushed.
        """
        pass

    def isatty(self):
        """ This buffer is interactive.
        """
        return True

    def readline(self):
        """ Read and return one line from the buffer.
        """
        self.new_prompt('')

        self._reading = True
        while self._reading:
            QtCore.QCoreApplication.processEvents()

        result = self.input_buffer + '\n'
        self.write('\n', refresh=False)
        return result

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
        self.SendScintilla(QsciBase.SCI_STARTSTYLING, self.text().length())
        try:
            self.append(segment)
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
            self.SendScintilla(QsciBase.SCI_SETSTYLING, len(text), style)
                
        self.setCursorPosition(*self._end_position())

        if refresh:
            current_time = time()
            if current_time - self._last_refresh_time > 0.03:
                self.repaint()
                self._last_refresh_time = current_time 

    def writelines(self, lines, refresh=True):
        """ Write a list of lines to the buffer.
        """
        for line in lines:
            self.write(line, refresh=False)
            self.write('\n', refresh=refresh)

    #--------------------------------------------------------------------------
    # 'QWidget' interface
    #--------------------------------------------------------------------------

    def contextMenuEvent(self, event):
        """ Reimplemented to create a menu without destructive actions like
            'Cut' and 'Delete'.
        """
        self._undo_action.setEnabled(self.isUndoAvailable())
        self._redo_action.setEnabled(self.isRedoAvailable())

        can_paste = bool(self.SendScintilla(QsciBase.SCI_CANPASTE))
        self._paste_action.setEnabled(can_paste)
        
        self._context_menu.exec_(event.globalPos())

    def keyPressEvent(self, event):
        """ Reimplemented to create a console-like interface.
        """
        intercepted = False
        line, index = self.getCursorPosition()
        key = event.key()
        ctrl_down = event.modifiers() & QtCore.Qt.ControlModifier

        if ctrl_down:
            if key in self._ctrl_down_remap:
                ctrl_down = False
                key = self._ctrl_down_remap[key]
                event = QtGui.QKeyEvent(QtCore.QEvent.KeyPress, key, 
                                        QtCore.Qt.NoModifier)

            elif key == QtCore.Qt.Key_L:
                vb = self.verticalScrollBar()
                vb.setValue(vb.maximum())
                intercepted = True

            elif key == QtCore.Qt.Key_K:
                self.input_buffer = ''
                intercepted = True

            elif key == QtCore.Qt.Key_T:
                # Transposing lines is not appropriate for a console.
                # FIXME: Transpose characters instead.
                intercepted = True
        
        if not self.isListActive():
            if key in (QtCore.Qt.Key_Return, QtCore.Qt.Key_Enter):
                if self._reading:
                    self._reading = False
                elif not self._enter_processing:
                    self._enter_processing = True
                    try:
                        self.enter_pressed()
                    finally:
                        self._enter_processing = False
                intercepted = True

            elif key == QtCore.Qt.Key_Up:
                intercepted = self._reading or not self.up_pressed()

            elif key == QtCore.Qt.Key_Down:
                intercepted = self._reading or not self.down_pressed()

            elif key == QtCore.Qt.Key_Left:
                intercepted = not self._in_buffer(line, index - 1)

            elif key == QtCore.Qt.Key_Home:
                if (self._in_buffer(line, index) and 
                    event.modifiers() & QtCore.Qt.ShiftModifier):
                    self.setSelection(line, index, line, self._prompt_index)
                else:
                    self.setCursorPosition(0, 0)
                intercepted = True

            elif key == QtCore.Qt.Key_Backspace:
                sel_line, sel_index, _, _ = self.getSelection()
                if sel_line == -1:
                    intercepted = not self._in_buffer(line, index - 1)
                else:
                    intercepted = not self._in_buffer(sel_line, sel_index)
                if event.modifiers() & QtCore.Qt.AltModifier:
                    # Alt-backspace is mapped to Undo by default? 
                    # FIXME: Do a backwards word chomp.
                    intercepted = True

            elif key == QtCore.Qt.Key_Delete:
                sel_line, sel_index, _, _ = self.getSelection()
                if sel_line == -1:
                    intercepted = not self._in_buffer(line, index)
                else:
                    intercepted = not self._in_buffer(sel_line, sel_index)

            self._keep_cursor_in_buffer()

        if not intercepted:
            QsciScintilla.keyPressEvent(self, event)

    def resizeEvent(self, event):
        """ Reimplemented to recalculate line width.
        """
        self._calc_line_width()
        QsciScintilla.resizeEvent(self, event)

    def showEvent(self, event):
        """ Reimplemented to call 'console_init' when the widget is first shown.
            We call console_init here (rather than in __init__) to ensure that
            the line width used for splitting the first lines reflects the
            final, post-layout width of widget. See 'append' for more info.
        """
        if not self._console_inited and not event.spontaneous():
            self.console_init()
            self._console_inited = True
        QsciScintilla.showEvent(self, event)

    #--------------------------------------------------------------------------
    # 'QScintilla' interface
    #--------------------------------------------------------------------------

    def append(self, string):
        """ Reimplemented to improve performance. We split long lines into
            shorter ones because QScintilla's line wrapping performs *very*
            badly for long lines (QFontMetric.width appears to get called at
            least twice for every character). We can do this much faster than
            QScintilla because we can guarantee a monospaced font.
        """
        # Code based on default implementation in 'qsciscintilla.cpp'
        for i, line in enumerate(string.splitlines(True)):
            stripped = line.rstrip('\n\r')
            num_lines = int(ceil(len(stripped) / float(self._line_width)))
            for j in xrange(max(1, num_lines)):
                if j:
                    self.SendScintilla(QsciBase.SCI_APPENDTEXT, 1, '\n')
                start = j * self._line_width
                sub = line[start : start + self._line_width]
                self.SendScintilla(QsciBase.SCI_APPENDTEXT, len(sub), sub)

        self.SendScintilla(QsciBase.SCI_EMPTYUNDOBUFFER)

    def paste(self):
        """ Reimplemented to ensure that text is pasted in editing region.
        """
        self._keep_cursor_in_buffer()
        QsciScintilla.paste(self)

    #--------------------------------------------------------------------------
    # 'QConsoleWidget' concrete interface
    #--------------------------------------------------------------------------

    def _set_input_buffer(self, string):
        # Remove old text
        self.setSelection(self._prompt_line, self._prompt_index, 
                          *self._end_position())
        self.removeSelectedText()
        
        # Add continuation prompts where necessary
        lines = string.splitlines()
        cont_prompt = self.continuation_prompt()
        for i in xrange(1, len(lines)):
            lines[i] = cont_prompt + lines[i]
        string = '\n'.join(lines)

        # Insert string and move cursor to end of buffer
        self.insertAt(string, self._prompt_line, self._prompt_index)
        self.recolor(self.positionFromLineIndex(self._prompt_line, 
                                                self._prompt_index), -1)
        self.setCursorPosition(*self._end_position())

    def _get_input_buffer(self):
        lines = [ str(self.text(self._prompt_line))[self._prompt_index:] ]
        cont_prompt_index = len(self.continuation_prompt())
        for i in xrange(self._prompt_line + 1, self.lines()):
            lines.append(str(self.text(i))[cont_prompt_index:])
        return ''.join(lines)

    # The buffer being edited:
    input_buffer = property(_get_input_buffer, _set_input_buffer)

    def new_prompt(self, prompt):
        """ Prints a prompt at start of line, and move the start of the current
            block there.
        """
        self.write(prompt, refresh=False)
        self._prompt_line, self._prompt_index = self._end_position()
        self.ensureCursorVisible()
        self._last_prompt = prompt

    def set_ansi_colors(self, ansi_colors):
        """ Sets the styles of the underlying Scintilla widget that we will use
            for ANSI color codes.
        """
        self._ansi_colors = ansi_colors
        for color_num, color_name in ansi_colors.values():
            style_num = color_num + _ANSI_STYLE_START
            style = QsciStyle(style_num)
            style.setColor(QtGui.QColor(color_name))
            font = QtGui.QFont(_FONT, _FONT_SIZE)
            font.setBold(True)
            style.setFont(font)

    def set_styles(self, style_dict):
        """ Sets the styles of the underlying Scintilla widget by parsing a
            style specification a la wx's SetStyleSpec.
        """
        for style_num in xrange(128):
            style = QsciStyle(style_num)
            font = QtGui.QFont(_FONT, _FONT_SIZE)
            if style_num in style_dict:
                style_string = style_dict[style_num]
                for attr in style_string.split(','):
                    attr = attr.strip().split(':')
                    name = attr[0].strip()
                    if name == 'fore':
                        style.setColor(QtGui.QColor(attr[1]))
                    elif name == 'back':
                        style.setPaper(QtGui.QColor(attr[1]))
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
    # 'QConsoleWidget' virtual interface
    #--------------------------------------------------------------------------

    def console_init(self):
        """ Called when the console is ready to have its first messages/prompt
            displayed. All initial writing should be done in this function.
        """
        pass

    def continuation_prompt(self):
        """ The string that prefixes lines for multi-line commands.
        """
        return '> '

    def enter_pressed(self):
        """ Called when the enter key is pressed.
        """
        pass

    def up_pressed(self):
        """ Called when the up key is pressed. Returns whether to continue
            processing the event.
        """
        return True

    def down_pressed(self):
        """ Called when the down key is pressed. Returns whether to continue
            processing the event.
        """
        return True

    #--------------------------------------------------------------------------
    # Protected interface
    #--------------------------------------------------------------------------

    def _calc_line_width(self):
        """ Calculate how many characters (assuming a monospaced font) will fit
            in a line.
        """
        font_metrics = QtGui.QFontMetrics(QtGui.QFont(_FONT, _FONT_SIZE))
        char_width = float(font_metrics.width(' '))
        self._line_width = int(floor(self.viewport().width() / char_width))
                                      
    def _in_buffer(self, line, index):
        """ Returns whether the given position is inside the editing region.
        """
        return line >= self._prompt_line and index >= self._prompt_index

    def _keep_cursor_in_buffer(self):
        """ Ensures that the cursor is inside the editing region. Returns
            whether the cursor was moved.
        """
        adjusted = False
        line, index = self.getCursorPosition()

        if line < self._prompt_line:
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
# 'QPythonShellWidget' class and associated constants:
#-------------------------------------------------------------------------------

# Horrible hack to determine if the window manager is Metacity. See
# 'keyPressEvent' for more info.
if sys.platform == 'linux2':
    from subprocess import Popen, PIPE
    METACITY = 'metacity' in Popen(['grep', 'metacity'], 
                                   stdin=Popen(['ps','-A'], stdout=PIPE).stdout,
                                   stdout=PIPE).communicate()[0]
else:
    METACITY = False

class QPythonShellWidget(QConsoleWidget):
    """ An embeddable Python shell.
    """

    #--------------------------------------------------------------------------
    # 'object' interface
    #--------------------------------------------------------------------------

    def __init__(self, parent=None):
        """ Set up lexer and internal variables
        """
        self.interpreter = InteractiveInterpreter()
        self.exec_callback = None

        # Set the lexer 
        QsciScintilla.__init__(self, parent)
        lexer = QsciLexerPython(self)
        apis = QPythonShellAPIs(lexer, self.interpreter)
        self.setLexer(lexer)
        self.setAutoCompletionSource(QsciScintilla.AcsAPIs)

        # Initialize QConsoleWidget. Replace the styles previously set by
        # QsciPythonLexer with the defaults of QConsoleWidget.
        self.SendScintilla(QsciBase.SCI_STYLERESETDEFAULT)
        self.SendScintilla(QsciBase.SCI_STYLECLEARALL)
        QConsoleWidget.__init__(self, parent, _base_init=False)

        # Set up internal variables
        self._indent = 0
        self._hidden = False
        self._more = False
        self._history = []
        self._history_index = 0

    #--------------------------------------------------------------------------
    # file-like object interface
    #--------------------------------------------------------------------------

    def write(self, text, refresh=True):
        if not self._hidden:
            QConsoleWidget.write(self, text, refresh)

    #---------------------------------------------------------------------------
    # 'QWidget' interface
    #---------------------------------------------------------------------------
    
    def keyPressEvent(self, event):
        """ Reimplemented to hack around a bug in QScintilla where creating
            an autocompletion prompt causes the window to lose focus if the 
            application is running under Gnome.
        """
        if METACITY:
            was_active = self.isListActive()
            QConsoleWidget.keyPressEvent(self, event)
            if not was_active and self.isListActive():
                for child in self.children():
                    if isinstance(child, QtGui.QListWidget):
                        child.setWindowFlags(QtCore.Qt.ToolTip |
                                             QtCore.Qt.WindowStaysOnTopHint)
                        child.show()
        else:
            QConsoleWidget.keyPressEvent(self, event)

    #---------------------------------------------------------------------------
    # 'QConsoleWidget' interface
    #---------------------------------------------------------------------------

    def console_init(self):
        self.SendScintilla(QsciBase.SCI_SETLEXER, QsciBase.SCLEX_NULL)

        self.write('Python %s on %s.\n' % (sys.version, sys.platform), 
                   refresh=False)
        self.write('Type "copyright", "credits" or "license" for more ' \
                       'information.\n\n', refresh=False)
        self.new_prompt()

        self.SendScintilla(QsciBase.SCI_SETLEXER, QsciBase.SCLEX_PYTHON)
    
    def continuation_prompt(self):
        return '... '

    def enter_pressed(self):
        self.execute(self.input_buffer)

    def up_pressed(self):
        line, _ = self.getCursorPosition()
        if line <= self._prompt_line:
            if self._history_index > 0:
                self._history_index -= 1
                self.input_buffer = self._history[self._history_index]
                # Go to first line for seamless history up scrolling.
                end_line, _ = self._end_position()
                if line != end_line:
                    i = len(str(self.text(self._prompt_line)).rstrip())
                    self.setCursorPosition(self._prompt_line, i)
            return False
        return True

    def down_pressed(self):
        line, _ = self.getCursorPosition()
        end_line, _ = self._end_position()
        if line < self._prompt_line or line == end_line:
            if self._history_index < len(self._history):
                self._history_index += 1
                if self._history_index < len(self._history):
                    self.input_buffer = self._history[self._history_index]
                else:
                    self.input_buffer = ''
            return False
        return True

    #--------------------------------------------------------------------------
    # 'QPythonShellWidget' interface
    #--------------------------------------------------------------------------

    def new_prompt(self, prompt='>>> '):
        """ Convenience method because the normal prompt is always the same.
        """
        QConsoleWidget.new_prompt(self, prompt)
        
    def execute(self, source, hidden=False):
        """ Execute a Python string.
        """
        source += '\n'
        if not hidden:
            self.write('\n', refresh=False)

        # Only execute interactive multiline input if it ends with a blank line
        stripped = source.strip()
        if stripped and (not self._more or 
                         source.splitlines()[-1].strip() == ''):
            # Save the current std* and point them here
            old_stdin = sys.stdin
            old_stdout = sys.stdout
            old_stderr = sys.stderr
            sys.stdin = sys.stdout = sys.stderr = self
            
            # Do not syntax highlight output
            if not hidden:
                self.SendScintilla(QsciBase.SCI_SETLEXER, QsciBase.SCLEX_NULL)

            # Run the source code in the interpeter
            self._hidden = hidden
            try:
                self._more = self.interpreter.runsource(source)
            finally:
                self._hidden = False

                # Restore std* unless the executed changed them
                if sys.stdin is self:
                    sys.stdin = old_stdin
                if sys.stdout is self:
                    sys.stdout = old_stdout
                if sys.stderr is self:
                    sys.stderr = old_stderr

            if not self._more:
                self._indent = 0
                if self.exec_callback:
                    self.exec_callback()
                if not hidden:
                    if len(self._history) == 0 or self._history[-1] != stripped:
                        self._history.append(stripped)
                    self._history_index = len(self._history)    

        if not hidden:
            if self._more:
                self.write('... ', refresh=False)
                if stripped.endswith(':'):
                    self._indent += 1
                self.write('\t' * self._indent, refresh=False)
            else:
                self.write('\n', refresh=False)
                self.new_prompt()
            
            # Turn Python syntax highlighting back on
            self.SendScintilla(QsciBase.SCI_SETLEXER, QsciBase.SCLEX_PYTHON)

#-------------------------------------------------------------------------------
# 'QPythonShellAPIs' class:
#-------------------------------------------------------------------------------

class QPythonShellAPIs(QsciAbstractAPIs):
    """ An implementation of QsciAbstractAPIs that uses the namespace of an
        InteractiveInterpreter to look up symbols.
    """

    #--------------------------------------------------------------------------
    # 'object' interface
    #--------------------------------------------------------------------------
    
    def __init__(self, lexer, interpreter):
        """ Store the interpreter.
        """
        QsciAbstractAPIs.__init__(self, lexer)
        self.interpreter = interpreter

    #--------------------------------------------------------------------------
    # 'QsciAbstractAPIs' interface
    #--------------------------------------------------------------------------

    def callTips(self, context, commas, style, shifts):
        """ Return the call tips valid for the context. (Note that the last word
            of the context will always be empty.) 'commas' is the number of
            commas the user has typed after the context and before the cursor
            position.
        """
        symbol = self._symbol_from_context(context)
        doc = getattr(symbol, '__doc__', None)
        return [] if doc is None else [ doc ]

    def updateAutoCompletionList(self, context, auto_list):
        """ Update the auto completion list with API entries derived from
            context. context is the list of words in the text preceding the
            cursor position. The last word is a partial word and may be empty if
            the user has just entered a word separator.
        """
        symbol = self._symbol_from_context(context)
        for name in getattr(symbol, '__dict__', {}).keys():
            auto_list.append(QtCore.QString(name))

    #--------------------------------------------------------------------------
    # Protected interface
    #--------------------------------------------------------------------------

    def _symbol_from_context(self, context):
        """ Find a python object in the interpeter namespace from a QStringList
            context object (see QsciAbstractAPIs interface above).
        """
        context = map(str, context)
        base_symbol_string = context[0]
        symbol = self.interpreter.locals.get(base_symbol_string, None)
        if symbol is None:
            symbol = __builtin__.__dict__.get(base_symbol_string, None)

        for name in context[1:-1]:
            if symbol is None:
                break
            symbol = getattr(symbol, name, None)

        return symbol
        
#-------------------------------------------------------------------------------
# 'QPyfacePythonShellWidget' class:
#-------------------------------------------------------------------------------

class QPyfacePythonShellWidget(QPythonShellWidget):
    """ A QPythonShellWidget customized to support the IPythonShell interface.
    """

    #--------------------------------------------------------------------------
    # 'object' interface
    #--------------------------------------------------------------------------

    def __init__(self, pyface_widget, *args, **kw):
        """ Reimplemented to store a reference to the Pyface widget which
            contains this control.
        """
        self._pyface_widget = pyface_widget

        QPythonShellWidget.__init__(self, *args, **kw)
    
    #---------------------------------------------------------------------------
    # 'QWidget' interface
    #---------------------------------------------------------------------------

    def keyPressEvent(self, event):
        """ Reimplemented to generate Pyface key press events.
        """
        # Pyface doesn't seem to be Unicode aware.  Only keep the key code if it
        # corresponds to a single Latin1 character.
        kstr = event.text().toLatin1()
        if kstr.length() == 1:
            kcode = ord(kstr.at(0))
        else:
            kcode = 0

        mods = event.modifiers()
        self._pyface_widget.key_pressed = KeyPressedEvent(
            alt_down     = ((mods & QtCore.Qt.AltModifier) == QtCore.Qt.AltModifier),
            control_down = ((mods & QtCore.Qt.ControlModifier) == QtCore.Qt.ControlModifier),
            shift_down   = ((mods & QtCore.Qt.ShiftModifier) == QtCore.Qt.ShiftModifier),
            key_code     = kcode,
            event        = QtGui.QKeyEvent(event))

        QPythonShellWidget.keyPressEvent(self, event)
