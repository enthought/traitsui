#-------------------------------------------------------------------------
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
#  Date:   07/06/2006
#
#-------------------------------------------------------------------------

""" Define an editor that displays a string value as a title.
"""

#-------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------

from __future__ import absolute_import
from .editor \
    import Editor

from pyface.heading_text \
    import HeadingText

# FIXME: TitleEditor (the editor factory for title editors) is a proxy class
# defined here just for backward compatibility. The class has been moved to
# traitsui.editors.title_editor.
from traitsui.editors.title_editor \
    import TitleEditor


#-------------------------------------------------------------------------
#  '_TitleEditor' class:
#-------------------------------------------------------------------------

class _TitleEditor(Editor):

    #-------------------------------------------------------------------------
    #  Finishes initializing the editor by creating the underlying toolkit
    #  widget:
    #-------------------------------------------------------------------------

    def init(self, parent):
        """ Finishes initializing the editor by creating the underlying toolkit
            widget.
        """
        self._control = HeadingText(parent)
        self.control = self._control.control
        self.set_tooltip()

    #-------------------------------------------------------------------------
    #  Updates the editor when the object trait changes external to the editor:
    #-------------------------------------------------------------------------

    def update_editor(self):
        """ Updates the editor when the object trait changes external to the
            editor.
        """
        self._control.text = self.str_value


SimpleEditor = _TitleEditor
CustomEditor = _TitleEditor
ReadonlyEditor = _TitleEditor
TextEditor = _TitleEditor
