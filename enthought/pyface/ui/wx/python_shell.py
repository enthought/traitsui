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
#  Author: Enthought, Inc.
#
#------------------------------------------------------------------------------

""" Enthought pyface package component
"""

# Standard library imports.
import __builtin__
import os
import sys
import types

# Major package imports.
from wx.py.shell import Shell as PyShellBase
import wx

# Enthought library imports.
from enthought.traits.api import Event, implements

# Private Enthought library imports.
from enthought.util.clean_strings import python_name
from enthought.util.wx.drag_and_drop import PythonDropTarget

# Local imports.
from enthought.pyface.i_python_shell import IPythonShell, MPythonShell
from enthought.pyface.key_pressed_event import KeyPressedEvent
from widget import Widget


class PythonShell(MPythonShell, Widget):
    """ The toolkit specific implementation of a PythonShell.  See the
    IPythonShell interface for the API documentation.
    """

    implements(IPythonShell)

    #### 'IPythonShell' interface #############################################

    command_executed = Event

    key_pressed = Event(KeyPressedEvent)

    ###########################################################################
    # 'object' interface.
    ###########################################################################

    # FIXME v3: Either make this API consistent with other Widget sub-classes
    # or make it a sub-class of HasTraits.
    def __init__(self, parent, **traits):
        """ Creates a new pager. """

        # Base class constructor.
        super(PythonShell, self).__init__(**traits)

        # Create the toolkit-specific control that represents the widget.
        self.control = self._create_control(parent)

        # Set up to be notified whenever a Python statement is executed:
        self.control.handlers.append(self._on_command_executed)

    ###########################################################################
    # 'IPythonShell' interface.
    ###########################################################################

    def interpreter(self):
        return self.control.interp

    def execute_command(self, command, hidden=True):
        if hidden:
            self.control.hidden_push(command)
        else:
            # Replace the edit area text with command, then run it:
            self.control.Execute(command)

    def execute_file(self, path, hidden=True):
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

        # Redirect sys.std* to control or null
        old_stdin = sys.stdin
        old_stdout = sys.stdout
        old_stderr = sys.stderr
        if hidden:
            sys.stdin = sys.stdout = sys.stderr = _NullIO()
        else:
            sys.stdin = sys.stdout = sys.stderr = self.control

        # Execute the file
        try:
            if not hidden:
                self.control.clearCommand()
                self.control.write('# Executing "%s"\n' % path)

            if sys.platform == 'win32' and sys.version_info < (2,5,1):
                # Work around a bug in Python for Windows. For details, see:
                # http://projects.scipy.org/ipython/ipython/ticket/123
                exec file(path) in prog_ns, prog_ns
            else:
                execfile(path, prog_ns, prog_ns)

            if not hidden:
                self.control.prompt()
        finally:
            # Ensure key global stuctures are restored
            sys.argv = save_argv
            sys.modules['__main__'] = save_main
            sys.stdin = old_stdin
            sys.stdout = old_stdout
            sys.stderr = old_stderr

        # Update the interpreter with the new namespace
        del prog_ns['__name__']
        del prog_ns['__file__']
        del prog_ns['__nonzero__']
        self.interpreter().locals.update(prog_ns)

    ###########################################################################
    # 'IWidget' interface.
    ###########################################################################

    def _create_control(self, parent):
        shell = PyShell(parent, -1)

        # Listen for key press events.
        wx.EVT_CHAR(shell, self._wx_on_char)

        # Enable the shell as a drag and drop target.
        shell.SetDropTarget(PythonDropTarget(self))

        return shell

    ###########################################################################
    # 'PythonDropTarget' handler interface.
    ###########################################################################

    def on_drop(self, x, y, obj, default_drag_result):
        """ Called when a drop occurs on the shell. """

        # If we can't create a valid Python identifier for the name of an
        # object we use this instead.
        name = 'dragged'

        if hasattr(obj, 'name') \
           and isinstance(obj.name, basestring) and len(obj.name) > 0:
            py_name = python_name(obj.name)

            # Make sure that the name is actually a valid Python identifier.
            try:
                if eval(py_name, {py_name : True}):
                    name = py_name

            except:
                pass

        self.control.interp.locals[name] = obj
        self.control.run(name)
        self.control.SetFocus()

        # We always copy into the shell since we don't want the data
        # removed from the source
        return wx.DragCopy

    def on_drag_over(self, x, y, obj, default_drag_result):
        """ Always returns wx.DragCopy to indicate we will be doing a copy."""
        return wx.DragCopy

    ###########################################################################
    # Private handler interface.
    ###########################################################################

    def _wx_on_char(self, event):
        """ Called whenever a change is made to the text of the document. """

        # This was originally in the python_shell plugin, but is toolkit
        # specific.
        if event.m_altDown and event.m_keyCode == 317:
            zoom = self.shell.control.GetZoom()
            if zoom != 20:
                self.control.SetZoom(zoom+1)

        elif event.m_altDown and event.m_keyCode == 319:
            zoom = self.shell.control.GetZoom()
            if zoom != -10:
                self.control.SetZoom(zoom-1)

        self.key_pressed = KeyPressedEvent(
            alt_down     = event.m_altDown == 1,
            control_down = event.m_controlDown == 1,
            shift_down   = event.m_shiftDown == 1,
            key_code     = event.m_keyCode,
            event        = event
        )

        # Give other event handlers a chance.
        event.Skip()


class PyShell(PyShellBase):

    def __init__(self, parent, id=-1, pos=wx.DefaultPosition,
                 size=wx.DefaultSize, style=wx.CLIP_CHILDREN,
                 introText='', locals=None, InterpClass=None, *args, **kwds):
        self.handlers=[]

        # save a reference to the original raw_input() function since
        # wx.py.shell dosent reassign it back to the original on destruction
        self.raw_input = __builtin__.raw_input

        super(PyShell,self).__init__(parent, id, pos, size, style, introText,
                                     locals, InterpClass, *args, **kwds)

    def hidden_push(self, command):
        """ Send a command to the interpreter for execution without adding
            output to the display.
        """
        wx.BeginBusyCursor()
        try:
            self.waiting = True
            self.more = self.interp.push(command)
            self.waiting = False
            if not self.more:
                self.addHistory(command.rstrip())
                for handler in self.handlers:
                    handler()
        finally:
            # This needs to be out here to make this works with
            # enthought.util.refresh.refresh()
            wx.EndBusyCursor()

    def push(self, command):
        """Send command to the interpreter for execution."""
        self.write(os.linesep)
        self.hidden_push(command)
        self.prompt()

    def Destroy(self):
        """Cleanup before destroying the control...namely, return std I/O and
        the raw_input() function back to their rightful owners!
        """
        self.redirectStdout(False)
        self.redirectStderr(False)
        self.redirectStdin(False)
        __builtin__.raw_input = self.raw_input
        self.destroy()
        super(PyShellBase, self).Destroy()


class _NullIO:
    """ A portable /dev/null for use with PythonShell.execute_file.
    """
    def tell(self): return 0
    def read(self, n = -1): return ""
    def readline(self, length = None): return ""
    def readlines(self): return []
    def write(self, s): pass
    def writelines(self, list): pass
    def isatty(self): return 0
    def flush(self): pass
    def close(self): pass
    def seek(self, pos, mode = 0): pass

#### EOF ######################################################################
