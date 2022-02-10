# (C) Copyright 2004-2022 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

# wizard.py -- Example of a traits-based wizard UI

from traits.api import HasTraits, Str
from traits.etsconfig.api import ETSConfig
from traitsui.api import Item, View, VGroup


class Person(HasTraits):
    first_name = Str()
    last_name = Str()

    company = Str()
    position = Str()

    view = View(
        VGroup(Item("first_name"), Item("last_name")),
        VGroup(Item("company"), Item("position")),
    )


person = Person(
    first_name='Postman',
    last_name='Pat',
    company="Enthought",
    position="Software Developer",
)


if ETSConfig.toolkit == "wx":
    # Wizard window is currently only available for wx backend.
    person.configure_traits(kind='wizard')
