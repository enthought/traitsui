#------------------------------------------------------------------------------
# Copyright (c) 2007, Riverbank Computing Limited
# All rights reserved.
# 
# This software is provided without warranty under the terms of the BSD license.
# However, when used with the GPL version of PyQt the additional terms described in the PyQt GPL exception also apply

# 
# Author: Riverbank Computing Limited
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
            self.control.hide()
            self.control.deleteLater()
            self.control = None

#### EOF ######################################################################
