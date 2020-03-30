# -------------------------------------------------------------------------
#
#  Copyright (c) 2005, Enthought, Inc.
#  All rights reserved.
#
#  This software is provided without warranty under the terms of the BSD
#  license included in LICENSE.txt and may be redistributed only
#  under the conditions described in the aforementioned license.  The license
#  is also available online at http://www.enthought.com/licenses/BSD.txt
#
#  Thanks for using Enthought open source!
#
#  Author: David C. Morrill
#  Date:   09/27/2005
#
# -------------------------------------------------------------------------

""" Editor that displays an interactive Python shell.
"""


# FIXME: ToolkitEditorFactory is a proxy class defined here just for backward
# compatibility. The class has been moved to the
# traitsui.editors.shell_editor file.
from traitsui.editors.shell_editor import (
    _ShellEditor as BaseShellEditor,
    ToolkitEditorFactory,
)

from .editor import Editor

# -------------------------------------------------------------------------
#  'ShellEditor' class:
# -------------------------------------------------------------------------


class _ShellEditor(BaseShellEditor, Editor):
    """ Editor that displays an interactive Python shell.
    """

    pass
