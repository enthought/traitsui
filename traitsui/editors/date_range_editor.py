
from __future__ import absolute_import

from traits.api import Bool
from .date_editor import DateEditor


class ToolkitEditorFactory(DateEditor):

    # Whether it is possible to unset the date range.
    allow_no_range = Bool(False)


DateRangeEditor = ToolkitEditorFactory
