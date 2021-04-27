# (C) Copyright 2004-2021 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

""" This module defines interaction objects that can be passed to
``UIWrapper.inspect`` where the actions represent 'queries'.

Implementations for these actions are expected to return value(s), ideally
without incurring side-effects.
"""


class SelectedText:
    """ An object representing an interaction to obtain the displayed (echoed)
    plain text which is currently selected.

    E.g. For a Enum List, with one entry currently selected, the displayed
    selected text would be the label of that entry.

    Implementations should return a ``str``, or None if nothing is selected.
    """
    pass


class DisplayedText:
    """ An object representing an interaction to obtain the displayed (echoed)
    plain text.

    E.g. For a textbox using a password styling, the displayed text should
    be a string of platform-dependent password mask characters.

    Implementations should return a ``str``.
    """
    pass


class IsChecked:
    """ An object representing an interaction to obtain whether a checkable
    widget (e.g. checkbox) is checked or not.

    Implementations should return True if checked and False if not.
    """
    pass


class IsEnabled:
    """ An object representing an interaction to obtain whether a widget is
    enabled or not.

    Implementations should return True if enabled and False if not.
    """
    pass


class IsVisible:
    """ An object representing an interaction to obtain whether a widget is
    visible or not.

    Implementations should return True if visible and False if not.
    """
    pass
