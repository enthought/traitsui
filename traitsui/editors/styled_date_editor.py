# (C) Copyright 2004-2023 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

from traits.api import Bool, List, Str

from traitsui.editors.date_editor import DateEditor


class StyledDateEditor(DateEditor):
    """A DateEditor that can show sets of dates in different styles."""

    #: The name of a dictionary on the object that maps names to groups
    #: (list/tuples) of datetime.date objects.  Each of these groups can be
    #: styled using the **styles** dict.
    dates_trait = Str()

    #: The name of a dictionary on the object that maps names of styles to
    #: CellFormat objects.  The names used must match the names used in the
    #: **dates** dict.
    styles_trait = Str()

    #: Allow selection of arbitrary dates in the past.
    allow_past = Bool(True)

    #: Allow selection of arbitrary dates in the future.
    allow_future = Bool(True)

    #: A list of strings that will be offered as an alternative to specifying
    #: an absolute date, and instead specify a relative date.
    relative_dates = List()


# This alias is deprecated and will be removed in TraitsUI 8.
ToolkitEditorFactory = StyledDateEditor
