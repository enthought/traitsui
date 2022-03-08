# interactive.py

from traits.api import HasTraits, Int, Button, observe
from traitsui.api import View, Item, ButtonEditor


class Counter(HasTraits):
    value = Int()
    add_one = Button()

    @observe('add_one')
    def _increment_value(self, event):
        self.value += 1

    view = View('value', Item('add_one', show_label=False))


Counter().configure_traits()
