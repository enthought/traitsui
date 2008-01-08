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
""" The wx specific implementation of a menu bar manager. """


# Major package imports.
import wx

# Local imports.
from enthought.pyface.action.action_manager import ActionManager


class MenuBarManager(ActionManager):
    """ A menu bar manager realizes itself in errr, a menu bar control. """

    ###########################################################################
    # 'MenuBarManager' interface.
    ###########################################################################

    def create_menu_bar(self, parent, controller=None):
        """ Creates a menu bar representation of the manager. """

        # If a controller is required it can either be set as a trait on the
        # menu bar manager (the trait is part of the 'ActionManager' API), or
        # passed in here (if one is passed in here it takes precedence over the
        # trait).
        if controller is None:
            controller = self.controller
            
        menu_bar = wx.MenuBar()
        
        # Every item in every group must be a menu manager.
        for group in self.groups:
            for item in group.items:
                menu = item.create_menu(parent, controller)
                menu_bar.Append(menu, item.name)
                 
        return menu_bar

#### EOF ######################################################################
