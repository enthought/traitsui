# event_loop_qt.py

from pyface.qt.QtGui import QApplication

from traits.api import HasTraits, Int


class Counter(HasTraits):
    value = Int()


Counter().edit_traits()
QApplication.instance().exec_()
