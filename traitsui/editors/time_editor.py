# (C) Copyright 2004-2023 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

""" A Traits UI editor that wraps a timer control.
"""

from traits.api import Str

from traitsui.editor_factory import EditorFactory
from traitsui.ui_traits import AView


class TimeEditor(EditorFactory):
    """Editor factory for time editors."""

    # -------------------------------------------------------------------------
    #  Trait definitions:
    # -------------------------------------------------------------------------

    # -- ReadonlyEditor traits ------------------------------------------------

    #: Message to show when Time is None.
    message = Str("Undefined")

    #: The string representation of the time to show.  Uses time.strftime
    #: format.
    strftime = Str("%I:%M:%S %p")

    #: An optional view to display when a read-only text editor is clicked:
    view = AView
