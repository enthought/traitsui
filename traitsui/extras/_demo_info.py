# (C) Copyright 2004-2023 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

""" This module provides the metadata to contribute example files for
the ETS demo application.
"""

import pkg_resources


def info(request):
    """Return a configuration for contributing demo examples to the
    Demo application.

    Parameters
    ----------
    request : dict
        Information provided by the demo application.
        Currently this is a placeholder.

    Returns
    -------
    response : dict
    """
    return dict(
        version=1,
        name="TraitsUI Demo",
        root=pkg_resources.resource_filename("traitsui", "examples/demo"),
    )
