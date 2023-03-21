# (C) Copyright 2004-2023 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

""" Defines the Boolean editor factory for all traits toolkit backends.
"""
from traits.api import Dict, Str, Any

from traitsui.editors.text_editor import TextEditor
from traitsui.view import View

# -------------------------------------------------------------------------
#  Trait definitions:
# -------------------------------------------------------------------------

# Mapping from user input text to Boolean values
mapping_trait = Dict(
    Str,
    Any,
    {
        "True": True,
        "true": True,
        "t": True,
        "yes": True,
        "y": True,
        "False": False,
        "false": False,
        "f": False,
        "no": False,
        "n": False,
    },
)


class BooleanEditor(TextEditor):
    """Editor factory for Boolean editors."""

    # -------------------------------------------------------------------------
    #  Trait definitions:
    # -------------------------------------------------------------------------

    #: Dictionary mapping user input to other values.
    #: These definitions override definitions in the 'text_editor' version
    mapping = mapping_trait

    # -------------------------------------------------------------------------
    #  Traits view definition:
    # -------------------------------------------------------------------------

    traits_view = View()

    # -------------------------------------------------------------------------
    #  EditorFactory methods
    # -------------------------------------------------------------------------

    def _get_custom_editor_class(self):
        """Returns the editor class to use for "custom" style views.
        Overridden to return the simple_editor_class (instead of the
        CustomEditor class for the text editor's factory, which this class
        inherits from).

        """
        return self.simple_editor_class


# This alias is deprecated and will be removed in TraitsUI 8.
ToolkitEditorFactory = BooleanEditor
