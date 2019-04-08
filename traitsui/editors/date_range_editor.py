
from __future__ import absolute_import

from traits.api import Bool
from .date_editor import DateEditor


class ToolkitEditorFactory(DateEditor):
    """ Editor for a date range. The target value should be a tuple
    containing two dates (start date, end date)
    """

    # This must be set to true for setting a date range.
    multi_select = Bool(True)

    # Whether it is possible to unset the date range.
    allow_no_range = Bool(False)


DateRangeEditor = ToolkitEditorFactory
