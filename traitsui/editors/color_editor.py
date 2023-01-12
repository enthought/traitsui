# (C) Copyright 2004-2023 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

""" Defines the color editor factory for the all traits toolkit backends.
"""

from traits.api import Bool

from traitsui.editor_factory import EditorFactory
from traitsui.toolkit import toolkit_object
from traitsui.view import View

# -------------------------------------------------------------------------
#  'ToolkitEditorFactory' class:
# -------------------------------------------------------------------------


class ToolkitEditorFactory(EditorFactory):
    """Editor factory for color editors."""

    # -------------------------------------------------------------------------
    #  Trait definitions:
    # -------------------------------------------------------------------------

    #: Is the underlying color trait mapped?
    mapped = Bool(True)

    #: Do we use a native dialog for the popup or the toolkit's?
    #: At present, only affects Qt.
    use_native_dialog = Bool(True)

    # -------------------------------------------------------------------------
    #  Traits view definition:
    # -------------------------------------------------------------------------

    traits_view = View(["mapped{Is value mapped?}", "|[]>"])


# Define the ColorEditor class
# The function will try to return the toolkit-specific editor factory (located
# in traitsui.<toolkit>.color_editor, and if none is found, the
# ToolkitEditorFactory declared here is returned.
def ColorEditor(*args, **traits):
    r"""Returns an instance of the toolkit-specific editor factory declared in
    traitsui.<toolkit>.color_editor. If such an editor factory
    cannot be located, an instance of the abstract ToolkitEditorFactory
    declared in traitsui.editors.color_editor is returned.

    Parameters
    ----------
    \*args, \*\*traits
        arguments and keywords to be passed on to the editor
        factory's constructor.
    """

    try:
        return toolkit_object("color_editor:ToolkitEditorFactory", True)(
            *args, **traits
        )
    except:
        return ToolkitEditorFactory(*args, **traits)
