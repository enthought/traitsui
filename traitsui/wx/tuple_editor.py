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
#  Date:   12/13/2004
#
#------------------------------------------------------------------------------

""" Defines the tuple editor for the wxPython user interface toolkit.
"""

#-------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------


# FIXME: ToolkitEditorFactory is a proxy class defined here just for backward
# compatibility. The class has been moved to the
# traitsui.editors.tuple_editor file.
from __future__ import absolute_import
from traitsui.editors.tuple_editor \
    import SimpleEditor as BaseSimpleEditor, ToolkitEditorFactory

from .editor \
    import Editor

#-------------------------------------------------------------------------
#  'SimpleEditor' class:
#-------------------------------------------------------------------------


class SimpleEditor(BaseSimpleEditor, Editor):
    """ Simple style of editor for tuples.

        The editor displays an editor for each of the fields in the tuple,
        based on the type of each field.
    """
    pass

### EOF #######################################################################
