# (C) Copyright 2004-2021 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

from pyface.image.image import *

from warnings import warn

warn(
    DeprecationWarning(
        "traitsui.image has been moved to pyface.image and will be removed in "
        "TraitsUI version 7.2 (originally intended to be removed in 6.0)"
    )
)
