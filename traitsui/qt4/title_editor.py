#------------------------------------------------------------------------------
# Copyright (c) 2008, Riverbank Computing Limited
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD license.
# However, when used with the GPL version of PyQt the additional terms
# described in the PyQt GPL exception also apply

#
# Author: Riverbank Computing Limited
#------------------------------------------------------------------------------

#-------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------

from __future__ import absolute_import

from pyface.qt import QtCore

from .editor import Editor

from pyface.heading_text import HeadingText

# FIXME: ToolkitEditorFactory is a proxy class defined here just for backward
# compatibility. The class has been moved to the
# traitsui.editors.title_editor file.
from ..editors.title_editor import TitleEditor


class SimpleEditor(Editor):

    #-------------------------------------------------------------------------
    #  Finishes initializing the editor by creating the underlying toolkit
    #  widget:
    #-------------------------------------------------------------------------

    def init(self, parent):
        """ Finishes initializing the editor by creating the underlying toolkit
            widget.
        """
        self._control = HeadingText(None)
        self.control = self._control.control
        if self.factory.allow_selection:
            flags = (self.control.textInteractionFlags() |
                     QtCore.Qt.TextSelectableByMouse)
            self.control.setTextInteractionFlags(flags)
        self.set_tooltip()

    #-------------------------------------------------------------------------
    #  Updates the editor when the object trait changes external to the editor:
    #-------------------------------------------------------------------------

    def update_editor(self):
        """ Updates the editor when the object trait changes external to the
            editor.
        """
        self._control.text = self.str_value

CustomEditor = SimpleEditor
ReadonlyEditor = SimpleEditor
TextEditor = SimpleEditor
