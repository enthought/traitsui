# (C) Copyright 2004-2023 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

""" A Traits UI editor for datetime.datetime objects.
"""


from pyface.qt import QtGui, is_pyside
from pyface.qt.QtCore import QDateTime
from traits.api import Datetime, observe

from .editor import Editor
from .editor_factory import ReadonlyEditor as BaseReadonlyEditor


class SimpleEditor(Editor):
    """Simple Traits UI time editor that wraps QDateTimeEdit."""

    #: the earliest datetime allowed by the editor
    minimum_datetime = Datetime(allow_none=True)

    #: the latest datetime allowed by the editor
    maximum_datetime = Datetime(allow_none=True)

    def init(self, parent):
        """Finishes initializing the editor by creating the underlying toolkit
        widget.
        """
        # set min and max early, don't wait for editor sync
        self.minimum_datetime = self.factory.minimum_datetime
        self.maximum_datetime = self.factory.maximum_datetime

        self.control = QtGui.QDateTimeEdit()
        self.update_minimum_datetime()
        self.update_maximum_datetime()
        self.control.dateTimeChanged.connect(self.update_object)

    def dispose(self):
        """Disposes of the contents of an editor."""
        if self.control is not None:
            self.control.dateTimeChanged.disconnect(self.update_object)
        super().dispose()

    def update_editor(self):
        """Updates the editor when the object trait changes externally to the
        editor.
        """
        value = self.value
        if value:
            if self.minimum_datetime and self.minimum_datetime > value:
                value = self.minimum_datetime
            elif self.maximum_datetime and self.value > self.maximum_datetime:
                value = self.maximum_datetime
            try:
                q_datetime = QDateTime(value)
            except Exception:
                pass
            self.control.setDateTime(q_datetime)
            self.value = value

    def update_object(self, q_datetime):
        """Handles the user entering input data in the edit control."""
        try:
            if is_pyside:
                self.value = q_datetime.toPython()
            else:
                self.value = q_datetime.toPyDateTime()
        except ValueError:
            pass

    @observe('minimum_datetime')
    def update_minimum_datetime(self, event=None):
        # sanity checking of values
        if (
            self.minimum_datetime is not None
            and self.maximum_datetime is not None
            and self.minimum_datetime > self.maximum_datetime
        ):
            self.maximum_datetime = self.minimum_datetime

        if self.control is not None:
            if self.minimum_datetime is not None:
                self.control.setMinimumDateTime(
                    QDateTime(self.minimum_datetime)
                )
            else:
                self.control.clearMinimumDateTime()

    @observe('maximum_datetime')
    def update_maximum_datetime(self, event=None):
        # sanity checking of values
        if (
            self.minimum_datetime is not None
            and self.maximum_datetime is not None
            and self.minimum_datetime > self.maximum_datetime
        ):
            self.minimum_datetime = self.maximum_datetime

        if self.control is not None:
            if self.maximum_datetime is not None:
                self.control.setMaximumDateTime(
                    QDateTime(self.maximum_datetime)
                )
            else:
                self.control.clearMaximumDateTime()


class ReadonlyEditor(BaseReadonlyEditor):
    """Readonly Traits UI time editor that uses a QLabel for the view."""

    def _get_str_value(self):
        """Replace the default string value with our own time version."""
        if not self.value:
            return self.factory.message
        else:
            return self.value.strftime(self.factory.strftime)
