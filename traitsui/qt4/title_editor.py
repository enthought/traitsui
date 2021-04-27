# (C) Copyright 2009-2021 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

# ------------------------------------------------------------------------------
# Copyright (c) 2008, Riverbank Computing Limited
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD license.
# However, when used with the GPL version of PyQt the additional terms
# described in the PyQt GPL exception also apply

#
# Author: Riverbank Computing Limited
# ------------------------------------------------------------------------------



from pyface.qt import QtCore

from .editor import Editor

from pyface.heading_text import HeadingText


class SimpleEditor(Editor):
    def init(self, parent):
        """ Finishes initializing the editor by creating the underlying toolkit
            widget.
        """
        self._control = HeadingText(None)
        self.control = self._control.control
        if self.factory.allow_selection:
            flags = (
                self.control.textInteractionFlags()
                | QtCore.Qt.TextSelectableByMouse
            )
            self.control.setTextInteractionFlags(flags)
        self.set_tooltip()

    def update_editor(self):
        """ Updates the editor when the object trait changes external to the
            editor.
        """
        self._control.text = self.str_value


CustomEditor = SimpleEditor
ReadonlyEditor = SimpleEditor
TextEditor = SimpleEditor
