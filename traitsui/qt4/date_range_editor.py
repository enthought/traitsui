
from __future__ import absolute_import

import datetime

from pyface.qt import QtCore, QtGui
from pyface.qt.QtGui import QFont

from traits.api import Dict

from .date_editor import CustomEditor as DateCustomEditor
import six
from six.moves import map


class CustomEditor(DateCustomEditor):

    def init(self, parent):
        if not self.factory.multi_select:
            raise ValueError("multi_select must be true.")

        super(CustomEditor, self).init(parent)

    def update_object(self, q_date):
        """ Handles the user entering input data in the edit control.
        """
        value = datetime.date(q_date.year(), q_date.month(), q_date.day())
        start_date, end_date = self.value

        if (self.factory.allow_no_range and
                start_date is not None and
                end_date is not None and
                value >= start_date and
                value <= end_date):
            self.value = (None, None)
            self.apply_unselected_style_to_all()
            return

        if start_date is None:
            start_date = value

        if end_date is None:
            end_date = value

        if start_date != end_date:
            start_date = value
            end_date = value

        elif value > start_date:
            end_date = value

        else:
            start_date = value

        self.value = (start_date, end_date)
        num_days = (end_date - start_date).days + 1

        selected_dates = [
            start_date + datetime.timedelta(days=i)
            for i in range(num_days)
        ]
        self.apply_unselected_style_to_all()
        for dt in selected_dates:
            self.select_date(dt)
