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

# Major package imports.
from IPython.frontend.wx.wx_frontend import WxController
from IPython.kernel.core.interpreter import Interpreter
import wx

# Enthought library imports.
from enthought.traits.api import Event, implements, Instance, Str

# Private Enthought library imports.
from enthought.util.clean_strings import python_name
from enthought.util.wx.drag_and_drop import PythonDropTarget
from enthought.io.file import File as EnthoughtFile

# Local imports.
from enthought.pyface.i_python_shell import IPythonShell
from enthought.pyface.key_pressed_event import KeyPressedEvent
from widget import Widget

################################################################################
class IPythonController(WxController):
    """ Subclass the IPython WxController

        This class should probably be moved in the IPython codebase.
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
            if getattr(self, 'ipython0', None):
                self._banner = self.ipython0.BANNER
        return self._banner

    def _set_banner(self, value):
        self._banner = value
        return

    banner = property(_get_banner, _set_banner)

    def __init__(self, *args, **kwargs):
        WxController.__init__(self, *args, **kwargs)

        # Add a magic to clear the screen
        def cls(args):
            """ Clear the screen.
            """
            self.ClearAll()
        self.ipython0.magic_cls = cls

        # XXX: This is bugware for IPython bug:
        # https://bugs.launchpad.net/ipython/+bug/270998
        # Fix all the magics with no docstrings:
        for funcname in dir(self.ipython0):
            if not funcname.startswith('magic'):
                continue
            func = getattr(self.ipython0, funcname)
            if func.__doc__ is None:
                func.__doc__ = ''

    def execute_command(self, command, hidden=False):
        """ Execute a command, not only in the model, but also in the
            view.
        """
        # XXX: This needs to be moved to the IPython codebase.
        if hidden:
            return self.shell.execute(command)
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


################################################################################
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

    def execute_command(self, command, hidden=False):
        self.control.execute_command(command, hidden=hidden)
        self.command_executed = True

    ###########################################################################
    # Protected 'IWidget' interface.
    ###########################################################################

    def _create_control(self, parent):
        shell = IPythonController(parent, -1, shell=self.interp)

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

        return

#### EOF ######################################################################
