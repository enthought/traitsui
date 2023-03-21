# (C) Copyright 2004-2023 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

""" Defines the font editor factory for all traits user interface toolkits.
"""

from traitsui.editor_factory import EditorFactory
from traitsui.toolkit import toolkit_object

# -------------------------------------------------------------------------
#  'ToolkitEditorFactory' class:
# -------------------------------------------------------------------------


class ToolkitEditorFactory(EditorFactory):
    """Editor factory for font editors."""

    pass


# Define the FontEditor class
# The function will try to return the toolkit-specific editor factory (located
# in traitsui.<toolkit>.font_editor, and if none is found, the
# ToolkitEditorFactory declared here is returned.
def FontEditor(*args, **traits):
    r"""Returns an instance of the toolkit-specific editor factory declared in
    traitsui.<toolkit>.font_editor. If such an editor factory
    cannot be located, an instance of the abstract ToolkitEditorFactory
    declared in traitsui.editors.font_editor is returned.

    Parameters
    ----------
    \*args, \*\*traits
        arguments and keywords to be passed on to the editor
        factory's constructor.
    """

    try:
        return toolkit_object("font_editor:ToolkitEditorFactory", True)(
            *args, **traits
        )
    except Exception:
        return ToolkitEditorFactory(*args, **traits)
