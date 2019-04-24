#------------------------------------------------------------------------------
#
#  Copyright (c) 2006, Enthought, Inc.
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
#  Date:   01/05/2006
#
#------------------------------------------------------------------------------

""" Defines the tree-based Python value editor and the value editor factory,
    for the wxPython user interface toolkit.
"""

#-------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------

# FIXME: ToolkitEditorFactory is a proxy class defined here just for backward
# compatibility. The class has been moved to the
# traitsui.editors.value_editor file.
from __future__ import absolute_import
from traitsui.editors.value_editor \
    import _ValueEditor, ToolkitEditorFactory

from .editor import Editor


class SimpleEditor(_ValueEditor, Editor):
    """ Returns the editor to use for simple style views.
    """

    # Override the value of the readonly trait.
    readonly = False


class ReadonlyEditor(_ValueEditor, Editor):
    """ Returns the editor to use for readonly style views.
    """

    # Override the value of the readonly trait.
    readonly = True

### EOF #######################################################################
