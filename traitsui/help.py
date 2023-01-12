# (C) Copyright 2004-2023 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

""" Defines the help interface for displaying the help associated with a
    Traits UI View object.
"""


from .toolkit import toolkit


def default_show_help(info, control):
    """Default handler for showing the help associated with a view."""
    toolkit().show_help(info.ui, control)


# The default handler for showing help
show_help = default_show_help


def on_help_call(new_show_help=None):
    """Sets a new global help provider function.

    The help provider function must have a signature of
    *function*(*info*, *control*), where *info* is a UIInfo object for the
    current view, and *control* is the UI control that invokes the function
    (typically, a **Help** button). It is provided in case the help provider
    needs to position the help window relative to the **Help** button.

    To retrieve the current help provider function, call this function with
    no arguments.

    Parameters
    ----------
    new_show_help : function
        The function to set as the new global help provider

    Returns
    -------
    previous : callable
        The previous global help provider function
    """
    global show_help

    result = show_help
    if new_show_help is not None:
        show_help = new_show_help
    return result
