# Test for TextEditor 'invalid' trait.
#
# Look for:
#
#   background color should be correctly to the error indicating color
#     whenever the name is invalid (all whitespace).  In particular:
#
#   background color should be set at initialization.

from traits.api import Bool, HasTraits, Property, Str
from traitsui.api import Item, View
from traitsui.api import TextEditor


class Person(HasTraits):
    name = Str

    invalid = Property(Bool, depends_on='name')

    def _get_invalid(self):
        # Name is valid iff it doesn't consist entirely of whitespace.
        stripped_name = self.name.strip()
        return stripped_name == ''

    traits_view = View(
        Item('name', editor=TextEditor(invalid='invalid')),
    )


if __name__ == '__main__':
    Person().configure_traits()
