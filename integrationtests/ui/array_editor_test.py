# (C) Copyright 2004-2022 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

# -------------------------------------------------------------------------
#  Imports:
# -------------------------------------------------------------------------

from traits.api import HasPrivateTraits, Array

from traitsui.api import View, ArrayEditor

# -------------------------------------------------------------------------
#  'Test' class:
# -------------------------------------------------------------------------


class Test(HasPrivateTraits):

    # -------------------------------------------------------------------------
    #  Trait definitions:
    # -------------------------------------------------------------------------

    three = Array(int, (3, 3))
    four = Array(float, (4, 4), editor=ArrayEditor(width=-50))

    # -------------------------------------------------------------------------
    #  Traits view definitions:
    # -------------------------------------------------------------------------

    view = View(
        'three',
        '_',
        'three',
        '_',
        'three~',
        '_',
        'four',
        '_',
        'four',
        '_',
        'four~',
        title='ArrayEditor Test Case',
        resizable=True,
    )


# -------------------------------------------------------------------------
#  Run the test case:
# -------------------------------------------------------------------------

if __name__ == '__main__':
    Test().configure_traits()
