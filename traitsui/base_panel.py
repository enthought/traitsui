# (C) Copyright 2004-2023 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

from pyface.action.api import ActionController
from traits.api import Any, Instance
from traitsui.menu import Action

# Set of all predefined system button names:
SystemButtons = {"Undo", "Redo", "Apply", "Revert", "OK", "Cancel", "Help"}


class BasePanel(ActionController):
    """Base class for Traits UI panels and dialog boxes.

    Concrete subclasses of BasePanel are the Python-side owners of the
    top-level toolkit control for a UI.  They also implement the Pyface
    ActionController API for menu and toolbar action handling.
    """

    #: The top-level toolkit control of the UI.
    control = Any()

    #: The UI instance for the view.
    ui = Instance("traitsui.ui.UI")

    def default_icon(self):
        """Return a default icon for a TraitsUI dialog."""
        from pyface.image_resource import ImageResource

        return ImageResource("frame.png")

    def check_button(self, buttons, action):
        """Adds *action* to the system buttons list for this dialog, if it is
        not already in the list.
        """
        name = action.name
        for button in buttons:
            if self.is_button(button, name):
                return
        buttons.append(action)

    def is_button(self, action, name):
        """Returns whether a specified action button is a system button."""
        if isinstance(action, str):
            return action == name
        return action.name == name

    def coerce_button(self, action):
        """Coerces a string to an Action if necessary."""
        if isinstance(action, str):
            return Action(
                name=action, action="" if action in SystemButtons else "?"
            )
        return action

    # Button handlers --------------------------------------------------------

    def _on_undo(self, event=None):
        """Handles an "Undo" change request."""
        self.ui.history.undo()

    def _on_redo(self, event=None):
        """Handles a "Redo" change request."""
        self.ui.history.redo()

    def _on_revert(self, event=None):
        """Handles a request to revert all changes."""
        ui = self.ui
        if ui.history is not None:
            ui.history.revert()
        ui.handler.revert(ui.info)

    def _on_help(self, event=None):
        """Handles the user clicking the Help button."""
        self.ui.handler.show_help(self.ui.info)

    # ------------------------------------------------------------------------
    # ActionController interface
    # ------------------------------------------------------------------------

    def perform(self, action, event):
        """Dispatches the action to be handled by the handler.

        Parameters
        ----------
        action : Action instance
            The action to perform.
        event : ActionEvent instance
            The event that triggered the action.

        Returns
        -------
        result : any
            The result of the action's perform method (usually None).
        """
        handler = self.ui.handler
        self.ui.do_undoable(handler.perform, self.ui.info, action, event)

    def add_to_menu(self, menu_item):
        """Adds a menu item to the menu bar being constructed.

        The bulk of the back-end work is done in Pyface.  This code is simply
        responsible for hooking up radio groups, checkboxes, and enabled
        status.

        This routine is also used to add items to the toolbar, as logic and
        APIs are identical.

        Parameters
        ----------

        menu_item : toolkit MenuItem
            The Pyface toolkit-level item to add to the menu.
        """
        item = menu_item.item
        action = item.action

        if action.id != "":
            self.ui.info.bind(action.id, menu_item)

        if action.enabled_when != "":
            self.ui.add_enabled(action.enabled_when, menu_item)

        if action.visible_when != "":
            self.ui.add_visible(action.visible_when, menu_item)

        if action.checked_when != "":
            self.ui.add_checked(action.checked_when, menu_item)

    def add_to_toolbar(self, toolbar_item):
        """Adds a menu item to the menu bar being constructed.

        The bulk of the back-end work is done in Pyface.  This code is simply
        responsible for hooking up radio groups, checkboxes, and enabled
        status.

        This simply calls the analagous menu as logic and APIs are identical.

        Parameters
        ----------

        toolbar_item : toolkit Tool
            The Pyface toolkit-level item to add to the toolbar.
        """
        self.add_to_menu(toolbar_item)

    def can_add_to_menu(self, action):
        """Should the toolbar action be defined in the user interface.

        This simply calls the analagous menu as logic and APIs are identical.

        Parameters
        ----------

        action : Action
            The Action to add to the toolbar.

        Returns
        -------
        defined : bool
            Whether or not the action should be added to the menu.
        """
        if action.defined_when == "":
            return True

        return self.ui.eval_when(action.defined_when)

    def can_add_to_toolbar(self, action):
        """Should the toolbar action be defined in the user interface.

        This simply calls the analagous menu as logic and APIs are identical.

        Parameters
        ----------

        action : Action
            The Action to add to the toolbar.

        Returns
        -------
        defined : bool
            Whether or not the action should be added to the toolbar.
        """
        return self.can_add_to_menu(action)
