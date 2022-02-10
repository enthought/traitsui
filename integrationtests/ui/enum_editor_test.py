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

from traits.api import HasTraits, Trait, Enum, Range

from traitsui.api import View, Item, EnumEditor

# -------------------------------------------------------------------------
#  Trait definitions:
# -------------------------------------------------------------------------

values = ['one', 'two', 'three', 'four']
enum = Enum(*values)
range = Range(1, 4)

# -------------------------------------------------------------------------
#  'TestEnumEditor' class:
# -------------------------------------------------------------------------


class TestEnumEditor(HasTraits):

    # -------------------------------------------------------------------------
    #  Trait definitions:
    # -------------------------------------------------------------------------
    value = Trait(1, enum, range)

    other_value = Range(0, 4)

    trait_view = View(
        Item('value', editor=EnumEditor(values=values, evaluate=int)),
        Item('other_value'),
        resizable=True,
    )


# -------------------------------------------------------------------------
#  Run the test:
# -------------------------------------------------------------------------

if __name__ == '__main__':
    test = TestEnumEditor()
    test.configure_traits()
    test.print_traits()
