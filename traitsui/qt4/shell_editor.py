#-------------------------------------------------------------------------
#
#  Copyright (c) 2011, Enthought, Inc.
#  All rights reserved.
#
#  This software is provided without warranty under the terms of the BSD
#  license included in enthought/LICENSE.txt and may be redistributed only
#  under the conditions described in the aforementioned license.  The license
#  is also available online at http://www.enthought.com/licenses/BSD.txt
#
#  Thanks for using Enthought open source!
#
#-------------------------------------------------------------------------

""" Editor that displays an interactive Python shell.
"""

#-------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------

# FIXME: ToolkitEditorFactory is a proxy class defined here just for backward
# compatibility. The class has been moved to the
# traitsui.editors.shell_editor file.
from __future__ import absolute_import
from traitsui.editors.shell_editor import \
    _ShellEditor as BaseShellEditor

from .editor import Editor

#-------------------------------------------------------------------------
#  'ShellEditor' class:
#-------------------------------------------------------------------------


class _ShellEditor(BaseShellEditor, Editor):
    """ Editor that displays an interactive Python shell.
    """

    def init(self, parent):
        super(_ShellEditor, self).init(None)
