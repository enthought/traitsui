#  Copyright (c) 2007, Enthought, Inc.
#  License: BSD Style.

# array_editor.py -- Example of using array editors

#--[Imports]--------------------------------------------------------------
from __future__ import absolute_import
from numpy import int16, float32

from traits.api import HasPrivateTraits, Array
from traitsui.api import View, ArrayEditor, Item
from traitsui.menu import NoButtons

#--[Code]-----------------------------------------------------------------


class ArrayEditorTest(HasPrivateTraits):

    three = Array(int16, (3, 3))
    four = Array(float32,
                 (4, 4),
                 editor=ArrayEditor(width=-50))

    view = View(Item('three', label='3x3 Integer'),
                '_',
                Item('three',
                     label='Integer Read-only',
                     style='readonly'),
                '_',
                Item('four', label='4x4 Float'),
                '_',
                Item('four',
                     label='Float Read-only',
                     style='readonly'),
                buttons=NoButtons,
                resizable=True)


if __name__ == '__main__':
    ArrayEditorTest().configure_traits()
