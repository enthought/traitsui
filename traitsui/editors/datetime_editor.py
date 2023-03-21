# (C) Copyright 2004-2023 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

""" A Traits UI editor
"""

import datetime

from traits.api import Datetime, Str

from traitsui.editor_factory import EditorFactory


class DatetimeEditor(EditorFactory):
    """Editor factory for the datetime editor."""

    # -------------------------------------------------------------------------
    #  Trait definitions:
    # -------------------------------------------------------------------------

    #: The earliest datetime allowed by the editor
    minimum_datetime = Datetime(datetime.datetime(100, 1, 1), allow_none=True)

    #: The latest datetime allowed by the editor
    maximum_datetime = Datetime(datetime.datetime.max, allow_none=True)

    # -- ReadonlyEditor traits ------------------------------------------------

    #: Message to show when datetime is None.
    message = Str("Undefined")

    #: The string representation of the datetime to show.  Uses time.strftime
    #: format.
    strftime = Str("%Y-%m-%dT%H:%M:%S")
