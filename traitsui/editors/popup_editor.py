# (C) Copyright 2004-2022 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

from traits.api import Float, Enum, Any, Property

from traitsui.basic_editor_factory import BasicEditorFactory
from traitsui.editor_factory import EditorFactory
from traitsui.editors.text_editor import TextEditor
from traitsui.item import Item
from traitsui.toolkit import toolkit_object
from traitsui.ui_editor import UIEditor
from traitsui.ui_traits import EditorStyle
from traitsui.view import View

# -------------------------------------------------------------------------
#  '_PopupEditor' class:
# -------------------------------------------------------------------------


class _PopupEditor(UIEditor):
    def init_ui(self, parent):
        """Creates the traits UI for the editor."""
        return self.object.edit_traits(view=self.base_view(), parent=parent)

    def base_view(self):
        """Returns the View that allows the popup view to be displayed."""
        return View(
            Item(
                self.name,
                show_label=False,
                style="readonly",
                editor=TextEditor(view=self.popup_view()),
                padding=-4,
            ),
            kind="subpanel",
        )

    def popup_view(self):
        """Returns the popup View."""
        factory = self.factory
        item = Item(
            self.name,
            show_label=False,
            padding=-4,
            style=factory.style,
            height=factory.height,
            width=factory.width,
        )

        editor = factory.editor
        if editor is not None:
            if not isinstance(editor, EditorFactory):
                editor = editor()
            item.editor = editor

        return View(item, kind=factory.kind)


# -------------------------------------------------------------------------
#  'PopupEditor' class:
# -------------------------------------------------------------------------


class PopupEditor(BasicEditorFactory):

    #: The class used to construct editor objects:
    klass = Property()

    #: The kind of popup to use:
    kind = Enum("popover", "popup", "info")

    #: The editor to use for the pop-up view (can be None (use default editor),
    #: an EditorFactory instance, or a callable that returns an EditorFactory
    #: instance):
    editor = Any()

    #: The style of editor to use for the popup editor (same as Item.style):
    style = EditorStyle

    #: The height of the popup (same as Item.height):
    height = Float(-1.0)

    #: The width of the popup (same as Item.width):
    width = Float(-1.0)

    def _get_klass(self):
        """The class used to construct editor objects."""
        return toolkit_object("popup_editor:_PopupEditor")
