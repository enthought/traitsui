# (C) Copyright 2004-2022 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

# default_trait_editors.py -- Example of using default trait editors

from traits.api import Bool, HasTraits, Range, Str
from traitsui.api import Item, View


class Adult(HasTraits):
    first_name = Str()
    last_name = Str()
    age = Range(21, 99)
    registered_voter = Bool()

    traits_view = View(
        Item(name='first_name'),
        Item(name='last_name'),
        Item(name='age'),
        Item(name='registered_voter'),
    )


alice = Adult(
    first_name='Alice',
    last_name='Smith',
    age=42,
    registered_voter=True,
)

alice.configure_traits()
