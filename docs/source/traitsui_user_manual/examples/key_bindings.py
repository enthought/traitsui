# (C) Copyright 2004-2022 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

# key_bindings.py -- Example of a code editor with a key bindings editor

from traits.api import Button, Code, HasPrivateTraits, observe, Str
from traitsui.api import Group, Handler, Item, View
from traitsui.key_bindings import KeyBinding, KeyBindings

key_bindings = KeyBindings(
    KeyBinding(
        binding1='Ctrl-s',
        description='Save to a file',
        method_name='save_file',
    ),
    KeyBinding(
        binding1='Ctrl-r',
        description='Run script',
        method_name='run_script',
    ),
    KeyBinding(
        binding1='Ctrl-k',
        description='Edit key bindings',
        # special method name handled internally
        method_name='edit_bindings',
    ),
)


class CodeHandler(Handler):
    """Handler class for bound methods."""

    def save_file(self, info):
        info.object.status = "save file"

    def run_script(self, info):
        info.object.status = "run script"


class KBCodeExample(HasPrivateTraits):

    code = Code()
    status = Str()
    kb = Button(label='Edit Key Bindings')

    view = View(
        Group(
            Item('code', style='custom', resizable=True),
            Item('status', style='readonly'),
            'kb',
            orientation='vertical',
            show_labels=False,
        ),
        id='KBCodeExample',
        key_bindings=key_bindings,
        title='Code Editor With Key Bindings',
        resizable=True,
        handler=CodeHandler(),
    )

    @observe('kb')
    def _edit_key_bindings(self, event):
        key_bindings.edit()


if __name__ == '__main__':
    KBCodeExample().configure_traits()
