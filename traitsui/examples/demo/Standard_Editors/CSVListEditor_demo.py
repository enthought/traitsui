# (C) Copyright 2004-2023 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

"""
Demonstrate the CSVListEditor class.

This editor allows the user to enter a *single* line of input text, containing
comma-separated values (or another separator may be specified). Your program
specifies an element Trait type of Int, Float, Str, Enum, or Range.

Please refer to the `CSVListEditor API docs`_ for further information.

.. _CSVListEditor API docs: https://docs.enthought.com/traitsui/api/traitsui.editors.csv_list_editor.html#traitsui.editors.csv_list_editor.CSVListEditor
"""

from traits.api import (
    HasTraits,
    List,
    Int,
    Float,
    Enum,
    Range,
    Str,
    Button,
    Property,
    observe,
)
from traitsui.api import (
    View,
    Item,
    Label,
    Heading,
    VGroup,
    HGroup,
    UItem,
    spring,
    TextEditor,
    CSVListEditor,
)


class CSVListEditorDemo(HasTraits):

    list1 = List(Int)

    list2 = List(Float)

    list3 = List(Str, maxlen=3)

    list4 = List(Enum('red', 'green', 'blue', 2, 3))

    list5 = List(Range(low=0.0, high=10.0))

    # 'low' and 'high' are used to demonstrate lists containing dynamic ranges.
    low = Float(0.0)
    high = Float(1.0)

    list6 = List(Range(low=-1.0, high='high'))

    list7 = List(Range(low='low', high='high'))

    pop1 = Button("Pop from first list")

    sort1 = Button("Sort first list")

    # This will be str(self.list1).
    list1str = Property(Str, observe='list1')

    traits_view = View(
        HGroup(
            # This VGroup forms the column of CSVListEditor examples.
            VGroup(
                Item(
                    'list1',
                    label="List(Int)",
                    editor=CSVListEditor(ignore_trailing_sep=False),
                    tooltip='options: ignore_trailing_sep=False',
                ),
                Item(
                    'list1',
                    label="List(Int)",
                    style='readonly',
                    editor=CSVListEditor(),
                ),
                Item(
                    'list2',
                    label="List(Float)",
                    editor=CSVListEditor(enter_set=True, auto_set=False),
                    tooltip='options: enter_set=True, auto_set=False',
                ),
                Item(
                    'list3',
                    label="List(Str, maxlen=3)",
                    editor=CSVListEditor(),
                ),
                Item(
                    'list4',
                    label="List(Enum('red', 'green', 'blue', 2, 3))",
                    editor=CSVListEditor(sep=None),
                    tooltip='options: sep=None',
                ),
                Item(
                    'list5',
                    label="List(Range(low=0.0, high=10.0))",
                    editor=CSVListEditor(),
                ),
                Item(
                    'list6',
                    label="List(Range(low=-1.0, high='high'))",
                    editor=CSVListEditor(),
                ),
                Item(
                    'list7',
                    label="List(Range(low='low', high='high'))",
                    editor=CSVListEditor(),
                ),
                springy=True,
            ),
            # This VGroup forms the right column; it will display the
            # Python str representation of the lists.
            VGroup(
                UItem(
                    'list1str',
                    editor=TextEditor(),
                    enabled_when='False',
                    width=240,
                ),
                UItem(
                    'list1str',
                    editor=TextEditor(),
                    enabled_when='False',
                    width=240,
                ),
                UItem(
                    'list2',
                    editor=TextEditor(),
                    enabled_when='False',
                    width=240,
                ),
                UItem(
                    'list3',
                    editor=TextEditor(),
                    enabled_when='False',
                    width=240,
                ),
                UItem(
                    'list4',
                    editor=TextEditor(),
                    enabled_when='False',
                    width=240,
                ),
                UItem(
                    'list5',
                    editor=TextEditor(),
                    enabled_when='False',
                    width=240,
                ),
                UItem(
                    'list6',
                    editor=TextEditor(),
                    enabled_when='False',
                    width=240,
                ),
                UItem(
                    'list7',
                    editor=TextEditor(),
                    enabled_when='False',
                    width=240,
                ),
            ),
        ),
        '_',
        HGroup('low', 'high', spring, UItem('pop1'), UItem('sort1')),
        Heading("Notes"),
        Label(
            "Hover over a list to see which editor options are set, " "if any."
        ),
        Label(
            "The editor of the first list, List(Int), uses "
            "ignore_trailing_sep=False, so a trailing comma is "
            "an error."
        ),
        Label("The second list is a read-only view of the first list."),
        Label(
            "The editor of the List(Float) example has enter_set=True "
            "and auto_set=False; press Enter to validate."
        ),
        Label("The List(Str) example will accept at most 3 elements."),
        Label(
            "The editor of the List(Enum(...)) example uses sep=None, "
            "i.e. whitespace acts as a separator."
        ),
        Label(
            "The last three List(Range(...)) examples take neither, one or "
            "both of their limits from the Low and High fields below."
        ),
        width=720,
        title="CSVListEditor Demonstration",
    )

    def _list1_default(self):
        return [1, 4, 0, 10]

    def _get_list1str(self):
        return str(self.list1)

    @observe("pop1")
    def _pop_from_list1(self, event):
        if len(self.list1) > 0:
            x = self.list1.pop()
            print(x)

    @observe('sort1')
    def _sort_list1(self, event):
        self.list1.sort()


if __name__ == "__main__":
    demo = CSVListEditorDemo()
    demo.configure_traits()
