# (C) Copyright 2004-2022 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

# mixed_styles.py -- Example of using editor styles at various levels

from traits.api import Enum, HasTraits, Str
from traitsui.api import Group, Item, View


class MixedStyles(HasTraits):
    first_name = Str()
    last_name = Str()

    department = Enum("Business", "Research", "Admin")
    position_type = Enum("Full-Time", "Part-Time", "Contract")

    traits_view = View(
        Group(
            Item(name='first_name'),
            Item(name='last_name'),
            Group(
                Item(name='department'),
                Item(name='position_type', style='custom'),
                style='simple',
            ),
        ),
        title='Mixed Styles',
        style='readonly',
    )


ms = MixedStyles(first_name='Sam', last_name='Smith')
ms.configure_traits()
