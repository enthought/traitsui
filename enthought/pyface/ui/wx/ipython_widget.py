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
