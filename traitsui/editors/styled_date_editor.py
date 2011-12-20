
from traits.api import Bool, List, Str
from .date_editor import DateEditor

class CellFormat(object):
    """ Encapsulates some common visual attributes to set on the cells of a
    calendar widget.  All attributes default to None, which means that they
    will not override the existing values of the calendar widget.
    """

    italics = None
    bold = None
    underline = None

    # The color attributes should be strings representing color names,
    # from the list:
    #   red, green, blue, cyan, magenta, yellow, gray, white,
    #   darkRed, darkGreen, darkBlue, darkCyan, darkmagenta, darkYellow, darkGray,
    #   black, lightGray
    #
    # Alternatively, they can be a tuple of (R,G,B) values from 0-255.
    bgcolor = None
    fgcolor = None

    def __init__(self, **args):
        for key,val in args.items():
            setattr(self, key, val)


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
