# (C) Copyright 2004-2022 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

# enum_editor.py -- Example of using an enumeration editor

from traits.api import Enum, HasTraits
from traitsui.api import EnumEditor, Item, View


class EnumExample(HasTraits):
    priority = Enum('Medium', 'Highest', 'High', 'Low', 'Lowest')

    view = View(
        Item(
            name='priority',
            editor=EnumEditor(
                values={
                    'Highest': '1:Highest',
                    'High': '2:High',
                    'Medium': '3:Medium',
                    'Low': '4:Low',
                    'Lowest': '5:Lowest',
                }
            ),
        ),
    )


EnumExample().configure_traits()
