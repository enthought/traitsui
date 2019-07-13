#-------------------------------------------------------------------------
#
#  Copyright (c) 2007, Enthought, Inc.
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
#  Date:   03/02/2007
#
#-------------------------------------------------------------------------

""" Traits UI 'display only' LED numeric editor.
"""

#-------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------

from __future__ import absolute_import
from wx.gizmos \
    import LEDNumberCtrl, LED_ALIGN_LEFT, LED_ALIGN_CENTER, LED_ALIGN_RIGHT

from traits.api \
    import Enum

from traitsui.wx.editor \
    import Editor

from traitsui.basic_editor_factory \
    import BasicEditorFactory

#-------------------------------------------------------------------------
#  Constants:
#-------------------------------------------------------------------------

# LED alignment styles:
LEDStyles = {
    'left': LED_ALIGN_LEFT,
    'center': LED_ALIGN_CENTER,
    'right': LED_ALIGN_RIGHT,
}

#-------------------------------------------------------------------------
#  '_LEDEditor' class:
#-------------------------------------------------------------------------


class _LEDEditor(Editor):
    """ Traits UI 'display only' LED numeric editor.
    """

    #-------------------------------------------------------------------------
    #  Finishes initializing the editor by creating the underlying toolkit
    #  widget:
    #-------------------------------------------------------------------------

    def init(self, parent):
        """ Finishes initializing the editor by creating the underlying toolkit
            widget.
        """
        self.control = LEDNumberCtrl(parent, -1)
        self.control.SetAlignment(LEDStyles[self.factory.alignment])
        self.set_tooltip()

    #-------------------------------------------------------------------------
    #  Updates the editor when the object trait changes external to the editor:
    #-------------------------------------------------------------------------

    def update_editor(self):
        """ Updates the editor when the object trait changes externally to the
            editor.
        """
        self.control.SetValue(self.str_value)

#-------------------------------------------------------------------------
#  Create the editor factory object:
#-------------------------------------------------------------------------

# wxPython editor factory for LED editors:


class LEDEditor(BasicEditorFactory):

    # The editor class to be created:
    klass = _LEDEditor

    # The alignment of the numeric text within the control:
    alignment = Enum('right', 'left', 'center')
