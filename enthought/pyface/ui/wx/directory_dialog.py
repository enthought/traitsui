#------------------------------------------------------------------------------
# Copyright (c) 2005, Enthought, Inc.
# All rights reserved.
# 
# This software is provided without warranty under the terms of the BSD
# license included in enthought/LICENSE.txt and may be redistributed only
# under the conditions described in the aforementioned license.  The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
# Thanks for using Enthought open source!
# 
# Author: Enthought, Inc.
# Description: <Enthought pyface package component>
#------------------------------------------------------------------------------


# Major package imports.
import wx

# Enthought library imports.
from enthought.traits.api import Bool, implements, Unicode

# Local imports.
from enthought.pyface.i_directory_dialog import IDirectoryDialog, MDirectoryDialog
from dialog import Dialog


class DirectoryDialog(MDirectoryDialog, Dialog):
    """ The toolkit specific implementation of a DirectoryDialog.  See the
    IDirectoryDialog interface for the API documentation.
    """

    implements(IDirectoryDialog)

    #### 'IDirectoryDialog' interface #########################################

    default_path = Unicode

    message = Unicode

    new_directory = Bool(True)

    path = Unicode

    ###########################################################################
    # Protected 'IDialog' interface.
    ###########################################################################

    def _create_contents(self, parent):
        # In wx this is a canned dialog.
        pass

    ###########################################################################
    # 'IWindow' interface.
    ###########################################################################

    def close(self):
        # Get the path of the chosen directory.
        self.path = unicode(self.control.GetPath())

        # Let the window close as normal.
        super(DirectoryDialog, self).close()

    ###########################################################################
    # Protected 'IWidget' interface.
    ###########################################################################

    def _create_control(self, parent):
        # The default style.
        style = wx.OPEN | wx.HIDE_READONLY

        # Create the wx style depending on which buttons are required etc.
        if self.new_directory:
            style = style | wx.DD_NEW_DIR_BUTTON

        if self.message:
            message = self.message
        else:
            message = "Choose a directory"

        # Create the actual dialog.
        return wx.DirDialog(parent, message=message,
                defaultPath=self.default_path, style=style)

#### EOF ######################################################################
