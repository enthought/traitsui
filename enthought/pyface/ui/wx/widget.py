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


# Enthought library imports.
from enthought.traits.api import Any, HasTraits, implements

# Local imports.
from enthought.pyface.i_widget import IWidget, MWidget


class Widget(MWidget, HasTraits):
    """ The toolkit specific implementation of a Widget.  See the IWidget
    interface for the API documentation.
    """

    implements(IWidget)

    #### 'IWidget' interface ##################################################

    control = Any

    parent = Any

    ###########################################################################
    # 'IWidget' interface.
    ###########################################################################

    def destroy(self):
        if self.control is not None:
            self.control.Destroy()
            self.control = None

#### EOF ######################################################################
