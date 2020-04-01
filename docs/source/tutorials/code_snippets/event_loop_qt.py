from traits.api import HasTraits, Int
from pyface.qt.QtCore import QApplication


class Counter(HasTraits):
    value = Int()


Counter().edit_traits()
QApplication.instance().exec_()
