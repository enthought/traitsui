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


from traits.api import Enum, List

from traitsui.api import Handler, View, Item, CheckListEditor

# -------------------------------------------------------------------------
#  Constants:
# -------------------------------------------------------------------------

colors = ['red', 'orange', 'yellow', 'green', 'blue', 'indigo', 'violet']

numbers = [
    'one',
    'two',
    'three',
    'four',
    'five',
    'six',
    'seven',
    'eight',
    'nine',
    'ten',
]

# -------------------------------------------------------------------------
#  'CheckListTest' class:
# -------------------------------------------------------------------------


class CheckListTest(Handler):

    # -------------------------------------------------------------------------
    #  Trait definitions:
    # -------------------------------------------------------------------------

    case = Enum('Colors', 'Numbers')
    value = List(editor=CheckListEditor(values=colors, cols=5))

    # -------------------------------------------------------------------------
    #  Event handlers:
    # -------------------------------------------------------------------------

    def object_case_changed(self, info):
        if self.case == 'Colors':
            info.value.factory.values = colors
        else:
            info.value.factory.values = numbers


# -------------------------------------------------------------------------
#  Run the tests:
# -------------------------------------------------------------------------

if __name__ == '__main__':
    clt = CheckListTest()
    clt.configure_traits(view=View('case', '_', Item('value', id='value')))
    print('value:', clt.value)
    clt.configure_traits(view=View('case', '_', Item('value@', id='value')))
    print('value:', clt.value)
