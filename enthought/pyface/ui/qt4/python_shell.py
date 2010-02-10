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
from glob import glob
import keyword
from math import ceil, floor
import os
import re
from subprocess import Popen, PIPE
from string import whitespace
import sys
from textwrap import dedent
from time import time
import types
import traceback

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
        if hidden:
            self.control.execute_source(command, hidden=True)
        else:
            self.control.input_buffer = command
            self.control.execute()

    def execute_file(self, path, hidden=True):
        if hidden:
            self.control.execute_file(path, hidden=True)
        else:
            self.control.input_buffer = 'run %s' % path
            self.control.execute()

    #--------------------------------------------------------------------------
    # 'IWidget' interface.
    #--------------------------------------------------------------------------

    def _create_control(self, parent):
        return QPyfacePythonShellWidget(self, parent)

#-------------------------------------------------------------------------------
# 'WrappingStringIO' class:
#-------------------------------------------------------------------------------

class WrappingStringIO(object):
    """ A wrapper around cStringIO that wraps lines that exceed a specified
        width.

        This class exists because QScintilla's line wrapping performs *very*
        badly for long lines (QFontMetric.width appears to get called at least
        twice for every character). We can do this much faster than QScintilla
        because we can guarantee a monospaced font. That being said, this is
        still a performance bottleneck and it may be worth reimplementing in C.
    """

    def __init__(self, width):
        """ Create a WrappingStringIO with the specified fill width.
        """ 
        import cStringIO
        self.__cio = cStringIO.StringIO()
        self.width = width

    def __getattr__(self, name):
        """ Pretend that this is a subclass of cStringIO.
        """
        return getattr(self.__cio, name)

    def write(self, string):
        """ Wrap text as it is written to the buffer. This wrapping ignores word
            boundaries; all long lines will be broken at the fill width.
        """
        i = start = count = 0
        for i, char in enumerate(string):
            if char == '\n':
                self.__cio.write(string[start:i+1])
                start = i + 1
                count = 0
            elif char == '\t':
                count += 4
            elif char != '\r':
                count += 1
            if count >= self.width:
                self.__cio.write(string[start:i+1])
                self.__cio.write('\n')
                start = i + 1
                count = 0
        if start <= i:
            self.__cio.write(string[start:i+1])

#-------------------------------------------------------------------------------
# 'QConsoleWidget' class and associated constants:
#-------------------------------------------------------------------------------

# Note: This code was adapted from the wx ConsoleWidget in IPython, although
#       it is now quite different and certainly not interchangeable.

# New style numbers
_INPUT_STYLE = 15
_ERROR_STYLE = 16
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
    _INPUT_STYLE : '#EDFDFF', # Nice blue
    _ERROR_STYLE : '#FFF1F1', # Nice red 
    _TRACE_STYLE : '#F5F5F5', # Nice grey
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

# Determine if the window manager is Metacity (see 'keyPressEvent' for info)
if sys.platform == 'linux2':
    METACITY = 'metacity' in Popen(['ps', '-A'], stdout=PIPE).communicate()[0]
else:
    METACITY = False

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
        # Allow subclasses to call QsciScintilla's initializer separately from
        # this classe's initializer. This is useful if using a QScintilla lexer,
        # because calling setLexer will blow away all the styling information
        # set in this initializer.
        if _base_init:
            QsciScintilla.__init__(self, parent)

        # Initialize public and protected variables
        self.colorize_regions = True
        self.title = 'Console' # captured from ANSI escape sequences
        self._buffer = WrappingStringIO(80)
        self._console_inited = False
        self._enter_processing = False
        self._last_refresh_time = 0
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
        self._finished_input_mkr = self.markerDefine(QsciScintilla.Background)
        self._input_mkr = self.markerDefine(QsciScintilla.Background)
        self._error_mkr = self.markerDefine(QsciScintilla.Background)

        # Configure indentation
        self.setIndentationWidth(4)
        self.setIndentationsUseTabs(True)
        self.setTabWidth(4)

        # Do not wrap text--we will do it ourselves.
        self.setWrapMode(QsciScintilla.WrapNone)
        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)

        # Cache layout for improved performance
        self.SendScintilla(QsciBase.SCI_SETLAYOUTCACHE, QsciBase.SC_CACHE_PAGE)

        # Do not show a margin
        self.setMarginWidth(1, 0)

        # Define Scintilla text and marker styles
        self.set_styles(styles)
        self.set_marker_colors(marker_colors)
        self.set_ansi_colors(ansi_colors)

    #--------------------------------------------------------------------------
    # file-like object interface
    #-------------------------------------------------------------------------- 

    def flush(self):
        """ Flush the buffer by writing its contents to the screen.
        """
        self._buffer.seek(0)
        text = self._buffer.getvalue()
        self._buffer.close()
        self._buffer = WrappingStringIO(self._buffer.width)

        # Because the handling of ANSI sequences is not currently being used,
        # the following code has commented out and replaced. If ANSI sequences
        # are to be used, this should be reimplemented more efficiently.
        self.SendScintilla(QsciBase.SCI_STARTSTYLING, self.length())
        self.append(text)
#         title = self.title_pattern.split(text)
#         if len(title) > 1:
#             self.title = title[-2]

#         text = self.title_pattern.sub('', text)
#         segments = self.color_pattern.split(text)
#         segment = segments.pop(0)
#         self.SendScintilla(QsciBase.SCI_STARTSTYLING, self.text().length())
#         try:
#             self.append(segment)
#         except UnicodeDecodeError:
#             # FIXME: Do I really want to skip the exception?
#             pass
        
#         for ansi_tag, text in zip(segments[::2], segments[1::2]):
#             self.SendScintilla(QsciBase.SCI_STARTSTYLING, self.text().length())
#             try:
#                 self.append(text)
#             except UnicodeDecodeError:
#                 # FIXME: Do I really want to skip the exception?
#                 pass
#             if ansi_tag in self._ansi_colors:
#                 style = self._ansi_colors[ansi_tag][0] + _ANSI_STYLE_START
#             else:
#                 style = 0
#             self.SendScintilla(QsciBase.SCI_SETSTYLING, len(text), style)
                
        self.setCursorPosition(*self._end_position())

    def readline(self, prompt=None):
        """ Read and return one line of input from the user.
        """
        self._reading = True
        if prompt is None:
            self.new_prompt('')
        else:
            self.new_prompt(prompt)
        while self._reading:
            QtCore.QCoreApplication.processEvents()

        result = self.input_buffer + '\n'
        self.write('\n')
        return result

    def write(self, text, refresh=True):
        """ Write text to the buffer, possibly flushing it if 'refresh' is set.
        """
        # WARNING: Do not put print statements to sys.stdout/sys.stderr in this
        # method, as print will call this method, creating an infinite loop.

        self._buffer.write(text)
        
        if refresh:
            current_time = time()
            if current_time - self._last_refresh_time > 0.05:
                self.flush()
                self.repaint()
                self._last_refresh_time = current_time 

    def writelines(self, lines, refresh=True):
        """ Write a list of lines to the buffer.
        """
        for line in lines:
            self.write(line, refresh=refresh)

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
        alt_down = event.modifiers() & QtCore.Qt.AltModifier
        shift_down = event.modifiers() & QtCore.Qt.ShiftModifier

        if ctrl_down:
            if key in self._ctrl_down_remap:
                ctrl_down = False
                key = self._ctrl_down_remap[key]
                event = QtGui.QKeyEvent(QtCore.QEvent.KeyPress, key, 
                                        QtCore.Qt.NoModifier)

            elif key == QtCore.Qt.Key_L:
                # FIXME: The current prompt line should become the top line of
                # the console.
                intercepted = True

            elif key == QtCore.Qt.Key_K:
                if self._in_buffer(line, index):
                    end_index = len(self.continuation_prompt())
                    self.setSelection(line, index, line + 1, end_index)
                    self.removeSelectedText()
                else:
                    # Won't be called because ctrl is down
                    self._keep_cursor_in_buffer()
                intercepted = True

            elif key == QtCore.Qt.Key_T:
                # Transposing lines is not appropriate for a console.
                # FIXME: Transpose characters instead.
                intercepted = True

            elif key == QtCore.Qt.Key_Y:
                self.paste()
                intercepted = True

            elif key == QtCore.Qt.Key_Underscore:
                self.undo()
                intercepted = True

        elif alt_down:
            if key == QtCore.Qt.Key_B:
                self.setCursorPosition(*self._get_word_start(line, index))
                intercepted = True
                
            elif key == QtCore.Qt.Key_F:
                self.setCursorPosition(*self._get_word_end(line, index))
                intercepted = True

            elif key == QtCore.Qt.Key_Backspace:
                start_line, start_index = self._get_word_start(line, index)
                self.setSelection(start_line, start_index, line, index)
                self.removeSelectedText()
                intercepted = True

            elif key == QtCore.Qt.Key_D:
                end_line, end_index = self._get_word_end(line, index)
                self.setSelection(line, index, end_line, end_index + 1)
                self.removeSelectedText()
                intercepted = True

        list_active = self.isListActive()
        if not list_active:
            if key in (QtCore.Qt.Key_Return, QtCore.Qt.Key_Enter):
                if self._reading:
                    self._reading = False
                elif not self._enter_processing:
                    self._enter_processing = True
                    try:
                        self.execute(interactive=True)
                    finally:
                        self._enter_processing = False
                intercepted = True

            elif key == QtCore.Qt.Key_Up:
                intercepted = self._reading or not self._up_pressed()

            elif key == QtCore.Qt.Key_Down:
                intercepted = self._reading or not self._down_pressed()

            elif key == QtCore.Qt.Key_Tab:
                if self._reading:
                    intercepted = False
                else:
                    intercepted = not self._tab_pressed()

            elif key == QtCore.Qt.Key_Left:
                intercepted = not self._in_buffer(line, index - 1)

            elif key == QtCore.Qt.Key_Home:
                if shift_down and self._in_buffer(line, index):
                    self.setSelection(line, index, line, self._prompt_index)
                else:
                    self.setCursorPosition(line, self._prompt_index)
                intercepted = True

            elif key == QtCore.Qt.Key_Backspace and not alt_down:

                # Handle case where a line needs to be removed
                len_prompt = len(self.continuation_prompt())
                if line != self._prompt_line and index == len_prompt:
                    self.setSelection(
                        line-1, self.text(line-1).length()-1, line, index)
                    self.removeSelectedText()
                    intercepted = True

                # Regular backwards deletion
                else:
                    sel_line, sel_index, _, _ = self.getSelection()
                    if sel_line == -1:
                        intercepted = not self._in_buffer(line, index - 1)
                    else:
                        intercepted = not self._in_buffer(sel_line, sel_index)

            elif key == QtCore.Qt.Key_Delete:
                sel_line, sel_index, _, _ = self.getSelection()
                if sel_line == -1:
                    intercepted = not self._in_buffer(line, index)
                else:
                    intercepted = not self._in_buffer(sel_line, sel_index)

            if not ctrl_down:
                self._keep_cursor_in_buffer()

        if intercepted:
            if key != QtCore.Qt.Key_Tab:
                # Cancel any call tips or autocompletion lists which are active
                self.callTip() 
                self.cancelList()
        else:
            QsciScintilla.keyPressEvent(self, event)

        # Hack around a bug in QScintilla where creating an autocompletion
        # prompt causes the window to lose focus if the application is running
        # under Gnome.
        if METACITY and not list_active and self.isListActive():
            for child in self.children():
                if isinstance(child, QtGui.QListWidget):
                    child.setWindowFlags(QtCore.Qt.ToolTip |
                                         QtCore.Qt.WindowStaysOnTopHint)
                    child.show()

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
            self._console_init()
            self._console_inited = True
        QsciScintilla.showEvent(self, event)

    #--------------------------------------------------------------------------
    # 'QScintilla' interface
    #--------------------------------------------------------------------------

    def paste(self):
        """ Reimplemented to ensure that text is pasted in the editing region.
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

        # Reset the input buffer region background, if necessary
        if self.colorize_regions:
            self.markerDeleteAll(self._input_mkr)
            for i in xrange(self._prompt_line, self.lines()):
                self.markerAdd(i, self._input_mkr)

    def _get_input_buffer(self):
        lines = [ str(self.text(self._prompt_line))[self._prompt_index:] ]
        cont_prompt_index = len(self.continuation_prompt())
        for i in xrange(self._prompt_line + 1, self.lines()):
            lines.append(str(self.text(i))[cont_prompt_index:])
        return ''.join(lines)

    # The buffer being edited:
    input_buffer = property(_get_input_buffer, _set_input_buffer)

    def new_prompt(self, prompt):
        """ Prints a new prompt at the end of the buffer.
        """
        self.flush()
        self.append('\n')
        self.write(prompt, refresh=False)
        self.flush()

        self._prompt = prompt
        self._prompt_line, self._prompt_index = self._end_position()

        if self.colorize_regions and not self._reading:
            self.markerDeleteAll(self._input_mkr)
            self.markerAdd(self._prompt_line, self._input_mkr)
        self.ensureCursorVisible()

    def execute(self, interactive=False):
        """ Execute the text in the input buffer. Returns whether the input
            buffer was completely processed and a new prompt created.
        """
        self.append('\n')
        current, end = self._prompt_line, self.lines() - 1
        done = self._execute(interactive=interactive)

        if self.colorize_regions:
            if done:
                for i in xrange(current, end):
                    self.markerAdd(i, self._finished_input_mkr)
            else:
                self.markerAdd(end, self._input_mkr)

        return done

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
                                      self._finished_input_mkr)
        self.setMarkerBackgroundColor(QtGui.QColor(colors[_INPUT_STYLE]),
                                      self._input_mkr)
        self.setMarkerBackgroundColor(QtGui.QColor(colors[_ERROR_STYLE]),
                                      self._error_mkr)

    #--------------------------------------------------------------------------
    # 'QConsoleWidget' virtual interface
    #--------------------------------------------------------------------------

    def _console_init(self):
        """ Called when the console is ready to have its first messages/prompt
            displayed. All initial writing should be done in this function.
        """
        raise NotImplementedError

    def continuation_prompt(self):
        """ The string that prefixes lines for multi-line commands.
        """
        return '> '

    def _execute(self, interactive):
        """ Called to execute the input buffer. When triggered by an the enter
            key press, 'interactive' is True; otherwise, it is False. Returns
            whether the input buffer was completely processed and a new prompt
            created.
        """
        raise NotImplementedError

    def _up_pressed(self):
        """ Called when the up key is pressed. Returns whether to continue
            processing the event.
        """
        return True

    def _down_pressed(self):
        """ Called when the down key is pressed. Returns whether to continue
            processing the event.
        """
        return True

    def _tab_pressed(self):
        """ Called when the tab key is pressed. Returns whether to continue
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
        self._buffer.width = int(floor(self.viewport().width() / char_width))        

    def _get_word_start(self, line, index):
        """ Find the start of the word to the left the given position. If a
            sequence of non-word characters precedes the first word, skip over
            them. (This emulates the behavior of bash, emacs, etc.)
        """
        if index == self._prompt_index:
            # Don't let Scintilla get confused by a continuation promot
            line -= 1
            index = self.text(line).length() - 1

        pos = self.positionFromLineIndex(line, index)
        start = self.SendScintilla(QsciBase.SCI_WORDSTARTPOSITION, pos, False)
        if not self.isWordCharacter(chr(self.SendScintilla(
                    QsciBase.SCI_GETCHARAT, start))):
            start = self.SendScintilla(QsciBase.SCI_WORDSTARTPOSITION, 
                                       start - 1, True)
        start_line, start_index = self.lineIndexFromPosition(start)

        if start_line < self._prompt_line:
            start_line, start_index = self._prompt_line, self._prompt_index
        elif start_index < self._prompt_index:
            start_index = self._prompt_index
        return start_line, start_index

    def _get_word_end(self, line, index):
        """ Find the end of the word to the right the given position. If a
            sequence of non-word characters precedes the first word, skip over
            them. (This emulates the behavior of bash, emacs, etc.)
        """
        pos = self.positionFromLineIndex(line, index)
        end = self.SendScintilla(QsciBase.SCI_WORDENDPOSITION, pos, False)
        if not self.isWordCharacter(chr(self.SendScintilla(
                    QsciBase.SCI_GETCHARAT, end - 1))):
            end = self.SendScintilla(QsciBase.SCI_WORDENDPOSITION, 
                                       end, False)
        return self.lineIndexFromPosition(end)
                                      
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
# 'QPythonShellWidget' class:
#-------------------------------------------------------------------------------

class QPythonShellWidget(QConsoleWidget):
    """ An embeddable Python shell.
    """

    shell_help_msg = """\
The Enthought Python Shell provides an interactive python shell, extended
with the following commands (brackets around an argument means it is optional):
?
    Print this message.
cd [path]
    Change directory to the given path.  If the path is not given, change to
    your home directory.
ls [path]
    List the files in directory path.  If the path is not given, list the files
    in the current directory.
pwd
    Print the current directory.
reset
    Remove all names from the python shell's namespace.  This will clear all
    variables, functions, imported names, etc.
run filename
    Run the python script in filename.
who
    List all the names in the python shell's namespace.
    
The shell also provides a shortcut for printing the docstring associated with
a name: enter the name followed by or preceded by a question mark.  For
example:
    >>> str?
    str(object) -> string

    Return a nice string representation of the object.
    If the argument is a string, the return value is the same object.

    >>> 
"""

    #--------------------------------------------------------------------------
    # 'object' interface
    #--------------------------------------------------------------------------

    def __init__(self, parent=None):
        """ Set up lexer and internal variables
        """
        self.locals = dict(__name__="__console__", __doc__=None)
        self.interpreter = InteractiveInterpreter(self.locals)
        self.exec_callback = None
        self._hidden = False
        self._history = []
        self._history_index = 0

        # Set the lexer and its autocompletion API
        QsciScintilla.__init__(self, parent)
        lexer = QsciLexerPython(self)
        apis = QsciPythonAPIs(lexer, self.interpreter)
        self.setLexer(lexer)

        # If there is only a single autocompletion entry, just use it. Only
        # relevant when autocompletion explicity requested (eg Tab completion)
        self.setAutoCompletionShowSingle(True)

        # Uncomment for autocompletion to occur when the user types a '.' char.
        # (Autocompletion is configured to occur on Tab key press regardless.)
        #self.setAutoCompletionSource(QsciScintilla.AcsAPIs)

        # Initialize QConsoleWidget. Replace the styles previously set by
        # QsciPythonLexer with the defaults of QConsoleWidget.
        self.SendScintilla(QsciBase.SCI_STYLERESETDEFAULT)
        self.SendScintilla(QsciBase.SCI_STYLECLEARALL)
        QConsoleWidget.__init__(self, parent, _base_init=False)

    #--------------------------------------------------------------------------
    # file-like object interface
    #--------------------------------------------------------------------------

    def write(self, text, refresh=True):
        if not self._hidden:
            QConsoleWidget.write(self, text, refresh)

    #---------------------------------------------------------------------------
    # 'QConsoleWidget' interface
    #---------------------------------------------------------------------------

    def _console_init(self):
        self.SendScintilla(QsciBase.SCI_SETLEXER, QsciBase.SCLEX_NULL)

        self.write('Python %s on %s.\n' % (sys.version, sys.platform), 
                   refresh=False)
        self.write('Type "copyright", "credits" or "license" for more ' \
                       'information.\n', refresh=False)
        self.write('''Type "?" to see this shell's enhancements.\n''', refresh=False)
        self.new_prompt()

        self.SendScintilla(QsciBase.SCI_SETLEXER, QsciBase.SCLEX_PYTHON)
    
    def continuation_prompt(self):
        return '... '

    def _execute(self, interactive=False):
        return self.execute_string(self.input_buffer, interactive=interactive)

    def _up_pressed(self):
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

    def _down_pressed(self):
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

    def _tab_pressed(self):
        line, index = self.getCursorPosition()

        # Case 1: a 'magic' command that operates on files needs completion
        text = self.input_buffer
        magic = self._is_magic(text, 'ls', 'cd', 'run')
        if magic and len(text) > len(magic):

            # Get the components of the path that is currently entered
            start_index = self._prompt_index + len(magic) + 1
            line, end_index = self.getCursorPosition()
            path = str(self.text(line))[start_index:end_index]
            context = re.split(r'[\\/]', path)
            
            # Decide which file extensions to match
            extensions = [ '/' ]
            if magic == 'run':
                extensions.append('.py')

            # Build the list of files and directories
            auto_list = []
            for match in self._path_matches(path, extensions):
                display_match = os.path.basename(match)
                if not display_match:
                    display_match = os.path.basename(os.path.dirname(match))+'/'
                auto_list.append(display_match)
            if not len(auto_list):
                return False

            # Have the underlying Scintilla widget start autocompletion. The
            # choice of separator symbol is significant. When autocompletion is
            # peformed via QScintilla's higher-level API, the ETX character is
            # used. QScintilla defines a non-overridable special behavior for
            # this character (stopping the autocompletion on spaces), so we use
            # EOT instead.
            self.SendScintilla(QsciBase.SCI_AUTOCSETCHOOSESINGLE, True);
            self.SendScintilla(QsciBase.SCI_AUTOCSETSEPARATOR, 4);
            last_len = len(context[-1])
            packed_list = chr(4).join(auto_list)
            self.SendScintilla(QsciBase.SCI_AUTOCSHOW, last_len, packed_list)
            return False

        # Case 2: autocompletion on a Python symbol
        elif chr(self.SendScintilla(
                QsciBase.SCI_GETCHARAT,
                self.positionFromLineIndex(line, index - 1))) not in whitespace:
            self.autoCompleteFromAPIs()
            return False

        # Case 3: allow a '\t' to be inserted
        return True

    #--------------------------------------------------------------------------
    # 'QPythonShellWidget' interface
    #--------------------------------------------------------------------------

    def new_prompt(self, prompt='>>> '):
        """ Convenience method because the normal prompt is always the same.
        """
        QConsoleWidget.new_prompt(self, prompt)
        
    def execute_string(self, source, hidden=False, interactive=False):
        """ Execute a Python string. If 'hidden', no output is shown. Returns
            whether the source executed (ie returns True only if no more input
            is needed).
        """
        # Only execute interactive multiline input if it ends with a blank line
        if interactive:
            lines = source.splitlines()
            if len(lines) == 1:
                more = False
            else:
                more = not lines[-1].strip() == ''
        else:
            source += '\n'
            more = False

        # Do not syntax highlight output
        if not hidden:
            self.SendScintilla(QsciBase.SCI_SETLEXER, QsciBase.SCLEX_NULL)

        # Process 'magic' commands
        stripped = source.strip()
        if self._is_magic(stripped, 'cd'):
            if len(stripped) == 2:
                path = '~'
            else:
                path = self._parse_path(stripped[2:])
            try:
                os.chdir(os.path.expanduser(path))
            except OSError:
                self.write(str(sys.exc_info()[1]) + '\n', refresh=False)
            self.write(os.path.abspath(os.getcwd()) + '\n', refresh=False)

        elif self._is_magic(stripped, 'pwd'):
            self.write(os.path.abspath(os.getcwd()) + '\n', refresh=False)

        elif self._is_magic(stripped, 'ls'):
            if len(stripped) == 2:
                path = os.getcwd()
            else:
                path = os.path.expanduser(self._parse_path(stripped[2:]))
            # FIXME: Check for availability of 'ls' on Windows in __init__
            if sys.platform == 'win32':
                args = [ 'dir', path.rstrip('/') ]
                out, err = self._subprocess_out_err(args, shell=True)
            elif sys.platform == 'darwin':
                # FIXME: Figure out how to get the file names to align like they
                # do when ls is run in a terminal.
                args = ['ls', '-CF', path]
                out, err = self._subprocess_out_err(args,
                                    env=dict(COLUMNS=str(self._buffer.width)))
            else:
                # Use columns, a tab width of 4, and our computed line width
                args = ['ls', '-CF', '-T 4', '-w %i' % self._buffer.width, path]
                out, err = self._subprocess_out_err(args)
            self.write(out, refresh=False)
            self.write(err, refresh=False)

        elif self._is_magic(stripped, 'run'):
            if len(stripped) == 3:
                self.write('A filename must be provided!\n', refresh=False)
            else:
                path = os.path.expanduser(self._parse_path(stripped[4:]))
                if not os.path.isfile(path) and not path.endswith('.py'):
                    path += '.py'
                if os.path.exists(path):
                    self.execute_file(path, hidden)
                else:
                    self.write('File `%s` not found.\n' % path, refresh=False)

        elif self._is_magic(stripped, 'who'):
            # The 'who' command prints the names in the namespace.
            spacing = 8
            skip = ['__builtins__', '__name__', '__doc__']
            names = [n for n in sorted(self.locals.keys()) if n not in skip]
            if names:
                out = names[0]
                names = names[1:]
                for name in names:
                    nspaces = spacing - (len(out) % spacing)
                    if len(out+name) + nspaces >= self._buffer.width:
                        self.write(out + '\n', refresh=False)
                        out = name
                    else:
                        out = out + ' '*nspaces + name
                if out:
                    self.write(out + '\n', refresh=False)

        elif self._is_magic(stripped, 'reset'):
            # Reset the namespace.
            answer = self.readline(prompt='Once deleted, variables cannot be recovered. Proceed (y/[n])? ')
            answer = answer.strip().lower()
            if answer == 'y' or answer == 'yes':
                self.locals.clear()
                self.locals['__name__'] = '__console__'
                self.locals['__doc__'] = None

        # Process special '?' help syntax
        elif not more and (stripped.startswith('?') or stripped.endswith('?')):
            line = self._prompt_line
            index = self.text(line).length() - 1 # before newline
            if stripped.endswith('?'):
                index -= 1
            if stripped == "?":
                # The user entered a single question mark.
                self.write(self.shell_help_msg, refresh=False)
            else:                
                name, obj = self.lexer().apis().get_symbol(line, index)
                if obj is None:
                    self.write('Object `%s` not found.\n' % name, refresh=False)
                elif obj.__doc__ is None:
                    self.write("'%s' has no docstring.\n" % name, refresh=False)
                else:
                    self.write(obj.__doc__.rstrip() + '\n', refresh=False)

        # Process a regular python command
        elif stripped and not more:
            # Save the current std* and point them here
            old_stdin = sys.stdin
            old_stdout = sys.stdout
            old_stderr = sys.stderr
            sys.stdin = sys.stdout = sys.stderr = self
            
            # Run the source code in the interpeter
            self._hidden = hidden
            try:
                more = self.interpreter.runsource(source)
            finally:
                self._hidden = False
                # Restore std* unless the executed changed them
                if sys.stdin is self:
                    sys.stdin = old_stdin
                if sys.stdout is self:
                    sys.stdout = old_stdout
                if sys.stderr is self:
                    sys.stderr = old_stderr

        if stripped and not more:
            if self.exec_callback:
                self.exec_callback()
            if not hidden:
                if len(self._history) == 0 or self._history[-1] != stripped:
                    self._history.append(stripped)
                self._history_index = len(self._history)

        if not hidden:
            if more:
                self.write(self.continuation_prompt(), refresh=False)
                space = 0
                for c in source.splitlines()[-1]:
                    if c == '\t':
                        space += 4
                    elif c == ' ':
                        space += 1
                    else:
                        break
                indent = space / 4
                if stripped.endswith(':'):
                    indent += 1
                self.write('\t' * indent, refresh=False)
                self.flush()
            else:
                self.new_prompt()

            # Turn Python syntax highlighting back on
            self.SendScintilla(QsciBase.SCI_SETLEXER, QsciBase.SCLEX_PYTHON)

        return not more

    def execute_file(self, path, hidden=False):
        """ Execute a file in the interpeter. If 'hidden', no output is shown.
        """
        # Note: The code in this function is largely ripped from IPython's
        #       Magic.py, FakeModule.py, and iplib.py.

        filename = os.path.basename(path)

        # Run in a fresh, empty namespace
        main_mod = types.ModuleType('__main__')
        prog_ns = main_mod.__dict__
        prog_ns['__file__'] = filename
        prog_ns['__nonzero__'] = lambda: True

        # Make sure that the running script gets a proper sys.argv as if it
        # were run from a system shell.
        save_argv = sys.argv
        sys.argv = [ filename ]

        # Make sure that the running script thinks it is the main module
        save_main = sys.modules['__main__']
        sys.modules['__main__'] = main_mod

        # Redirect sys.std* to control
        old_stdin = sys.stdin
        old_stdout = sys.stdout
        old_stderr = sys.stderr
        sys.stdin = sys.stdout = sys.stderr = self

        # Execute the file
        self._hidden = hidden
        try:
            if sys.platform == 'win32' and sys.version_info < (2,5,1):
                # Work around a bug in Python for Windows. For details, see:
                # http://projects.scipy.org/ipython/ipython/ticket/123
                exec file(path) in prog_ns, prog_ns
            else:
                execfile(path, prog_ns, prog_ns)
        except (KeyboardInterrupt, Exception), exc:
            self.write(traceback.format_exc())
        finally:
            # Ensure key global stuctures are restored
            sys.argv = save_argv
            sys.modules['__main__'] = save_main
            sys.stdin = old_stdin
            sys.stdout = old_stderr
            sys.stderr = old_stdout
            self._hidden = False

        # Update the interpreter with the new namespace
        del prog_ns['__name__']
        del prog_ns['__file__']
        del prog_ns['__nonzero__']
        self.interpreter.locals.update(prog_ns)

    #--------------------------------------------------------------------------
    # Protected interface
    #--------------------------------------------------------------------------

    def _is_magic(self, string, *magics):
        """ Returns whether a given command string matches a magic command.
        """
        for magic in magics:
            if (string.startswith(magic) and 
                (len(string) == len(magic) or string[len(magic)] == ' ')):
                return magic
        return False

    def _parse_path(self, string):
        """ Given a path string as specified by a user for a magic command,
            return a cleaned-up path.
        """
        # Remove trailing and leading quotes and whitespace
        string = string.strip('"\' ')

        # Convert all non-space-escaping backslashes to slashes (eg C:\blah)
        string = re.sub(r'\\(?! )', '/', string)
    
        return string

    def _path_matches(self, string, extensions=['']):
        """ Returns a list of matching file/directory names.
        """
        result = []
        for extension in extensions:
            pattern = string + '*' + extension
            matches = glob(pattern)
            result.extend(matches)
        result.sort(key=str.lower)
        return result

    def _subprocess_out_err(self, cmd, **kw):
        """ Given a command suitable for use with subprocess.Popen, execute
            the command and returns its output and error streams as strings.
        """
        proc = Popen(cmd, stdout=PIPE, stderr=PIPE, **kw)
        return proc.communicate()

#-------------------------------------------------------------------------------
# 'QsciPythonAPIs' class:
#-------------------------------------------------------------------------------

class QsciPythonAPIs(QsciAbstractAPIs):
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
    # 'QsciPythonAPIs' interface
    #--------------------------------------------------------------------------

    def get_symbol(self, line, index):
        """ Given a position defined by 'line' and 'index', use the lexer to 
            determine what the symbol is to the left of the position. Returns
            the symbol name (eg 'foo.bar') and the symbol object. 
        """
        editor = self.lexer().editor()
        position = editor.positionFromLineIndex(line, index)
        context, context_start, last_word_start = editor.apiContext(position)
        symbol, leftover = self._symbol_from_context(context)
        if len(leftover):
            symbol = None
        return '.'.join(map(str, context)), symbol

    #--------------------------------------------------------------------------
    # 'QsciAbstractAPIs' interface
    #--------------------------------------------------------------------------

    def callTips(self, context, commas, style, shifts):
        """ Return the call tips valid for the context. (Note that the last word
            of the context will always be empty.) 'commas' is the number of
            commas the user has typed after the context and before the cursor
            position.
        """
        symbol, leftover = self._symbol_from_context(context)
        doc = getattr(symbol, '__doc__', None)
        if doc is not None and len(leftover) == 1 and leftover[0] == '':
            doc = dedent(doc.rstrip()).lstrip()
            match = re.match("(?:[^\n]*\n){20}", doc)
            if match:
                doc = doc[:match.end()] + '\n[Documentation continues...]'
            return [ doc ]
        return []

    def updateAutoCompletionList(self, context, auto_list):
        """ Update the auto completion list with API entries derived from
            context. context is the list of words in the text preceding the
            cursor position. The last word is a partial word and may be empty if
            the user has just entered a word separator.
        """
        symbol, leftover = self._symbol_from_context(context)
        if len(leftover) == 1:
            leftover = leftover[0]
            if symbol is None:
                names = self.interpreter.locals.keys()
                names += __builtin__.__dict__.keys()
            else:
                names = dir(symbol)
            for name in names:
                if name.startswith(leftover):
                    auto_list.append(QtCore.QString(name))

    #--------------------------------------------------------------------------
    # Protected interface
    #--------------------------------------------------------------------------

    def _symbol_from_context(self, context):
        """ Find a python object in the interpeter namespace from a QStringList
            context object (see QsciAbstractAPIs interface above).
        """
        context = map(str, context)
        if len(context) == 0:
            return None, context

        base_symbol_string = context[0]
        symbol = self.interpreter.locals.get(base_symbol_string, None)
        if symbol is None:
            symbol = __builtin__.__dict__.get(base_symbol_string, None)
        if symbol is None:
            return None, context

        context = context[1:]
        for i, name in enumerate(context):
            new_symbol = getattr(symbol, name, None)
            if new_symbol is None:
                return symbol, context[i:]
            else:
                symbol = new_symbol

        return symbol, []

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
