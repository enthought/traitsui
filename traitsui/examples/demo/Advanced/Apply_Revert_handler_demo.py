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
Apply / Revert

Provides support in a dialog box for an "Apply" button which modifies the
object being viewed, and a "Revert" button, which returns the object to its
starting state (before any "Apply").

Note that this does not automatically provide a full (multi-step incremental)
Undo capability.
"""

from traits.api import HasTraits, Str, List
from traitsui.api import Item, View, Handler, HGroup, VGroup, TextEditor


class ApplyRevert_Handler(Handler):
    def apply(self, info):
        print('apply called...')
        object = info.object
        object.stack.insert(0, object.input)
        object.queue.append(object.input)

    def revert(self, info):
        # Do something exciting here...
        print('revert called...')


class ApplyRevertDemo(HasTraits):

    # Trait definitions:
    input = Str()
    stack = List()
    queue = List()

    # Traits view definitions:
    traits_view = View(
        VGroup(
            VGroup(
                Item(
                    'input', show_label=False, editor=TextEditor(auto_set=True)
                ),
                label='Input',
                show_border=True,
            ),
            HGroup(
                VGroup(
                    Item(
                        'stack',
                        show_label=False,
                        height=50,
                        width=100,
                        style='readonly',
                    ),
                    label='Stack',
                    show_border=True,
                ),
                VGroup(
                    Item(
                        'queue',
                        show_label=False,
                        height=50,
                        width=100,
                        style='readonly',
                    ),
                    label='Queue',
                    show_border=True,
                ),
            ),
        ),
        resizable=True,
        height=300,
        title='Apply/Revert example',
        buttons=['Apply', 'Revert'],
        handler=ApplyRevert_Handler,
    )


# Create the demo:
modal_popup = ApplyRevertDemo()

# Run the demo (if invoked from the command line):
if __name__ == '__main__':
    modal_popup.configure_traits(kind='modal')
