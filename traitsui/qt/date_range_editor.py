# (C) Copyright 2004-2023 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

import datetime

from pyface.qt import QtCore, QtGui
from pyface.qt.QtGui import QFont

from traits.api import Dict

from .date_editor import CustomEditor as DateCustomEditor


class CustomEditor(DateCustomEditor):
    def init(self, parent):
        if not self.factory.multi_select:
            raise ValueError("multi_select must be true.")

        super().init(parent)

    def update_editor(self):
        """Updates the editor when the object trait changes externally to the
        editor.
        """
        start_date, end_date = self.value
        if start_date is not None and end_date is not None:
            self._apply_style_to_range(start_date, end_date)
        elif start_date is None and end_date is None:
            self.apply_unselected_style_to_all()
        else:
            raise ValueError(
                "The start and end dates must be either both defined or "
                "both be None. Got {!r}".format(self.value)
            )

    def update_object(self, q_date):
        """Handles the user entering input data in the edit control."""
        value = datetime.date(q_date.year(), q_date.month(), q_date.day())
        start_date, end_date = self.value

        if (
            self.factory.allow_no_selection
            and start_date is not None
            and end_date is not None
            and start_date < end_date
        ):
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
        self._apply_style_to_range(start_date, end_date)

    def _apply_style_to_range(self, start_date, end_date):
        num_days = (end_date - start_date).days + 1

        selected_dates = (
            start_date + datetime.timedelta(days=i) for i in range(num_days)
        )
        self.apply_unselected_style_to_all()
        for dt in selected_dates:
            self.select_date(dt)
