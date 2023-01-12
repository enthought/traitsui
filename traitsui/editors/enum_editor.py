# (C) Copyright 2004-2023 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

""" Defines the editor factory for single-selection enumerations, for all
traits user interface toolkits.
"""

import os
import sys

from traits.api import Any, Range, Enum, Bool, Str

from traitsui.editor_factory import EditorWithListFactory
from traitsui.toolkit import toolkit_object

# -------------------------------------------------------------------------
#  Trait definitions:
# -------------------------------------------------------------------------

#: Supported display modes for a custom style editor
Mode = Enum("radio", "list")

#: Supported display modes for a custom style editor
CompletionMode = Enum("inline", "popup")


class EnumEditor(EditorWithListFactory):
    """Editor factory for enumeration editors."""

    # -------------------------------------------------------------------------
    #  Trait definitions:
    # -------------------------------------------------------------------------

    #: (Optional) Function used to evaluate text input:
    evaluate = Any()

    #: Is user input set on every keystroke (when text input is allowed)?
    auto_set = Bool(True)

    #: Number of columns to use when displayed as a grid:
    cols = Range(1, 20)

    #: Display modes supported for a custom style editor:
    mode = Mode

    #: Completion mode for editors with text-entry (Qt only):
    completion_mode = CompletionMode

    #: Whether values trait contains separators (Qt only)
    use_separator = Bool(False)

    #: The separator string used in values trait (Qt only)
    separator = Str("")

    # -------------------------------------------------------------------------
    #  'Editor' factory methods:
    # -------------------------------------------------------------------------

    def _get_custom_editor_class(self):
        """Returns the editor class to use for "custom" style views.
        Overridden to return the editor class for the specified mode.
        """
        editor_file_name = os.path.basename(
            sys.modules[self.__class__.__module__].__file__
        )
        try:
            if self.mode == "radio":
                return toolkit_object(
                    editor_file_name.split(".")[0] + ":RadioEditor",
                    raise_exceptions=True,
                )
            else:
                return toolkit_object(
                    editor_file_name.split(".")[0] + ":ListEditor",
                    raise_exceptions=True,
                )
        except:
            return super()._get_custom_editor_class()


# This alias is deprecated and will be removed in TraitsUI 8.
ToolkitEditorFactory = EnumEditor
