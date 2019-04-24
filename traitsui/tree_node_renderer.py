# Copyright (c) 2019, Enthought Inc.
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in enthought/LICENSE.txt and may be redistributed only
# under the conditions described in the aforementioned license.  The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
# Thanks for using Enthought open source!

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

        Returns
        -------
        size : tuple of (width, height) or None
            Optionally return a new preferred size so that the toolkit can
            perform better layout.
        """
        raise NotImplementedError()

    @abstractmethod
    def size(self, node, column, object, size_context):
        """ Return the preferred size for the item

        Parameters
        ----------
        node : ITreeNode instance
            The tree node to render.
        column : int
            The column in the tree that should be rendererd.
        object : object
            The underlying object being edited.
        size_context : object
            A toolkit-dependent context for performing sizing operations.

        Returns
        -------
        size : tuple of (width, height) or None
        """
        raise NotImplementedError()

    def get_label(self, node, object, column=0):
        """ Get the label associated with an item and column. """
        if column == 0:
            return node.get_label(object)
        else:
            return node.get_column_labels(object)[column]
