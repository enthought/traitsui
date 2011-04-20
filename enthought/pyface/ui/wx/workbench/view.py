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

# Enthought library imports.
from enthought.traits.api import Bool
from enthought.pyface.workbench.i_view import MView


class View(MView):
    """ The toolkit specific implementation of a View.

    See the IView interface for the API documentation.

    """

    # Trait to indicate if the dock window containing the view should be
    # closeable. See FIXME comment in the _wx_create_view_dock_control method
    # in workbench_window_layout.py.
    closeable = Bool(False)

    ###########################################################################
    # 'IWorkbenchPart' interface.
    ###########################################################################

    def create_control(self, parent):
        """ Create the toolkit-specific control that represents the part. """

        import wx

        # By default we create a red panel!
        control = wx.Panel(parent, -1)
        control.SetBackgroundColour("red")
        control.SetSize((100, 200))

        return control

    def destroy_control(self):
        """ Destroy the toolkit-specific control that represents the part. """

        if self.control is not None:
            self.control.Destroy()
            self.control = None

        return

    def set_focus(self):
        """ Set the focus to the appropriate control in the part. """

        if self.control is not None:
            self.control.SetFocus()

        return

#### EOF ######################################################################
