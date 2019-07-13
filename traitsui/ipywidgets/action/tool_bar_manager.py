from pyface.action.action_manager import ActionManager
from traits.api import Bool, Enum, Str, Tuple


class ToolBarManager(ActionManager):
    """ A tool bar manager realizes itself as a tool bar widget.
    """

    # 'ToolBarManager' interface -----------------------------------------------

    #: The size of tool images (width, height).
    image_size = Tuple((16, 16))

    #: The toolbar name (used to distinguish multiple toolbars).
    name = Str('ToolBar')

    #: The orientation of the toolbar.
    orientation = Enum('horizontal', 'vertical')

    #: Should we display the name of each tool bar tool under its image?
    show_tool_names = Bool(True)

    #: Should we display the horizontal divider?
    show_divider = Bool(True)

    # ------------------------------------------------------------------------
    # 'ToolBarManager' interface.
    # ------------------------------------------------------------------------

    def create_tool_bar(self, parent, controller=None):
        """ Creates a tool bar. """
        # IPyWidgets doesn't currently support toolbars.
        pass