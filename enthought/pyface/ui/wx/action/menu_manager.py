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

""" The wx specific implementation of a menu manager.
"""

# Major package imports.
import wx

# Enthought library imports.
from enthought.traits.api import Unicode

# Local imports.
from enthought.pyface.action.action_manager import ActionManager
from enthought.pyface.action.action_manager_item import ActionManagerItem
from enthought.pyface.action.group import Group


class MenuManager(ActionManager, ActionManagerItem):
    """ A menu manager realizes itself in a menu control.

    This could be a sub-menu or a context (popup) menu.
    """

    #### 'MenuManager' interface ##############################################

    # The menu manager's name (if the manager is a sub-menu, this is what its
    # label will be).
    name = Unicode

    ###########################################################################
    # 'MenuManager' interface.
    ###########################################################################

    def create_menu(self, parent, controller=None):
        """ Creates a menu representation of the manager. """

        # If a controller is required it can either be set as a trait on the
        # menu manager (the trait is part of the 'ActionManager' API), or
        # passed in here (if one is passed in here it takes precedence over the
        # trait).
        if controller is None:
            controller = self.controller

        return _Menu(self, parent, controller)

    ###########################################################################
    # 'ActionManagerItem' interface.
    ###########################################################################

    def add_to_menu(self, parent, menu, controller):
        """ Adds the item to a menu. """

        id  = wx.NewId()
        sub = self.create_menu(parent, controller)

        # fixme: Nasty hack to allow enabling/disabling of menus.
        sub._id = id
        sub._menu = menu
        
        menu.AppendMenu(id, self.name, sub)

        return

    def add_to_toolbar(self, parent, tool_bar, image_cache, controller):
        """ Adds the item to a tool bar. """

        raise ValueError("Cannot add a menu manager to a toolbar.")


class _Menu(wx.Menu):
    """ The toolkit-specific menu control. """

    ###########################################################################
    # 'object' interface.
    ###########################################################################

    def __init__(self, manager, parent, controller):
        """ Creates a new tree. """

        # Base class constructor.
        wx.Menu.__init__(self)

        # The parent of the menu.
        self._parent = parent
        
        # The manager that the menu is a view of.
        self._manager = manager

        # The controller.
        self._controller = controller
        
        # List of menu items
        self.menu_items = []
        
        # Create the menu structure.
        self.refresh()

        # Listen to the manager being updated.
        self._manager.on_trait_change(self.refresh, 'changed')
        self._manager.on_trait_change(self._on_enabled_changed, 'enabled')

        return

    ###########################################################################
    # '_Menu' interface.
    ###########################################################################

    def clear(self):
        """ Clears the items from the menu. """
        
        for item in self.GetMenuItems():
            if item.GetSubMenu() is not None:
                item.GetSubMenu().clear()
            self.Delete(item.GetId())
            
        for item in self.menu_items:
            item.dispose()
        
        self.menu_items = []

        return

    def is_empty(self):
        """ Is the menu empty? """

        return self.GetMenuItemCount() == 0

    def refresh(self):
        """ Ensures that the menu reflects the state of the manager. """

        self.clear()

        manager = self._manager
        parent  = self._parent

        previous_non_empty_group = None
        for group in manager.groups:
            previous_non_empty_group = self._add_group(
                parent, group, previous_non_empty_group
            )

        return

    def show(self, x, y):
        """ Show the menu at the specified location. """

        self._parent.PopupMenuXY(self, x, y)

        return

    ###########################################################################
    # Private interface.
    ###########################################################################

    def _on_enabled_changed(self, obj, trait_name, old, new):
        """ Dynamic trait change handler. """

        # fixme: Nasty hack to allow enabling/disabling of menus.
        #
        # We cannot currently (AFAIK) disable menus on the menu bar. Hence
        # we don't give them an '_id'...

        if hasattr(self, '_id'):
            self._menu.Enable(self._id, new)
        
        return
    
    def _add_group(self, parent, group, previous_non_empty_group=None):
        """ Adds a group to a menu. """

        if len(group.items) > 0:
            # Is a separator required?
            if previous_non_empty_group is not None and group.separator:
                self.AppendSeparator()

            # Create actions and sub-menus for each contribution item in
            # the group.
            for item in group.items:
                if isinstance(item, Group):
                    if len(item.items) > 0:
                        self._add_group(parent, item, previous_non_empty_group)

                        if previous_non_empty_group is not None \
                           and previous_non_empty_group.separator \
                           and item.separator:
                            self.AppendSeparator()

                        previous_non_empty_group = item

                else:
                    item.add_to_menu(parent, self, self._controller)

            previous_non_empty_group = group

        return previous_non_empty_group

#### EOF ######################################################################
