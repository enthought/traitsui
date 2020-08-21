#  Copyright (c) 2005-2020, Enthought, Inc.
#  All rights reserved.
#
#  This software is provided without warranty under the terms of the BSD
#  license included in LICENSE.txt and may be redistributed only
#  under the conditions described in the aforementioned license.  The license
#  is also available online at http://www.enthought.com/licenses/BSD.txt
#
#  Thanks for using Enthought open source!
#

""" This module defines interaction objects that can be passed to
``UIWrapper.perform`` where the actions represent 'commands'.

Implementations for these actions are expected to produce the
documented side effects without returning any values.
"""


class MouseClick:
    """ An object representing the user clicking a mouse button.
    Currently the left mouse button is assumed.

    In most circumstances, a widget can still be clicked on even if it is
    disabled. Therefore unlike key events, if the widget is disabled,
    implementations should not raise an exception.
    """
    pass
