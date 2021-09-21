from pyface.action.action import Action
from pyface.action.action_manager import ActionManager
from pyface.action.action_manager_item import ActionManagerItem
from traits.api import Unicode, Instance


class MenuManager(ActionManager, ActionManagerItem):
    """ A menu manager realizes itself in a menu control.
    This could be a sub-menu or a context (popup) menu.
    """

    # 'MenuManager' interface -----------------------------------------------

    #: The menu manager's name
    name = Unicode

    #: The default action for tool button when shown in a toolbar (Qt only)
    action = Instance(Action)

    # ------------------------------------------------------------------------
    # 'MenuManager' interface.
    # ------------------------------------------------------------------------

    def create_menu(self, parent, controller=None):
        """ Creates a menu representation of the manager. """
        # IPyWidgets doesn't currently support menus.
        pass

    # ------------------------------------------------------------------------
    # 'ActionManagerItem' interface.
    # ------------------------------------------------------------------------

    def add_to_menu(self, parent, menu, controller):
        """ Adds the item to a menu. """
        # IPyWidgets doesn't currently support menus.
        pass

    def add_to_toolbar(self, parent, tool_bar, image_cache, controller,
                       show_labels=True):
        """ Adds the item to a tool bar. """
        pass
