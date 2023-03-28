# (C) Copyright 2008-2023 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

# ------------------------------------------------------------------------------
# Copyright (c) 2007, Riverbank Computing Limited
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD license.
# However, when used with the GPL version of PyQt the additional terms
# described in the PyQt GPL exception also apply

#
# Author: Riverbank Computing Limited
# ------------------------------------------------------------------------------

""" Defines the PyQt implementation of the editor used to wrap a non-Traits
based custom control.
"""


from pyface.qt import QtGui

from .editor import Editor

# -------------------------------------------------------------------------
#  'CustomEditor' class:
# -------------------------------------------------------------------------


class CustomEditor(Editor):
    """Wrapper for a custom editor control"""

    # -------------------------------------------------------------------------
    #  Finishes initializing the editor by creating the underlying toolkit
    #  widget:
    # -------------------------------------------------------------------------

    def init(self, parent):
        """Finishes initializing the editor by creating the underlying toolkit
        widget.
        """
        factory = self.factory.factory
        if factory is not None:
            self.control = factory(*((parent, self) + self.factory.args))
        if self.control is None:
            self.control = QtGui.QLabel(
                "An error occurred creating a custom editor.\n"
                "Please contact the developer."
            )
            self.control.setStyleSheet("background-color: red; color: white")
        self.set_tooltip()

    # -------------------------------------------------------------------------
    #  Updates the editor when the object trait changes external to the editor:
    # -------------------------------------------------------------------------

    def update_editor(self):
        """Updates the editor when the object trait changes externally to the
        editor.
        """
        pass
