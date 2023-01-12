# (C) Copyright 2004-2023 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

""" Defines a completely empty editor, intended to be used as a spacer.
"""


from pyface.qt import QtGui

from .editor import Editor


class NullEditor(Editor):
    """A completely empty editor."""

    def init(self, parent):
        """Finishes initializing the editor by creating the underlying toolkit
        widget.
        """
        self.control = QtGui.QWidget()

    def update_editor(self):
        """Updates the editor when the object trait changes externally to the
        editor.
        """
        pass
