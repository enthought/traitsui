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

""" The wx-backend Pyface widget for an embedded IPython shell.
"""

# Standard library imports.
import __builtin__
import codeop
import re
import sys

# System library imports
import IPython
from IPython.frontend.wx.wx_frontend import WxController
from IPython.kernel.core.interpreter import Interpreter
import wx

# Enthought library imports.
from enthought.io.file import File as EnthoughtFile
from enthought.pyface.i_python_shell import IPythonShell
from enthought.pyface.key_pressed_event import KeyPressedEvent
from enthought.traits.api import Event, implements, Instance, Str
from enthought.util.clean_strings import python_name
from enthought.util.wx.drag_and_drop import PythonDropTarget

# Local imports.
from widget import Widget

# Constants.
IPYTHON_VERSION = tuple(map(int, IPython.Release.version_base.split('.')))


class IPythonController(WxController):
    """ An WxController for IPython version >= 0.9. Adds a few extras.
    """

    def __init__(self, *args, **kwargs):
        WxController.__init__(self, *args, **kwargs)
        
        # Add a magic to clear the screen
        def cls(args):
            self.ClearAll()
        self.ipython0.magic_cls = cls


class IPython010Controller(IPythonController):
    """ A WxController hacked/patched specifically for the 0.10 branch.
    """
    
    def execute_command(self, command, hidden=False):
        # XXX: Overriden to fix bug where executing a hidden command still
        # causes the prompt number to increase.
        super(IPython010Controller, self).execute_command(command, hidden)
        if hidden:
            self.shell.current_cell_number -= 1


class IPython09Controller(IPythonController):
    """ A WxController hacked/patched specifically for the 0.9 branch.
    """

    # In the parent class, this is a property that expects the
    # container to be a frame, thus it fails when modified.
    # The title of the IPython windows (not displayed in Envisage)
    title = Str

    # Cached value of the banner for the IPython shell.
    # NOTE: The WxController object (declared in wx_frontend module) contains
    # a 'banner' attribute. If this is None, WxController sets the
    # banner = IPython banner + an additional string ("This is the wx 
    # frontend, by Gael Varoquaux. This is EXPERIMENTAL code."). We want to 
    # set banner = the IPython banner. This means 'banner' needs to be
    # a property, since in the __init__ method of WxController, the IPython 
    # shell object is created AND started (meaning the banner is written to
    # stdout). 
    _banner = None

    def _get_banner(self):
        """ Returns the IPython banner.
        """
        if self._banner is None:
            # 'ipython0' gets set in the __init__ method of the base class.
            if hasattr(self, 'ipython0'):
                self._banner = self.ipython0.BANNER
        return self._banner

    def _set_banner(self, value):
        self._banner = value

    banner = property(_get_banner, _set_banner)


    def __init__(self, *args, **kwargs):
        # This is a hack to avoid the IPython exception hook to trigger
        # on exceptions (https://bugs.launchpad.net/bugs/337105)
        # XXX: This is horrible: module-level monkey patching -> side
        # effects.
        from IPython import iplib
        iplib.InteractiveShell.isthreaded = True

        # Suppress all key input, to avoid waiting
        def my_rawinput(x=None):
            return '\n'
        old_rawinput = __builtin__.raw_input
        __builtin__.raw_input = my_rawinput
        IPythonController.__init__(self, *args, **kwargs)
        __builtin__.raw_input = old_rawinput

        # XXX: This is bugware for IPython bug:
        # https://bugs.launchpad.net/ipython/+bug/270998
        # Fix all the magics with no docstrings:
        for funcname in dir(self.ipython0):
            if not funcname.startswith('magic'):
                continue
            func = getattr(self.ipython0, funcname)
            try:
                if func.__doc__ is None:
                    func.__doc__ = ''
            except AttributeError:
                """ Avoid "attribute '__doc__' of 'instancemethod'
                    objects is not writable".
                """

    def complete(self, line):
        """ Returns a list of possible completions for line.
        Overridden from the base class implementation to fix bugs in retrieving
        the completion text from line.
        
        """
          
        completion_text = self._get_completion_text(line)
        suggestion, completions = super(IPython09Controller, self).complete( \
            completion_text)
        new_line = line[:-len(completion_text)] + suggestion
        return new_line, completions

    def is_complete(self, string):
        """ Check if a string forms a complete, executable set of
        commands.

        For the line-oriented frontend, multi-line code is not executed
        as soon as it is complete: the users has to enter two line
        returns.
        
        Overridden from the base class (linefrontendbase.py in IPython\frontend
        to handle a bug with using the '\' symbol in multi-line inputs.
        """
        
        # FIXME: There has to be a nicer way to do this. Th code is
        # identical to the base class implementation, except for the if ..
        # statement on line 146.
        if string in ('', '\n'):
            # Prefiltering, eg through ipython0, may return an empty
            # string although some operations have been accomplished. We
            # thus want to consider an empty string as a complete
            # statement.
            return True
        elif ( len(self.input_buffer.split('\n'))>2 
                        and not re.findall(r"\n[\t ]*\n[\t ]*$", string)):
            return False
        else:
            self.capture_output()
            try:
                # Add line returns here, to make sure that the statement is
                # complete (except if '\' was used).
                # This should probably be done in a different place (like
                # maybe 'prefilter_input' method? For now, this works.
                clean_string = string.rstrip('\n')
                if not clean_string.endswith('\\'): clean_string +='\n\n' 
                is_complete = codeop.compile_command(clean_string,
                            "<string>", "exec")
                self.release_output()
            except Exception, e:
                # XXX: Hack: return True so that the
                # code gets executed and the error captured.
                is_complete = True
            return is_complete
        
    def execute_command(self, command, hidden=False):
        """ Execute a command, not only in the model, but also in the
            view.
        """
        # XXX: This needs to be moved to the IPython codebase.
        if hidden:
            result = self.shell.execute(command)
            # XXX: Fix bug where executing a hidden command still causes the
            # prompt number to increase.
            self.shell.current_cell_number -= 1
            return result
        else:
            # XXX: we are not storing the input buffer previous to the
            # execution, as this forces us to run the execution
            # input_buffer a yield, which is not good.
            ##current_buffer = self.shell.control.input_buffer
            command = command.rstrip()
            if len(command.split('\n')) > 1:
                # The input command is several lines long, we need to
                # force the execution to happen
                command += '\n'
            cleaned_command = self.prefilter_input(command)
            self.input_buffer = command
            # Do not use wx.Yield() (aka GUI.process_events()) to avoid
            # recursive yields.
            self.ProcessEvent(wx.PaintEvent())
            self.write('\n')
            if not self.is_complete(cleaned_command + '\n'):
                self._colorize_input_buffer()
                self.render_error('Incomplete or invalid input')
                self.new_prompt(self.input_prompt_template.substitute(
                                number=(self.last_result['number'] + 1)))
                return False
            self._on_enter()
            return True

    def clear_screen(self):
        """ Empty completely the widget.
        """
        self.ClearAll()
        self.new_prompt(self.input_prompt_template.substitute(
                                number=(self.last_result['number'] + 1)))

    def continuation_prompt(self):
        """Returns the current continuation prompt.
        Overridden to generate a continuation prompt matching the length of the
        current prompt."""
        
        # This assumes that the prompt is always of the form 'In [#]'.
        n = self.last_result['number']
        promptstr = "In [%d]" % n
        return ("."*len(promptstr) + ':')    
    
    def _popup_completion(self, create=False):
        """ Updates the popup completion menu if it exists. If create is 
            true, open the menu.
            Overridden from the base class implementation to filter out
            delimiters from the input buffer.
        """
        
        # FIXME: The implementation in the base class (wx_frontend.py in
        # IPython/wx/frontend) is faulty in that it doesn't filter out 
        # special characters (such as parentheses, '=') in the input buffer 
        # correctly. 
        # For example, (a): typing 's=re.' does not pop up the menu.  
        # (b): typing 'x[0].' brings up a menu for x[0] but the offset is
        # incorrect and so, upon selection from the menu, the text is pasted 
        # incorrectly.
        # I am patching this here instead of in the IPython module, but at some
        # point, this needs to be merged in.
        if self.debug:
            print >>sys.__stdout__, "_popup_completion" , self.input_buffer
        
        line = self.input_buffer        
        if (self.AutoCompActive() and line and not line[-1] == '.') \
                    or create==True:
            suggestion, completions = self.complete(line)
            if completions:
                offset = len(self._get_completion_text(line))
                self.pop_completion(completions, offset=offset)
                if self.debug:
                    print >>sys.__stdout__, completions
    
    def _get_completion_text(self, line):
        """ Returns the text to be completed by breaking the line at specified
        delimiters.
        """
        # Break at: spaces, '=', all parentheses (except if balanced).
        # FIXME2: In the future, we need to make the implementation similar to
        # that in the 'pyreadline' module (modes/basemode.py) where we break at
        # each delimiter and try to complete the residual line, until we get a
        # successful list of completions.
        expression = '\s|=|,|:|\((?!.*\))|\[(?!.*\])|\{(?!.*\})' 
        complete_sep = re.compile(expression)
        text = complete_sep.split(line)[-1]
        return text

    def _on_enter(self):
        """ Called when the return key is pressed in a line editing
            buffer.
            Overridden from the base class implementation (in 
            IPython/frontend/linefrontendbase.py) to include a continuation
            prompt.
        """
        current_buffer = self.input_buffer
        cleaned_buffer = self.prefilter_input(current_buffer.replace(
                                            self.continuation_prompt(),
                                            ''))
        if self.is_complete(cleaned_buffer):
            self.execute(cleaned_buffer, raw_string=current_buffer)
        else:
            self.input_buffer = current_buffer + \
                                self.continuation_prompt() + \
                                self._get_indent_string(current_buffer.replace(
                                            self.continuation_prompt(),
                                            '')[:-1])
            if len(current_buffer.split('\n')) == 2:
                self.input_buffer += '\t\t'
            if current_buffer[:-1].split('\n')[-1].rstrip().endswith(':'):
                self.input_buffer += '\t'


class IPythonWidget(Widget):
    """ The toolkit specific implementation of a PythonShell.  See the
    IPythonShell interface for the API documentation.
    """

    implements(IPythonShell)

    #### 'IPythonShell' interface #############################################

    command_executed = Event

    key_pressed = Event(KeyPressedEvent)

    #### 'IPythonWidget' interface ############################################

    interp = Instance(Interpreter, ())

    ###########################################################################
    # 'object' interface.
    ###########################################################################

    # FIXME v3: Either make this API consistent with other Widget sub-classes
    # or make it a sub-class of HasTraits.
    def __init__(self, parent, **traits):
        """ Creates a new pager. """

        # Base class constructor.
        super(IPythonWidget, self).__init__(**traits)

        # Create the toolkit-specific control that represents the widget.
        self.control = self._create_control(parent)

    ###########################################################################
    # 'IPythonShell' interface.
    ###########################################################################

    def interpreter(self):
        return self.interp

    def execute_command(self, command, hidden=True):
        self.control.execute_command(command, hidden=hidden)
        self.command_executed = True

    def execute_file(self, path, hidden=True):
        self.control.execute_command('%run ' + '"%s"' % path, hidden=hidden)
        self.command_executed = True

    ###########################################################################
    # Protected 'IWidget' interface.
    ###########################################################################

    def _create_control(self, parent):
        # Create the controller based on the version of the installed IPython
        klass = IPythonController
        if IPYTHON_VERSION[0] == 0:
            if IPYTHON_VERSION[1] == 9:
                klass = IPython09Controller
            elif IPYTHON_VERSION[1] == 10:
                klass = IPython010Controller
        shell = klass(parent, -1, shell=self.interp)

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

        # If this is a file, we'll just print the file name
        if isinstance(obj, EnthoughtFile):
            self.control.write(obj.absolute_path) 
            
        elif ( isinstance(obj, list) and len(obj) ==1 
                        and isinstance(obj[0], EnthoughtFile)):
            self.control.write(obj[0].absolute_path) 
            
        else:
            # Not a file, we'll inject the object in the namespace
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

            self.interp.user_ns[name] = obj
            self.execute_command(name, hidden=False)
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

        self.key_pressed = KeyPressedEvent(
            alt_down     = event.m_altDown == 1,
            control_down = event.m_controlDown == 1,
            shift_down   = event.m_shiftDown == 1,
            key_code     = event.m_keyCode,
            event        = event
        )

        # Give other event handlers a chance.
        event.Skip()
