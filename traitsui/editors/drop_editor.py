# (C) Copyright 2004-2023 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

""" Defines a drop editor factory for all traits toolkit backends.
    A drop target editor handles drag and drop operations as a drop
    target.
"""

from traits.api import Any, Bool

from traitsui.editors.text_editor import TextEditor


class DropEditor(TextEditor):
    """Editor factory for drop editors."""

    # -------------------------------------------------------------------------
    #  Trait definitions:
    # -------------------------------------------------------------------------

    #: Allowable drop objects must be of this class (optional)
    klass = Any()

    #: Must allowable drop objects be bindings?
    binding = Bool(False)

    #: Can the user type into the editor, or is it read only?
    readonly = Bool(True)


# This alias is deprecated and will be removed in TraitsUI 8.
ToolkitEditorFactory = DropEditor
