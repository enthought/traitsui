#  Copyright (c) 2007, Enthought, Inc.
#  License: BSD Style.

# wizard.py ---Example of a traits-based wizard UI

from traits.api import HasTraits, Str
from traits.etsconfig.api import ETSConfig
from traitsui.api import Item, View, VGroup


class Person(HasTraits):
    first_name = Str()
    last_name = Str()

    company = Str()
    position = Str()

    view = View(
        VGroup(
            Item("first_name"),
            Item("last_name"),
            # label="Personal info"
        ),
        VGroup(
            Item("company"),
            Item("position"),
            # label="Professional info"
        )

    )


person = Person(first_name='Postman', last_name='Pat', company="Enthought",
                position="Software Developer")


if ETSConfig.toolkit == "wx":
    # Wizard window is currently only available for wx backend.
    person.configure_traits(kind='wizard')
