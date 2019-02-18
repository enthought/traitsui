# -----------------------------------------------------------------------------
# Copyright (c) 2019, Enthought, Inc.
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in enthought/LICENSE.txt and may be redistributed only
# under the conditions described in the aforementioned license.  The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
# Thanks for using Enthought open source!
#
# -----------------------------------------------------------------------------
from __future__ import (
    absolute_import, division, print_function, unicode_literals
)

from collections import defaultdict

from pyface.qt import QtCore, QtGui
from pyface.timer.api import do_later
from traits.api import Bool, Type

from traitsui.api import TreeEditor as TreeEditorFactory, TreeNode
from traitsui.qt4.tree_editor import SimpleEditor as BaseSimpleEditor


class SimpleEditor(BaseSimpleEditor):
    """ A Qt TreeEditor which allows a QItemDelegate to be supplied for the
    drawing of items.
    """
    def init(self, parent):
        super(SimpleEditor, self).init(parent)

        # Create our item delegate
        delegate = self.factory.item_delegate_klass()
        delegate.editor = self
        self._tree.setItemDelegate(delegate)
        # From Qt Docs: QAbstractItemView does not take ownership of `delegate`
        self._item_delegate = delegate

    def _create_item(self, nid, node, instance, index=None):
        """ Override item creation to avoid `QTreeWidgetItem.setText` and
        `QTreeWidgetItem.setIcon` calls.
        """
        if not node.delegates_style:
            # Use the base class if this node is not styled
            return super(SimpleEditor, self)._create_item(
                nid, node, instance, index=index
            )

        if index is None:
            cnid = QtGui.QTreeWidgetItem(nid)
        else:
            cnid = QtGui.QTreeWidgetItem()
            nid.insertChild(index, cnid)

        cnid.setToolTip(0, node.get_tooltip(instance))
        self._set_column_labels(cnid, node.get_column_labels(instance))

        color = node.get_background(instance)
        if color:
            cnid.setBackground(0, self._get_brush(color))

        color = node.get_foreground(instance)
        if color:
            cnid.setForeground(0, self._get_brush(color))

        return cnid

    def _update_icon(self, nid):
        """ Override to avoid (again) calls to `QTreeWidgetItem.setIcon`
        """
        expanded, node, instance = self._get_node_data(nid)
        if not node.delegates_style:
            nid.setIcon(0, self._get_icon(node, instance, expanded))


class StyledTreeEditor(TreeEditorFactory):
    """ The EditorFactory for a StyledTreeEditor
    """
    #: A StyledTreeItemDelegate subclass which handles the drawing
    item_delegate_klass = Type

    def _get_simple_editor_class(self):
        return SimpleEditor


class StyledTreeItemDelegate(QtGui.QStyledItemDelegate):
    """ An ItemDelegate base class which handles `sizeHint`
    """
    def __init__(self, *args, **kwargs):
        self.size_map = defaultdict(lambda: QtCore.QSize(1, 21))
        QtGui.QStyledItemDelegate.__init__(self, *args, **kwargs)

    def custom_paint(self, painter, option, index, node, instance):
        """ The paint() method for subclasses to override.
        """
        raise NotImplementedError()

    def paint(self, painter, option, index):
        """ Draw the item """
        # Qt gives us some drawing for free
        super(StyledTreeItemDelegate, self).paint(painter, option, index)

        item = self.editor._tree.itemFromIndex(index)
        _, node, instance = self.editor._get_node_data(item)

        if node.delegates_style:
            self.custom_paint(painter, option, index, node, instance)
        else:
            # Need to set the appropriate sizeHint of the item.
            self.updateSizeHint(index, option.rect.size())

    def sizeHint(self, option, index):
        """ Returns area taken by the item. """
        return self.size_map[self.editor._tree.itemFromIndex(index)]

    def updateSizeHint(self, index, size):
        """ Updates the size stored in the size_map. """
        item = self.editor._tree.itemFromIndex(index)
        if self.size_map[item] != size:
            self.size_map[item] = size
            do_later(self.sizeHintChanged.emit, index)


class StyledTreeNode(TreeNode):
    """ A TreeNode to use with StyledTreeEditor
    """
    #: Set to True to use ItemDelegate for drawing
    delegates_style = Bool(False)


if __name__ == '__main__':
    from random import choice
    from traits.api import HasTraits, Instance, List, Unicode
    from traitsui.api import UItem, View

    class MyDataItem(HasTraits):
        text = Unicode

    class MyData(HasTraits):
        name = Unicode('Rooty McRootface')
        items = List(Instance(MyDataItem))

        def _items_default(self):
            DATA_ITEMS = (
                'I live on\nmultiple\nlines!', 'Foo\nBar', 'Baz', 'Qux',
            )
            return [MyDataItem(text=choice(DATA_ITEMS)) for _ in range(5)]

    class MyStyledTreeItemDelegate(StyledTreeItemDelegate):
        def custom_paint(self, painter, option, index, node, instance):
            """ The paint() method for subclasses to override.
            """
            text = node.get_label(instance)
            rect = painter.drawText(option.rect.left(),
                                    option.rect.top() + 2,
                                    option.rect.width(),
                                    option.rect.height() + 2,
                                    QtCore.Qt.TextWordWrap, text)

            # Need to set the appropriate sizeHint of the item.
            size = QtCore.QSize(rect.width(), rect.height() + 4)
            self.updateSizeHint(index, size)

    class MyClass(HasTraits):
        root = Instance(MyData, args=())
        traits_view = View(
            UItem(
                'root',
                editor=StyledTreeEditor(
                    item_delegate_klass=MyStyledTreeItemDelegate,
                    nodes=[
                        StyledTreeNode(
                            node_for=[MyData],
                            children='items',
                            label='name',
                        ),
                        StyledTreeNode(
                            delegates_style=True,
                            node_for=[MyDataItem],
                            auto_open=True,
                            label='text',
                        ),
                    ],
                    hide_root=False,
                    editable=False,
                ),
            ),
            resizable=True,
        )

    MyClass().configure_traits()
