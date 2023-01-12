# (C) Copyright 2009-2023 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

# ------------------------------------------------------------------------------
# Copyright (c) 2008, Riverbank Computing Limited
# All rights reserved.
#
#  This software is provided without warranty under the terms of the BSD
#  license included in LICENSE.txt and may be redistributed only
#  under the conditions described in the aforementioned license.  The license
#  is also available online at http://www.enthought.com/licenses/BSD.txt
#
#  Thanks for using Enthought open source!
#
#  Author: David C. Morrill
#
# ------------------------------------------------------------------------------

""" Defines the editor factory for multi-selection enumerations, for all traits
toolkit backends.
"""

from traits.api import Range

from traitsui.editor_factory import EditorWithListFactory


class CheckListEditor(EditorWithListFactory):
    """Editor factory for checklists."""

    # -------------------------------------------------------------------------
    #  Trait definitions:
    # -------------------------------------------------------------------------

    #: Number of columns to use when the editor is displayed as a grid
    cols = Range(1, 20)


# This alias is deprecated and will be removed in TraitsUI 8.
ToolkitEditorFactory = CheckListEditor
