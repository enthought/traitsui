
from __future__ import absolute_import
from pyface.qt import QtCore, QtGui
from pyface.qt.QtGui import QFont

from traits.api import Dict

# For a simple editor style, we just punt and use the same simple editor
# as in the default date_editor.
from .date_editor import SimpleEditor
from .date_editor import CustomEditor as DateCustomEditor
import six
from six.moves import map


class CustomEditor(DateCustomEditor):

    dates = Dict()

    styles = Dict()

    def init(self, parent):
        self.control = QtGui.QCalendarWidget()

        if not self.factory.allow_future:
            self.control.setMaximumDate(QtCore.QDate.currentDate())

        if not self.factory.allow_past:
            self.control.setMinimumDate(QtCore.QDate.currentDate())

        if self.factory.dates_trait and self.factory.styles_trait:
            self.sync_value(self.factory.dates_trait, "dates", "from")
            self.sync_value(self.factory.styles_trait, "styles", "from")

        self.control.clicked.connect(self.update_object)

        return

    def _dates_changed(self, old, new):
        # Someone changed out the entire dict.  The easiest, most robust
        # way to handle this is to reset the text formats of all the dates
        # in the old dict, and then set the dates in the new dict.
        if old:
            [list(map(self._reset_formatting, dates)) for dates in old.values()]
        if new:
            styles = getattr(self.object, self.factory.styles_trait, None)
            self._apply_styles(styles, new)

    def _dates_items_changed(self, event):
        # Handle the added and changed items
        groups_to_set = event.added
        groups_to_set.update(event.changed)
        styles = getattr(self.object, self.factory.styles_trait, None)
        self._apply_styles(styles, groups_to_set)

        # Handle the removed items by resetting them
        [list(map(self._reset_formatting, dates))
         for dates in event.removed.values()]

    def _styles_changed(self, old, new):
        groups = getattr(self.object, self.factory.dates_trait, {})
        if not new:
            # If no new styles, then reset all the dates to a default style
            [list(map(self._reset_formatting, dates)) for dates in groups.values()]
        else:
            self._apply_styles(new, groups)
        return

    def _styles_items_changed(self, event):
        groups = getattr(self.object, self.factory.dates_trait)
        styles = getattr(self.object, self.factory.styles_trait)

        names_to_update = list(event.added.keys()) + list(event.changed.keys())
        modified_groups = dict((name, groups[name])
                               for name in names_to_update)
        self._apply_styles(styles, modified_groups)

        names_to_reset = list(event.removed.keys())
        for name in names_to_reset:
            self._reset_formatting(groups[name])
        return

    #------------------------------------------------------------------------
    # Helper functions
    #------------------------------------------------------------------------

    def _apply_style(self, style, dates):
        """ **style** is a CellFormat, **dates** is a list of datetime.date """
        for dt in dates:
            self.set_unselected_style(style, date)
        return

    def _apply_styles(self, style_dict, date_dict):
        """ Applies the proper style out of style_dict to every (name,date_list)
        in date_dict.
        """
        if not style_dict or not date_dict:
            return
        for groupname, dates in date_dict.items():
            cellformat = style_dict.get(groupname, None)
            if not cellformat:
                continue
            for dt in dates:
                self.set_unselected_style(cellformat, dt)
        return

    def _reset_formatting(self, dates):
        # Resets the text format on the given dates
        for dt in dates:
            self.apply_unselected_style(date)
