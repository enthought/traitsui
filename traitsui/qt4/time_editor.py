#------------------------------------------------------------------------------
#
#  Copyright (c) 2009, Enthought, Inc.
#  All rights reserved.
#
#  This software is provided without warranty under the terms of the BSD
#  license included in enthought/LICENSE.txt and may be redistributed only
#  under the conditions described in the aforementioned license.  The license
#  is also available online at http://www.enthought.com/licenses/BSD.txt
#
#  Thanks for using Enthought open source!
#
#  Author: Evan Patterson
#  Date:   08/04/2009
#
#------------------------------------------------------------------------------

""" A Traits UI editor for datetime.time objects.
"""

#-------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------

from __future__ import absolute_import, print_function

import datetime

from pyface.qt import QtCore, QtGui

from .editor import Editor
from .editor_factory import ReadonlyEditor as BaseReadonlyEditor

#-------------------------------------------------------------------------
#  'SimpleEditor' class:
#-------------------------------------------------------------------------


class SimpleEditor(Editor):
    """ Simple Traits UI time editor that wraps QTimeEdit.
    """

    #-------------------------------------------------------------------------
    #  Finishes initializing the editor by creating the underlying toolkit
    #  widget:
    #-------------------------------------------------------------------------

    def init(self, parent):
        """ Finishes initializing the editor by creating the underlying toolkit
            widget.
        """
        self.control = QtGui.QTimeEdit()

        self.control.timeChanged.connect(self.update_object)

    #-------------------------------------------------------------------------
    #  Updates the editor when the object trait changes external to the editor:
    #-------------------------------------------------------------------------

    def update_editor(self):
        """ Updates the editor when the object trait changes externally to the
            editor.
        """
        value = self.value
        if value:
            q_date = QtCore.QTime(value.hour, value.minute, value.second)
            self.control.setTime(q_date)

    #-------------------------------------------------------------------------
    #  Handles the user entering input data in the edit control:
    #-------------------------------------------------------------------------

    def update_object(self, q_time):
        """ Handles the user entering input data in the edit control.
        """
        hour = q_time.hour()
        minute = q_time.minute()
        second = q_time.second()
        try:
            self.value = datetime.time(hour, minute, second)
        except ValueError:
            print('Invalid time:', hour, minute, second)
            raise

#------------------------------------------------------------------------------
# 'ReadonlyEditor' class:
#------------------------------------------------------------------------------


class ReadonlyEditor(BaseReadonlyEditor):
    """ Readonly Traits UI time editor that uses a QLabel for the view.
    """

    def _get_str_value(self):
        """ Replace the default string value with our own time verision.
        """
        if not self.value:
            return self.factory.message
        else:
            return self.value.strftime(self.factory.strftime)
