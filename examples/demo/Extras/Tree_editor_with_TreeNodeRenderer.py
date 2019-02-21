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

import numpy as np

from pyface.qt import QtCore, QtGui
from traits.api import Array, HasTraits, Instance, List, Unicode

from traitsui.api import TreeEditor, TreeNode, UItem, View
from traitsui.tree_node_renderer import AbstractTreeNodeRenderer
from traitsui.qt4.tree_editor import WordWrapRenderer


class MyDataItem(HasTraits):
    text = Unicode

    data = Array

    def _data_default(self):
        return np.random.standard_normal((1000,)).cumsum()


class MyData(HasTraits):
    name = Unicode('Rooty McRootface')
    items = List(Instance(MyDataItem))

    def _items_default(self):
        DATA_ITEMS = (
            'I live on\nmultiple\nlines!', 'Foo\nBar', 'Baz', 'Qux',
        )
        return [MyDataItem(text=choice(DATA_ITEMS)) for _ in range(5)]


class SparklineRenderer(AbstractTreeNodeRenderer):

    handles_all = True

    def paint(self, editor, node, column, object, paint_context):
        painter, option, index = paint_context
        data = self.get_data(object)

        xs = np.linspace(0, option.rect.width() - 4, len(data)) + option.rect.left() + 2
        ys = (data - data.min())/data.ptp() * (option.rect.height() - 4) + option.rect.top() + 2

        points = [QtCore.QPointF(x, y) for x, y in zip(xs, ys)]

        if bool(option.state & QtGui.QStyle.State_Selected):
            painter.fillRect(option.rect, option.palette.highlight())

        painter.drawPolyline(points)

        return None

    def get_data(self, object):
        return object.data


class SparklineTreeNode(TreeNode):

    def get_renderer(self, object, column=0):
        if column == 1:
            return SparklineRenderer()
        else:
            return WordWrapRenderer()


class MyClass(HasTraits):
    root = Instance(MyData, args=())
    traits_view = View(
        UItem(
            'root',
            editor=TreeEditor(
                nodes=[
                    TreeNode(
                        node_for=[MyData],
                        children='items',
                        label='name',
                    ),
                    SparklineTreeNode(
                        node_for=[MyDataItem],
                        auto_open=True,
                        label='text',
                    ),
                ],
                column_headers=["The Tree View", "The Sparklines"],
                hide_root=False,
                editable=False,
            ),
        ),
        resizable=True,
        width=400,
        height=300,
    )


if __name__ == '__main__':
    MyClass().configure_traits()
