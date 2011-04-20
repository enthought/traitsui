#------------------------------------------------------------------------------
# Copyright (c) 2006, Enthought, Inc.
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

# Enthought library imports
from enthought.traits.api import Any, HasTraits

class GridCellRenderer(HasTraits):

    # The toolkit-specific renderer for this cell.
    renderer = Any

    # A handler to be invoked on right-button mouse clicks.
    def on_right_click(self, grid, row, col):
        pass

    # A handler to be invoked on right-button mouse double clicks.
    def on_right_dclick(self, grid, row, col):
        pass

    # A handler to be invoked on left-button mouse clicks.
    def on_left_click(self, grid, row, col):
        pass

    # A handler to be invoked on left-button mouse double clicks.
    def on_left_dclick(self, grid, row, col):
        pass

    # A handler to be invoked on key press.
    def on_key(self, grid, row, col, key_event):
        pass

    # Clean-up!
    def dispose(self):
        pass

#### EOF ######################################################################
