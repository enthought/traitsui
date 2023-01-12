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
This program demonstrates the use of editors that support *history*. A
history is a persistent record of the last 'n' values the user has entered or
selected for a particular trait.

In order for the history to be recorded correctly, you must specify an *id*
for both the Item containing the history editor and the View containing the
Item.

The maximum number of history entries recorded is specified by the value of
the history editor's *entries* trait. If *entries* is less than or
equal to 0, then a normal, non-history, version of the editor will be used.

A history editor also attempts to restore the last value set as the current
value for the trait if the current value of the trait is the empty string. You
can see this for yourself by setting some values in the fields, selecting a
different demo, then reselecting this demo. Each field should have the same
value it had when the demo was run the previous time.
"""

# -- Imports --------------------------------------------------------------

from traits.api import HasTraits, Str, File, Directory

from traitsui.api import View, Item, FileEditor, DirectoryEditor, HistoryEditor

# -- HistoryDemo Class ----------------------------------------------------


class HistoryDemo(HasTraits):

    name = Str()
    file = File()
    directory = Directory()

    view = View(
        Item('name', id='name', editor=HistoryEditor(entries=5)),
        Item('file', id='file1', editor=FileEditor(entries=10)),
        Item(
            'file',
            id='file2',
            editor=FileEditor(
                entries=10,
                filter=['All files (*.*)|*.*', 'Python files (*.py)|*.py'],
            ),
        ),
        Item('directory', id='directory', editor=DirectoryEditor(entries=10)),
        title='History Editor Demo',
        id='enthought.test.history_demo.HistoryDemo',
        width=0.33,
        resizable=True,
    )


# Create the demo:
demo = HistoryDemo()

# Run the demo (if invoked from the command line):
if __name__ == '__main__':
    demo.configure_traits()
