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


from traits.api import Enum, List, Str

from traitsui.api import Handler, View, Item, CheckListEditor

# -------------------------------------------------------------------------
#  'CheckListTest' class:
# -------------------------------------------------------------------------


class CheckListTest(Handler):

    # -------------------------------------------------------------------------
    #  Trait definitions:
    # -------------------------------------------------------------------------

    value = List(editor=CheckListEditor(name='values', cols=5))
    values = List(Str)
    values_text = Str('red orange yellow green blue indigo violet')

    # -------------------------------------------------------------------------
    #  Traits view definitions:
    # -------------------------------------------------------------------------

    simple_view = View('value', 'values_text@')
    custom_view = View('value@', 'values_text@')

    # -------------------------------------------------------------------------
    #  'Initializes the object:
    # -------------------------------------------------------------------------

    def __init__(self, **traits):
        super().__init__(**traits)
        self._values_text_changed()

    # -------------------------------------------------------------------------
    #  Event handlers:
    # -------------------------------------------------------------------------

    def _values_text_changed(self):
        self.values = self.values_text.split()


# -------------------------------------------------------------------------
#  Run the tests:
# -------------------------------------------------------------------------

if __name__ == '__main__':
    clt = CheckListTest()
    clt.configure_traits(view='simple_view')
    print('value:', clt.value)
    clt.configure_traits(view='custom_view')
    print('value:', clt.value)
