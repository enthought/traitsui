# (C) Copyright 2004-2023 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

""" Editor that displays an interactive Python shell.
"""


from traitsui.editors.shell_editor import _ShellEditor as BaseShellEditor

from .editor import Editor

# -------------------------------------------------------------------------
#  'ShellEditor' class:
# -------------------------------------------------------------------------


class _ShellEditor(BaseShellEditor, Editor):
    """Editor that displays an interactive Python shell."""

    pass
