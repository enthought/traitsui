# (C) Copyright 2004-2023 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

from pyface.qt import QtCore, QtGui

from pyface.ui_traits import HasBorder
from traits.api import Int

from traitsui.tree_node_renderer import AbstractTreeNodeRenderer
from .helper import wrap_text_with_elision


class WordWrapRenderer(AbstractTreeNodeRenderer):
    """A renderer that wraps the label text across multiple lines."""

    #: The padding around the text.
    padding = HasBorder(0)

    #: The a good size for the width of the item.
    width_hint = Int(100)

    #: The maximum number of lines to show without eliding.
    max_lines = Int(5)

    #: The extra border applied by Qt internally
    # XXX get this dynamically from Qt? How?
    extra_space = Int(8)

    def paint(self, editor, node, column, object, paint_context):
        """Paint word-wrapped text with elision."""
        painter, option, index = paint_context

        text = self.get_label(node, object, column)

        if editor.factory.show_icons:
            icon_width = option.decorationSize.width() + self.extra_space
            icon_height = option.decorationSize.height()
        else:
            icon_width = 0
            icon_height = 0

        x = option.rect.left() + icon_width + self.padding.left
        y = option.rect.top() + self.padding.top
        width = (
            option.rect.width()
            - icon_width
            - self.padding.left
            - self.padding.right
        )
        height = option.rect.height() - self.padding.top - self.padding.bottom

        lines = wrap_text_with_elision(text, option.font, width, height)

        old_pen = painter.pen()
        if bool(option.state & QtGui.QStyle.StateFlag.State_Selected):
            painter.setPen(QtGui.QPen(option.palette.highlightedText(), 0))
        try:
            rect = painter.drawText(
                x, y, width, height, option.displayAlignment, "\n".join(lines)
            )
        finally:
            painter.setPen(old_pen)

    def size(self, editor, node, column, object, size_context):
        """Return the preferred size for the word-wrapped text

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
        option, index = size_context
        font_metrics = QtGui.QFontMetrics(option.font)
        text = self.get_label(node, object, column)
        if editor.factory.show_icons:
            icon_size = option.decorationSize
            icon_width = icon_size.width()
            icon_height = icon_size.height()
        else:
            icon_width = 0
            icon_height = 0

        width = (
            self.width_hint
            - icon_width
            - self.padding.left
            - self.padding.right
        )
        max_height = self.max_lines * font_metrics.lineSpacing()
        lines = wrap_text_with_elision(text, option.font, width, max_height)

        text_height = len(lines) * font_metrics.lineSpacing()

        height = (
            max(icon_height, text_height)
            + self.padding.top
            + self.padding.bottom
            + self.extra_space
        )
        return self.width_hint, height
