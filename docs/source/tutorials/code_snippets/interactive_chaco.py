from traits.api import *
from traitsui.api import View, Item, ButtonEditor

class Counter(HasTraits):
    value =  Int()
    add_one = Button()

    def _add_one_fired(self):
        self.value +=1

    view = View('value', Item('add_one', show_label=False ))

Counter().configure_traits()