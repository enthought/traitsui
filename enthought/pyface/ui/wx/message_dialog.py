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
from enthought.traits.api import Enum, implements, Unicode

# Local imports.
from enthought.pyface.i_message_dialog import IMessageDialog, MMessageDialog
from dialog import Dialog


# Map the ETS severity to the corresponding wx standard icon.
_SEVERITY_TO_ICON_MAP = {
    'information':  wx.ICON_INFORMATION,
    'warning':      wx.ICON_WARNING,
    'error':        wx.ICON_ERROR
}


class MessageDialog(MMessageDialog, Dialog):
    """ The toolkit specific implementation of a MessageDialog.  See the
    IMessageDialog interface for the API documentation.
    """

    implements(IMessageDialog)

    #### 'IMessageDialog' interface ###########################################

    message = Unicode

    severity = Enum('information', 'warning', 'error')

    ###########################################################################
    # Protected 'IDialog' interface.
    ###########################################################################

    def _create_contents(self, parent):
        # In wx this is a canned dialog.
        pass

    ###########################################################################
    # Protected 'IWidget' interface.
    ###########################################################################

    def _create_control(self, parent):
        return wx.MessageDialog(parent, self.message, self.title,
                _SEVERITY_TO_ICON_MAP[self.severity] | wx.OK | wx.STAY_ON_TOP)

#### EOF ######################################################################
