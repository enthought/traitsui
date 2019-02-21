from abc import abstractmethod

from traits.api import ABCHasStrictTraits, Bool


class AbstractTreeNodeRenderer(ABCHasStrictTraits):
    """ Abstract base class for renderers of tree node items.

    This is currently only supported for Qt.
    """

    #: Whether the renderer handles rendering everything
    handles_all = Bool(False)

    #: Whether the renderer handles rendering any text
    handles_text = Bool(True)

    #: Whether the renderer handles rendering the icon or other decoration
    handles_icon = Bool(False)

    @abstractmethod
    def paint(self, node, column, object, paint_context):
        """ Render the node.

        Parameters
        ----------
        node : ITreeNode instance
            The tree node to render.
        column : int
            The column in the tree that should be rendererd.
        object : object
            The underlying object being edited.
        paint_context : object
            A toolkit-dependent context for performing paint operations.
        """
        raise NotImplementedError()

    def get_label(self, node, object, column=0):
        """ Get the label associated with an item and column. """
        if column == 0:
            return node.get_label(object)
        else:
            return node.get_column_labels(object)[column]
