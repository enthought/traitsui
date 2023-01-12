# (C) Copyright 2004-2023 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

from unittest import TestCase

from traits.api import HasTraits, Str, Int, List
from traitsui.api import View, Group, Item, TableEditor, ObjectColumn, RGBColor
from traitsui.color_column import ColorColumn

from traitsui.tests._tools import (
    BaseTestMixin,
    create_ui,
    requires_toolkit,
    reraise_exceptions,
    ToolkitName,
)


class MyEntry(HasTraits):
    name = Str()
    value = Int(0)
    color = RGBColor()

    entry_view = View(Group(Item("name"), Item("value"), Item("color")))


my_editor = TableEditor(
    columns=[
        ObjectColumn(name="name"),
        ObjectColumn(name="value"),
        ColorColumn(name="color", style="readonly"),
    ],
    orientation="vertical",
    show_toolbar=True,
    row_factory=MyEntry,
)


class MyData(HasTraits):
    data_list = List(MyEntry)

    view = View(Item("data_list", editor=my_editor, show_label=False))


class TestColorColumn(BaseTestMixin, TestCase):
    def setUp(self):
        BaseTestMixin.setUp(self)

    def tearDown(self):
        BaseTestMixin.tearDown(self)

    @requires_toolkit([ToolkitName.qt, ToolkitName.wx])
    def test_color_column(self):
        # Behaviour: column ui should display without error

        d1 = MyEntry(name="a", value=2, color=(1.0, 0.3, 0.1))
        d2 = MyEntry(name="b", value=3, color=(0.1, 0.0, 0.9))
        data = MyData(data_list=[d1, d2])
        with reraise_exceptions(), create_ui(data):
            pass
