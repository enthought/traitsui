# (C) Copyright 2004-2023 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

""" Defines the title editor factory for all traits toolkit backends.
"""

from traits.api import Bool

from traitsui.editor_factory import EditorFactory
from traitsui.toolkit import toolkit_object


class TitleEditor(EditorFactory):
    """Editor factory for Title editors."""

    allow_selection = Bool(False)

    def _get_simple_editor_class(self):
        """Returns the editor class to use for "simple" style views.
        The default implementation tries to import the SimpleEditor class in
        the editor file in the backend package, and if such a class is not to
        found it returns the SimpleEditor class defined in editor_factory
        module in the backend package.

        """
        SimpleEditor = toolkit_object("title_editor:SimpleEditor")
        return SimpleEditor


# This alias is deprecated and will be removed in TraitsUI 8.
ToolkitEditorFactory = TitleEditor
