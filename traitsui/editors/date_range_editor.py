
from __future__ import absolute_import

from traits.api import Bool, Constant
from .date_editor import DateEditor


class ToolkitEditorFactory(DateEditor):
    """ Editor for a date range. The target value should be a tuple
    containing two dates (start date, end date)
    """

    # This must be set to true for setting a date range.
    multi_select = Constant(True)

    # Whether it is possible to unset the date range.
    # If true, then the date range will be set to (None, None)
    # when all the dates are unselected.
    allow_no_selection = Bool(False)


DateRangeEditor = ToolkitEditorFactory
