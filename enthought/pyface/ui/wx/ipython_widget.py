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


class IPythonController(WxController):
    """ Subclas the IPython WxController as it tries to set the title and
        fails.
    """
    # The title of the IPython windows (not displayed in Envisage)
    title = Str


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
        if hidden:
            self.interp.execute_python(command)
        else:
            current_buffer = self.control.input_buffer
            self.control.input_buffer = command + '\n'
            self.control._on_enter()
            self.control.input_buffer = current_buffer
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
