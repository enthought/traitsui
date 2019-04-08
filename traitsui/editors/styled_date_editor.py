
from __future__ import absolute_import
from traits.api import Bool, List, Str
from .date_editor import CellFormat, DateEditor


class ToolkitEditorFactory(DateEditor):
    """ A DateEditor that can show sets of dates in different styles.
    """

    # The name of a dictionary on the object that maps names to groups
    # (list/tuples) of datetime.date objects.  Each of these groups can be
    # styled using the **styles** dict.
    dates_trait = Str()

    # The name of a dictionary on the object that maps names of styles to
    # CellFormat objects.  The names used must match the names used in the
    # **dates** dict.
    styles_trait = Str()

    # Allow selection of arbitrary dates in the past.
    allow_past = Bool(True)

    # Allow selection of arbitrary dates in the future.
    allow_future = Bool(True)

    # A list of strings that will be offered as an alternative to specifying
    # an absolute date, and instead specify a relative date.
    relative_dates = List()

StyledDateEditor = ToolkitEditorFactory
