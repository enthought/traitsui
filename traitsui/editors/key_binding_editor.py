# (C) Copyright 2004-2023 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

""" Defines the key binding editor for use with the KeyBinding class. This is a
specialized editor used to associate a particular key with a control (i.e., the
key binding editor).
"""

from traitsui.basic_editor_factory import BasicEditorFactory
from traitsui.toolkit import toolkit_object

# Callable which returns the editor to use in the ui.


def key_binding_editor(*args, **traits):
    return toolkit_object("key_binding_editor:KeyBindingEditor")(
        *args, **traits
    )


# -------------------------------------------------------------------------
#  Create the editor factory object:
# -------------------------------------------------------------------------
KeyBindingEditor = ToolkitEditorFactory = BasicEditorFactory(
    klass=key_binding_editor
)
