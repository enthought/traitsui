#------------------------------------------------------------------------------
#
#  Copyright (c) 2008, Enthought, Inc.
#  All rights reserved.
#
#  This software is provided without warranty under the terms of the BSD
#  license included in enthought/LICENSE.txt and may be redistributed only
#  under the conditions described in the aforementioned license.  The license
#  is also available online at http://www.enthought.com/licenses/BSD.txt
#
#  Thanks for using Enthought open source!
#
#  Author: David C. Morrill
#
#------------------------------------------------------------------------------

""" Defines the title editor factory for all traits toolkit backends.
"""

#-------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------

from __future__ import absolute_import

from traits.api import Bool
from ..editor_factory import EditorFactory
from ..toolkit import toolkit_object


class ToolkitEditorFactory(EditorFactory):
    """ Editor factory for Title editors.
    """

    allow_selection = Bool(False)

    def _get_simple_editor_class(self):
        """ Returns the editor class to use for "simple" style views.
        The default implementation tries to import the SimpleEditor class in the
        editor file in the backend package, and if such a class is not to found
        it returns the SimpleEditor class defined in editor_factory module in
        the backend package.

        """
        SimpleEditor = toolkit_object('title_editor:SimpleEditor')
        return SimpleEditor


#-------------------------------------------------------------------------
#  Create the editor factory object:
#-------------------------------------------------------------------------
TitleEditor = ToolkitEditorFactory

### EOF #######################################################################
