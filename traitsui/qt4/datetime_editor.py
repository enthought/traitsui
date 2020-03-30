#  Copyright (c) 2019, Enthought, Inc.
#  All rights reserved.
#
#  This software is provided without warranty under the terms of the BSD
#  license included in LICENSE.txt and may be redistributed only
#  under the conditions described in the aforementioned license.  The license
#  is also available online at http://www.enthought.com/licenses/BSD.txt
#
#  Thanks for using Enthought open source!
#
#  Author: Corran Webster
#  Date:   August 2019

""" A Traits UI editor for datetime.datetime objects.
"""


import datetime

from pyface.qt import QtGui
from pyface.qt.QtCore import QDateTime
from traits.api import Instance

from .editor import Editor
from .editor_factory import ReadonlyEditor as BaseReadonlyEditor


class SimpleEditor(Editor):
    """ Simple Traits UI time editor that wraps QDateTimeEdit.
    """

    #: the earliest datetime allowed by the editor
    minimum_datetime = Instance(datetime.datetime)

    #: the latest datetime allowed by the editor
    maximum_datetime = Instance(datetime.datetime)

    def init(self, parent):
        """ Finishes initializing the editor by creating the underlying toolkit
            widget.
        """
        self.control = QtGui.QDateTimeEdit()
        self.minimum_datetime = self.factory.minimum_datetime
        self.maximum_datetime = self.factory.maximum_datetime
        self.update_date_range()
        self.control.dateTimeChanged.connect(self.update_object)

    def update_editor(self):
        """ Updates the editor when the object trait changes externally to the
            editor.
        """
        value = self.value
        if value:
            q_datetime = QDateTime(value)
            self.control.setTime(q_datetime)

    def update_object(self, q_datetime):
        """ Handles the user entering input data in the edit control.
        """
        self.value = q_datetime.toPyDateTime()

    def update_date_range(self):
        if self.control is not None:
            if self.minimum_datetime is not None:
                self.control.setMinimumDateTime(
                   QDateTime(self.minimum_datetime)
                )
            if self.maximum_datetime is not None:
                self.control.setMaximumDateTime(
                    QDateTime(self.maximum_datetime)
                )


class ReadonlyEditor(BaseReadonlyEditor):
    """ Readonly Traits UI time editor that uses a QLabel for the view.
    """

    def _get_str_value(self):
        """ Replace the default string value with our own time version.
        """
        if not self.value:
            return self.factory.message
        else:
            return self.value.strftime(self.factory.strftime)
