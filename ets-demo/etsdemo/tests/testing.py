# (C) Copyright 2020 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

import unittest


def require_gui(func):
    """ Decorator for tests that require a non-null GUI toolkit.
    """
    # Defer GUI import side-effect.
    # The toolkit is not resolved until we import pyface.api
    from pyface.api import GUI
    try:
        GUI()
    except NotImplementedError:
        return unittest.skip("No GUI available.")(func)
    return func
