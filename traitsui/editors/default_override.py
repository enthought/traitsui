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
Editor factory that overrides certain attributes of the default editor.

For example, the default editor for Range(low=0, high=1500) has
'1500' as the upper label.  To change it to 'Max' instead, use

my_range = Range(low=0, high=1500,
                 editor=DefaultOverride(high_label='Max'))

Alternatively, the override can also be specified in the view:

View(Item('my_range', editor=DefaultOverride(high_label='Max'))

"""

from traits.api import Dict

from traitsui.editor_factory import EditorFactory


class DefaultOverride(EditorFactory):
    """Editor factory for selectively overriding certain parameters
    of the default editor.

    """

    _overrides = Dict()

    def __init__(self, *args, **overrides):
        EditorFactory.__init__(self, *args)
        self._overrides = overrides

    def _customise_default(
        self, editor_kind, ui, object, name, description, parent
    ):
        """
        Obtain the given trait's default editor and set the parameters
        specified in `overrides` above.
        """
        trait = object.trait(name)
        editor_factory = trait.trait_type.create_editor()
        for option in self._overrides:
            setattr(editor_factory, option, self._overrides[option])

        editor = getattr(editor_factory, editor_kind)(
            ui, object, name, description, parent
        )
        return editor

    def simple_editor(self, ui, object, name, description, parent):
        return self._customise_default(
            "simple_editor", ui, object, name, description, parent
        )

    def custom_editor(self, ui, object, name, description, parent):
        return self._customise_default(
            "custom_editor", ui, object, name, description, parent
        )

    def text_editor(self, ui, object, name, description, parent):
        return self._customise_default(
            "text_editor", ui, object, name, description, parent
        )

    def readonly_editor(self, ui, object, name, description, parent):
        return self._customise_default(
            "readonly_editor", ui, object, name, description, parent
        )
