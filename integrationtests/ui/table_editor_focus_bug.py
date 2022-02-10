# (C) Copyright 2004-2022 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

from traits.api import HasTraits, Str, List
from traitsui.api import Group, Item, TableEditor, View
from traitsui.table_column import ObjectColumn


class Word(HasTraits):
    word = Str()


class Foo(HasTraits):

    # arbitrary string containing spaces
    input = Str()

    # input split on space
    parsed = List()

    def _input_changed(self):
        words = self.input.split()

        for word in self.parsed[:]:
            if word.word in words:
                words.remove(word.word)
            else:
                self.parsed.remove(word)

        for word in words:
            self.parsed.append(Word(word=word))

        return

    table_editor = TableEditor(
        columns=[ObjectColumn(name='word')], editable=True
    )

    help = Str(
        """Type in the 'input' box before clicking the Parsed tab.
The first non-whitespace character will cause changes to the parsed trait
and therefore changes to the table rows.  That is expected.

BUG: the table grabs the focus from 'input' and thus subsequent typing goes
into one of the table cells.

If you click the 'Parsed' tab, to view the table, and then the 'Inputs' tab
the focus will stay with the 'input' box.
"""
    )

    traits_view = View(
        Group(Item('help', style='readonly'), Item('input'), label='Input'),
        Group(Item('parsed', editor=table_editor), label='Parsed'),
        dock='tab',
        resizable=True,
        width=320,
        height=240,
    )


if __name__ == '__main__':

    # simple test of the model
    foo = Foo()
    foo.input = 'these words in the list'
    assert [word.word for word in foo.parsed] == [
        'these',
        'words',
        'in',
        'the',
        'list',
    ]
    foo.input = 'these dudes in the bar'
    assert [word.word for word in foo.parsed] == [
        'these',
        'in',
        'the',
        'dudes',
        'bar',
    ]

    foo.configure_traits(kind='modal')
    print(foo.input, [word.word for word in foo.parsed])
