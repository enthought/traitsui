# (C) Copyright 2004-2023 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

from traits.api import Bool, Constant

from traitsui.editors.date_editor import DateEditor


class DateRangeEditor(DateEditor):
    """Editor for a date range. The target value should be a tuple
    containing two dates (start date, end date)
    """

    #: This must be set to true for setting a date range.
    multi_select = Constant(True)

    #: Whether it is possible to unset the date range.
    #: If true, then the date range will be set to (None, None)
    #: when all the dates are unselected.
    allow_no_selection = Bool(False)


# This alias is deprecated and will be removed in TraitsUI 8.
ToolkitEditorFactory = DateRangeEditor
