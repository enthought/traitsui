# (C) Copyright 2004-2021 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

""" Defines the directory editor factory for all traits toolkit backends.
"""

from .file_editor import ToolkitEditorFactory as EditorFactory

# -------------------------------------------------------------------------
#  'ToolkitEditorFactory' class:
# -------------------------------------------------------------------------


class ToolkitEditorFactory(EditorFactory):
    """ Editor factory for directory editors.
    """

    pass


# Define the DirectoryEditor class
DirectoryEditor = ToolkitEditorFactory
