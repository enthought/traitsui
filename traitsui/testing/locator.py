import enum


class Cell:
    """ A location uniquely specified by a row index and a column index.

    Attributes
    ----------
    row : int
        0-based index
    column : int
        0-based index
    """

    def __init__(self, row, column):
        self.row = row
        self.column = column


class Index:
    """ A location uniquely specified by a single 0-based index.

    Attributes
    ----------
    index : int
        0-based index
    column : int
        0-based index
    """

    def __init__(self, index):
        self.index = index


class TreeNode:

    def __init__(self, row, column):
        self.row = row
        self.column = column


class WidgetType(enum.Enum):
    """ An Enum of widget types.
    """

    slider = "slider"
    textbox = "textbox"
    tabbar = "tabbar"


class TargetById:

    def __init__(self, id):
        self.id = id


class TargetByName:

    def __init__(self, name):
        self.name = name


class NestedUI:
    pass


class DefaultTarget:
    pass
