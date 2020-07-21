from pyface.qt.QtCore import QCoreApplication

from traits.api import HasTraits, Int


class Counter(HasTraits):
    value = Int()


Counter().edit_traits()
QCoreApplication.instance().exec_()
