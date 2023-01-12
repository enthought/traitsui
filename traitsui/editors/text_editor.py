# (C) Copyright 2004-2023 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

""" Defines the text editor factory for all traits toolkit backends.
"""

from traits.api import Dict, Str, Any, Bool

from traitsui.editor_factory import EditorFactory
from traitsui.group import Group
from traitsui.ui_traits import AView
from traitsui.view import View

# -------------------------------------------------------------------------
#  Define a simple identity mapping:
# -------------------------------------------------------------------------


class _Identity(object):
    """A simple identity mapping."""

    def __call__(self, value):
        return value


# -------------------------------------------------------------------------
#  Trait definitions:
# -------------------------------------------------------------------------

#: Mapping from user input text to other value
mapping_trait = Dict(Str, Any)

#: Function used to evaluate textual user input
evaluate_trait = Any(_Identity())


class TextEditor(EditorFactory):
    """Editor factory for text editors."""

    # -------------------------------------------------------------------------
    #  Trait definitions:
    # -------------------------------------------------------------------------

    #: Dictionary that maps user input to other values
    mapping = mapping_trait

    #: Is user input set on every keystroke?
    auto_set = Bool(True)

    #: Is user input set when the Enter key is pressed?
    enter_set = Bool(False)

    #: Is multi-line text allowed?
    multi_line = Bool(True)

    #: Is editor readonly (will use custom / default editor appearance with
    #: readonly flag set to true) in contrast with readonly style for item
    #: when completely another editor is used
    read_only = Bool(False)

    #: Is user input unreadable? (e.g., for a password)
    password = Bool(False)

    #: Function to evaluate textual user input
    evaluate = evaluate_trait

    #: The object trait containing the function used to evaluate user input
    evaluate_name = Str()

    #: The optional view to display when a read-only text editor is clicked:
    view = AView

    #: In a read-only text editor, allow selection and copying of the text.
    readonly_allow_selection = Bool(True)

    #: Grayed-out placeholder text to be displayed when the editor is empty.
    placeholder = Str()

    #: Whether or not to display a clear button for the text.  This only works
    #: in the qt>=5.2 backend for simple/text styles of the editor.  Note this
    #: trait is currently provisional and may be replaced in the future by a
    #: more general feature.
    cancel_button = Bool(False)

    # -------------------------------------------------------------------------
    #  Traits view definition:
    # -------------------------------------------------------------------------

    traits_view = View(
        [
            "auto_set{Set value when text is typed}",
            "enter_set{Set value when enter is pressed}",
            "multi_line{Allow multiple lines of text}",
            "<extras>",
            "|options:[Options]>",
        ]
    )

    extras = Group("password{Is this a password field?}")


# This alias is deprecated and will be removed in TraitsUI 8.
ToolkitEditorFactory = TextEditor
