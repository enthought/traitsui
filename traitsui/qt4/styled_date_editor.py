
from pyface.qt import QtCore, QtGui
from pyface.qt.QtGui import QFont

from traits.api import Dict

# For a simple editor style, we just punt and use the same simple editor
# as in the default date_editor.
from date_editor import SimpleEditor
from date_editor import CustomEditor as DateCustomEditor


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
            [map(self._reset_formatting, dates) for dates in old.values()]
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
        [map(self._reset_formatting, dates) for dates in event.removed.values()]

    def _styles_changed(self, old, new):
        groups = getattr(self.object, self.factory.dates_trait, {})
        if not new:
            # If no new styles, then reset all the dates to a default style
            [map(self._reset_formatting, dates) for dates in groups.values()]
        else:
            self._apply_styles(new, groups)
        return

    def _styles_items_changed(self, event):
        groups = getattr(self.object, self.factory.dates_trait)
        styles = getattr(self.object, self.factory.styles_trait)

        names_to_update = event.added.keys() + event.changed.keys()
        modified_groups = dict((name, groups[name]) for name in names_to_update)
        self._apply_styles(styles, modified_groups)

        names_to_reset = event.removed.keys()
        for name in names_to_reset:
            self._reset_formatting(groups[name])
        return

    #------------------------------------------------------------------------
    # Helper functions
    #------------------------------------------------------------------------

    def _apply_style(self, style, dates):
        """ **style** is a CellFormat, **dates** is a list of datetime.date """
        for dt in dates:
            qdt = QtCore.QDate(dt)
            textformat = self.control.dateTextFormat(qdt)
            self._apply_cellformat(style, textformat)
            self.control.setDateTextFormat(qdt, textformat)
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
                qdt = QtCore.QDate(dt)
                textformat = self.control.dateTextFormat(qdt)
                self._apply_cellformat(cellformat, textformat)
                self.control.setDateTextFormat(qdt, textformat)
        return

    def _reset_formatting(self, dates):
        # Resets the text format on the given dates
        for dt in dates:
            qdt = QtCore.QDate(dt)
            self.control.setDateTextFormat(qdt, QtGui.QTextCharFormat())

    def _apply_cellformat(self, cf, textformat):
        """ Applies the formatting in the cellformat cf to the QTextCharFormat
        object provided.
        """
        if cf.italics is not None:
            textformat.setFontItalic(cf.italics)

        if cf.underline is not None:
            textformat.setFontUnderline(cf.underline)

        if cf.bold is not None:
            if cf.bold:
                weight = QFont.Bold
            else:
                weight = QFont.Normal
            textformat.setFontWeight(weight)

        if cf.bgcolor is not None:
            textformat.setBackground(self._color_to_brush(cf.bgcolor))

        if cf.fgcolor is not None:
            textformat.setForeground(self._color_to_brush(cf.fgcolor))

        return

    def _color_to_brush(self, color):
        """ Returns a QBrush with the color specified in **color** """
        brush = QtGui.QBrush()
        if isinstance(color, basestring) and hasattr(QtCore.Qt, color):
            col = getattr(QtCore.Qt, color)
        elif isinstance(color, tuple) and len(color) == 3:
            col = QtGui.QColor()
            col.setRgb(*color)
        else:
            raise RuntimeError("Invalid color specification '%r'" % color)

        brush.setColor(col)
        return brush

