# ------------------------------------------------------------------------------
# Copyright (c) 2008, Enthought, Inc.
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

""" Defines the compound editor factory for all traits toolkit backends.
"""



from traits.api import Bool, List

from ..editor_factory import EditorFactory

# -------------------------------------------------------------------------
#  Trait definitions:
# -------------------------------------------------------------------------

# List of component editor factories used to build a compound editor
editors_trait = List(EditorFactory)

# -------------------------------------------------------------------------
#  'ToolkitEditorFactory' class:
# -------------------------------------------------------------------------


class ToolkitEditorFactory(EditorFactory):
    """ Editor factory for compound editors.
    """

    # -------------------------------------------------------------------------
    #  Trait definitions:
    # -------------------------------------------------------------------------

    #: Component editor factories used to build the editor
    editors = editors_trait

    #: Is user input set on every keystroke?
    auto_set = Bool(True)


# Define the CompoundEditor class
CompoundEditor = ToolkitEditorFactory
