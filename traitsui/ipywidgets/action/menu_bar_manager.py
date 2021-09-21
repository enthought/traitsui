from pyface.action.action_manager import ActionManager


class MenuBarManager(ActionManager):
    """ A menu bar manager realizes itself in a menu bar control. """

    # ------------------------------------------------------------------------
    # 'MenuBarManager' interface.
    # ------------------------------------------------------------------------

    def create_menu_bar(self, parent, controller=None):
        """ Creates a menu bar representation of the manager. """
        # IPyWidgets doesn't currently support menus.
        pass