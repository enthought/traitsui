# (C) Copyright 2004-2023 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

""" Defines the set editor factory for all traits user interface toolkits.
"""

from traits.api import Bool, Str

from traitsui.editor_factory import EditorWithListFactory


class SetEditor(EditorWithListFactory):
    """Editor factory for editors for sets."""

    # -------------------------------------------------------------------------
    #  Trait definitions:
    # -------------------------------------------------------------------------

    #: Are the items in the set ordered (vs. unordered)?
    ordered = Bool(False)

    #: Can the user add and delete all items in the set at once?
    can_move_all = Bool(True)

    #: Title of left column:
    left_column_title = Str()

    #: Title of right column:
    right_column_title = Str()


# This alias is deprecated and will be removed in TraitsUI 8.
ToolkitEditorFactory = SetEditor
