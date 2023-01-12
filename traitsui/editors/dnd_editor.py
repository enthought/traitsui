# (C) Copyright 2004-2023 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

""" Defines the editor factory for a drag-and-drop editor. A drag-and-drop
    editor represents its value as a simple image which, depending upon the
    editor style, can be a drag source only, a drop target only, or both a
    drag source and a drop target.
"""

from pyface.ui_traits import Image

from traitsui.editor_factory import EditorFactory


class DNDEditor(EditorFactory):
    """Editor factory for drag-and-drop editors."""

    # -------------------------------------------------------------------------
    #  Trait definitions:
    # -------------------------------------------------------------------------

    #: The image to use for the target:
    image = Image

    #: The image to use when the target is disabled:
    disabled_image = Image


# This alias is deprecated and will be removed in TraitsUI 8.
ToolkitEditorFactory = DNDEditor
