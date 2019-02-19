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

from random import choice

from pyface.qt import QtCore
from traits.api import HasTraits, Instance, List, Unicode

from traitsui.api import UItem, View
from traitsui.qt4.extra.styled_tree_editor import (
    StyledTreeEditor, StyledTreeItemDelegate, StyledTreeNode
)


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


if __name__ == '__main__':
    MyClass().configure_traits()
