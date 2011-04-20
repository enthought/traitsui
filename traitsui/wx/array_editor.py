#------------------------------------------------------------------------------
#
#  Copyright (c) 2005, Enthought, Inc.
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
#  Date:   01/10/2006
#
#------------------------------------------------------------------------------

""" Defines array editors for the WX user interface toolkit.
"""

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

# FIXME: ToolkitEditorFactory is a proxy class defined here just for backward
# compatibility. The class has been moved to the
# traitsui.editors.array_editor file.
from traitsui.editors.array_editor \
    import SimpleEditor as BaseSimpleEditor, ToolkitEditorFactory

from editor \
    import Editor

#-------------------------------------------------------------------------------
#  'SimpleEditor' class:
#-------------------------------------------------------------------------------

class SimpleEditor ( BaseSimpleEditor, Editor ):
    """ Simple style of editor for arrays.
    """
    # FIXME: This class has been re-defined here simply so it inherits from the
    # wx Editor class.
    pass

#-------------------------------------------------------------------------------
#  'ReadonlyEditor' class:
#-------------------------------------------------------------------------------

class ReadonlyEditor(SimpleEditor):

    # Set the value of the readonly trait.
    readonly = True

### EOF #######################################################################
