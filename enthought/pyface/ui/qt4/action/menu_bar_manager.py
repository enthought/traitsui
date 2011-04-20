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
""" The PyQt specific implementation of a menu bar manager. """


# Major package imports.
from enthought.qt import QtGui

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

        menu_bar = QtGui.QMenuBar(parent)

        # Every item in every group must be a menu manager.
        for group in self.groups:
            for item in group.items:
                menu = item.create_menu(parent, controller)
                menu.menuAction().setText(item.name)
                menu_bar.addMenu(menu)

        return menu_bar

#### EOF ######################################################################
