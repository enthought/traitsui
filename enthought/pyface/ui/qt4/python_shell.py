#------------------------------------------------------------------------------
# Copyright (c) 2011, Enthought, Inc.
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in enthought/LICENSE.txt and may be redistributed only
# under the conditions described in the aforementioned license.  The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
# Thanks for using Enthought open source!
#
# Author: Evan Patterson
#------------------------------------------------------------------------------

# Standard library imports.
import __builtin__
from code import compile_command, InteractiveInterpreter
from cStringIO import StringIO
import sys
from time import time

# System package imports.
from enthought.qt import QtCore, QtGui
from pygments.lexers import PythonLexer

# Enthought library imports.
from enthought.traits.api import Event, implements

# Local imports.
from code_editor.pygments_highlighter import PygmentsHighlighter
from console.api import BracketMatcher, CallTipWidget, CompletionLexer, \
    HistoryConsoleWidget
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
        super(PythonShell, self).__init__(**traits)

        # Create the toolkit-specific control that represents the widget.
        self.control = self._create_control(parent)

        # Set up to be notified whenever a Python statement is executed:
        self.control.executed.connect(self._on_command_executed)

    #--------------------------------------------------------------------------
    # 'IPythonShell' interface
    #--------------------------------------------------------------------------

    def interpreter(self):
        return self.control.interpreter

    def execute_command(self, command, hidden=True):
        self.control.execute(command, hidden=hidden)

    def execute_file(self, path, hidden=True):
        self.control.execute_file(path, hidden=hidden)

    #--------------------------------------------------------------------------
    # 'IWidget' interface.
    #--------------------------------------------------------------------------

    def _create_control(self, parent):
        return PyfacePythonWidget(self, parent)

#-------------------------------------------------------------------------------
# 'PythonWidget' class:
#-------------------------------------------------------------------------------

class PythonWidget(HistoryConsoleWidget):
    """ A basic in-process Python interpreter.
    """
    
    # Emitted when a command has been executed in the interpeter.
    executed = QtCore.Signal()
    
    #--------------------------------------------------------------------------
    # 'object' interface
    #--------------------------------------------------------------------------

    def __init__(self, parent=None):
        super(PythonWidget, self).__init__(parent)

        # PythonWidget attributes.
        self.locals = dict(__name__='__console__', __doc__=None)
        self.interpreter = InteractiveInterpreter(self.locals)

        # PythonWidget protected attributes.
        self._buffer = StringIO()
        self._bracket_matcher = BracketMatcher(self._control)
        self._call_tip_widget = CallTipWidget(self._control)
        self._completion_lexer = CompletionLexer(PythonLexer())
        self._highlighter = PythonWidgetHighlighter(self)
        self._last_refresh_time = 0

        # Configure the ConsoleWidget.
        self.tab_width = 4
        self._set_continuation_prompt('... ')

        # Configure the CallTipWidget.
        self._call_tip_widget.setFont(self.font)
        self.font_changed.connect(self._call_tip_widget.setFont)

        # Connect signal handlers.
        document = self._control.document()
        document.contentsChange.connect(self._document_contents_change)

        # Display the banner and initial prompt.
        self.reset()

    #--------------------------------------------------------------------------
    # file-like object interface
    #--------------------------------------------------------------------------

    def flush(self):
        """ Flush the buffer by writing its contents to the screen.
        """
        self._buffer.seek(0)
        text = self._buffer.getvalue()
        self._buffer.close()
        self._buffer = StringIO()

        self._append_plain_text(text)
        self._control.moveCursor(QtGui.QTextCursor.End)

    def readline(self, prompt=None):
        """ Read and return one line of input from the user.
        """
        return self._readline(prompt)

    def write(self, text, refresh=True):
        """ Write text to the buffer, possibly flushing it if 'refresh' is set.
        """
        if not self._hidden:
            self._buffer.write(text)
            if refresh:
                current_time = time()
                if current_time - self._last_refresh_time > 0.05:
                    self.flush()
                    self._last_refresh_time = current_time

    def writelines(self, lines, refresh=True):
        """ Write a list of lines to the buffer.
        """
        for line in lines:
            self.write(line, refresh=refresh)

    #---------------------------------------------------------------------------
    # 'ConsoleWidget' abstract interface
    #---------------------------------------------------------------------------

    def _is_complete(self, source, interactive):
        """ Returns whether 'source' can be completely processed and a new
            prompt created. When triggered by an Enter/Return key press,
            'interactive' is True; otherwise, it is False.
        """
        if interactive:
            lines = source.splitlines()
            if len(lines) == 1:
                try:
                    return compile_command(source) is not None
                except:
                    # We'll let the interpeter handle the error.
                    return True
            else:
                return lines[-1].strip() == ''
        else:
            return True

    def _execute(self, source, hidden):
        """ Execute 'source'. If 'hidden', do not show any output.

        See parent class :meth:`execute` docstring for full details.
        """
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

            self.executed.emit()
            self._show_interpreter_prompt()

    def _prompt_started_hook(self):
        """ Called immediately after a new prompt is displayed.
        """
        if not self._reading:
            self._highlighter.highlighting_on = True

    def _prompt_finished_hook(self):
        """ Called immediately after a prompt is finished, i.e. when some input
            will be processed and a new prompt displayed.
        """
        if not self._reading:
            self._highlighter.highlighting_on = False

    def _tab_pressed(self):
        """ Called when the tab key is pressed. Returns whether to continue
            processing the event.
        """
        # Perform tab completion if:
        # 1) The cursor is in the input buffer.
        # 2) There is a non-whitespace character before the cursor.
        text = self._get_input_buffer_cursor_line()
        if text is None:
            return False
        complete = bool(text[:self._get_input_buffer_cursor_column()].strip())
        if complete:
            self._complete()
        return not complete

    #---------------------------------------------------------------------------
    # 'ConsoleWidget' protected interface
    #---------------------------------------------------------------------------

    def _event_filter_console_keypress(self, event):
        """ Reimplemented for smart backspace.
        """
        if event.key() == QtCore.Qt.Key_Backspace and \
                not event.modifiers() & QtCore.Qt.AltModifier:
            # Smart backspace: remove four characters in one backspace if:
            # 1) everything left of the cursor is whitespace
            # 2) the four characters immediately left of the cursor are spaces
            col = self._get_input_buffer_cursor_column()
            cursor = self._control.textCursor()
            if col > 3 and not cursor.hasSelection():
                text = self._get_input_buffer_cursor_line()[:col]
                if text.endswith('    ') and not text.strip():
                    cursor.movePosition(QtGui.QTextCursor.Left,
                                        QtGui.QTextCursor.KeepAnchor, 4)
                    cursor.removeSelectedText()
                    return True

        return super(PythonWidget, self)._event_filter_console_keypress(event)

    def _insert_continuation_prompt(self, cursor):
        """ Reimplemented for auto-indentation.
        """
        super(PythonWidget, self)._insert_continuation_prompt(cursor)
        source = self.input_buffer
        space = 0
        for c in source.splitlines()[-1]:
            if c == '\t':
                space += 4
            elif c == ' ':
                space += 1
            else:
                break
        if source.rstrip().endswith(':'):
            space += 4
        cursor.insertText(' ' * space)

    #---------------------------------------------------------------------------
    # 'PythonWidget' public interface
    #---------------------------------------------------------------------------

    def execute_file(self, path, hidden=False):
        """ Attempts to execute file with 'path'. If 'hidden', no output is
            shown.
        """
        self.execute('execfile("%s")' % path, hidden=hidden)

    def reset(self):
        """ Resets the widget to its initial state. Similar to ``clear``, but
            also re-writes the banner.
        """ 
        self._reading = False
        self._highlighter.highlighting_on = False

        self._control.clear()
        self._append_plain_text(self._get_banner())
        self._show_interpreter_prompt()

    #---------------------------------------------------------------------------
    # 'PythonWidget' protected interface
    #---------------------------------------------------------------------------

    def _call_tip(self):
        """ Shows a call tip, if appropriate, at the current cursor location.
        """
        # Decide if it makes sense to show a call tip
        cursor = self._get_cursor()
        cursor.movePosition(QtGui.QTextCursor.Left)
        if cursor.document().characterAt(cursor.position()) != '(':
            return False
        context = self._get_context(cursor)
        if not context:
            return False

        # Look up the context and show a tip for it
        symbol, leftover = self._get_symbol_from_context(context)
        doc = getattr(symbol, '__doc__', None)
        if doc is not None and not leftover:
            self._call_tip_widget.show_call_info(doc=doc)
            return True
        return False

    def _complete(self):
        """ Performs completion at the current cursor location.
        """
        context = self._get_context()
        if context:
            symbol, leftover = self._get_symbol_from_context(context)
            if len(leftover) == 1:
                leftover = leftover[0]
                if symbol is None:
                    names = self.interpreter.locals.keys()
                    names += __builtin__.__dict__.keys()
                else:
                    names = dir(symbol)
                completions = [ n for n in names if n.startswith(leftover) ]
                if completions:
                    text = '.'.join(context)
                    cursor = self._get_cursor()
                    cursor.movePosition(QtGui.QTextCursor.Left, n=len(text))
                    self._complete_with_items(cursor, completions)
    
    def _get_banner(self):
        """ Gets a banner to display at the beginning of a session.
        """
        banner = 'Python %s on %s\nType "help", "copyright", "credits" or ' \
            '"license" for more information.'
        return banner % (sys.version, sys.platform)

    def _get_context(self, cursor=None):
        """ Gets the context for the specified cursor (or the current cursor
            if none is specified).
        """
        if cursor is None:
            cursor = self._get_cursor()
        cursor.movePosition(QtGui.QTextCursor.StartOfBlock, 
                            QtGui.QTextCursor.KeepAnchor)
        text = cursor.selection().toPlainText()
        return self._completion_lexer.get_context(text)

    def _get_symbol_from_context(self, context):
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

    def _show_interpreter_prompt(self):
        """ Shows a prompt for the interpreter.
        """
        self.flush()
        self._show_prompt('>>> ')

    #------ Signal handlers ----------------------------------------------------

    def _document_contents_change(self, position, removed, added):
        """ Called whenever the document's content changes. Display a call tip
            if appropriate.
        """
        # Calculate where the cursor should be *after* the change:
        position += added

        document = self._control.document()
        if position == self._get_cursor().position():
            self._call_tip()

#-------------------------------------------------------------------------------
# 'PythonWidgetHighlighter' class:
#-------------------------------------------------------------------------------

class PythonWidgetHighlighter(PygmentsHighlighter):
    """ A PygmentsHighlighter that can be turned on and off and that ignores
        prompts.
    """

    def __init__(self, python_widget):
        super(PythonWidgetHighlighter, self).__init__(
            python_widget._control.document())
        self._current_offset = 0
        self._python_widget = python_widget
        self.highlighting_on = False

    def highlightBlock(self, string):
        """ Highlight a block of text. Reimplemented to highlight selectively.
        """
        if not self.highlighting_on:
            return

        # The input to this function is a unicode string that may contain
        # paragraph break characters, non-breaking spaces, etc. Here we acquire
        # the string as plain text so we can compare it.
        current_block = self.currentBlock()
        string = self._python_widget._get_block_plain_text(current_block)

        # Decide whether to check for the regular or continuation prompt.
        if current_block.contains(self._python_widget._prompt_pos):
            prompt = self._python_widget._prompt
        else:
            prompt = self._python_widget._continuation_prompt

        # Don't highlight the part of the string that contains the prompt.
        if string.startswith(prompt):
            self._current_offset = len(prompt)
            string = string[len(prompt):]
        else:
            self._current_offset = 0

        super(PythonWidgetHighlighter, self).highlightBlock(string)

    def rehighlightBlock(self, block):
        """ Reimplemented to temporarily enable highlighting if disabled.
        """
        old = self.highlighting_on
        self.highlighting_on = True
        super(PythonWidgetHighlighter, self).rehighlightBlock(block)
        self.highlighting_on = old

    def setFormat(self, start, count, format):
        """ Reimplemented to highlight selectively.
        """
        start += self._current_offset
        super(PythonWidgetHighlighter, self).setFormat(start, count, format)

#-------------------------------------------------------------------------------
# 'PyfacePythonWidget' class:
#-------------------------------------------------------------------------------

class PyfacePythonWidget(PythonWidget):
    """ A PythonWidget customized to support the IPythonShell interface.
    """

    #--------------------------------------------------------------------------
    # 'object' interface
    #--------------------------------------------------------------------------

    def __init__(self, pyface_widget, *args, **kw):
        """ Reimplemented to store a reference to the Pyface widget which
            contains this control.
        """
        self._pyface_widget = pyface_widget

        super(PyfacePythonWidget, self).__init__(*args, **kw)

    #---------------------------------------------------------------------------
    # 'QWidget' interface
    #---------------------------------------------------------------------------

    def keyPressEvent(self, event):
        """ Reimplemented to generate Pyface key press events.
        """
        # Pyface doesn't seem to be Unicode aware.  Only keep the key code if it
        # corresponds to a single Latin1 character.
        kstr = event.text()
        try:
            kcode = ord(str(kstr))
        except:
            kcode = 0

        mods = event.modifiers()
        self._pyface_widget.key_pressed = KeyPressedEvent(
            alt_down     = ((mods & QtCore.Qt.AltModifier) == 
                            QtCore.Qt.AltModifier),
            control_down = ((mods & QtCore.Qt.ControlModifier) == 
                            QtCore.Qt.ControlModifier),
            shift_down   = ((mods & QtCore.Qt.ShiftModifier) == 
                            QtCore.Qt.ShiftModifier),
            key_code     = kcode,
            event        = event)

        super(PyfacePythonWidget, self).keyPressEvent(event)
