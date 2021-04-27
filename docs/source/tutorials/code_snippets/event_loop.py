# event_loop.py

from traits.api import *
from pyface.api import GUI

class Counter(HasTraits):
    value =  Int()

Counter().edit_traits()
GUI().start_event_loop()
