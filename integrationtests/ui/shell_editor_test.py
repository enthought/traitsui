# (C) Copyright 2004-2022 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

from traits.api import Dict, Float, HasPrivateTraits, Int, Str
from traitsui.api import Item, ShellEditor, View

# -------------------------------------------------------------------------
#  'ShellTest' class:
# -------------------------------------------------------------------------


class ShellTest(HasPrivateTraits):

    # -------------------------------------------------------------------------
    #  Trait definitions:
    # -------------------------------------------------------------------------

    name = Str()
    age = Int()
    weight = Float()
    shell_1 = Str()
    shell_2 = Dict()

    # -------------------------------------------------------------------------
    #  Traits view definitions:
    # -------------------------------------------------------------------------

    view = View(
        'name',
        'age',
        'weight',
        '_',
        Item('shell_1', editor=ShellEditor()),
        Item('shell_2', editor=ShellEditor()),
        id='traitsui.tests.shell_editor_test',
        resizable=True,
        width=0.3,
        height=0.3,
    )


# -------------------------------------------------------------------------
#  Run the test:
# -------------------------------------------------------------------------

if __name__ == '__main__':
    ShellTest().configure_traits()
