from pyface.qt import QtGui
from traitsui.qt4.editor import Editor
from traitsui.basic_editor_factory import BasicEditorFactory
from traits.api import undefined


class _LEDEditor(Editor):

    def init(self, parent):
        self.control = QtGui.QLCDNumber()
        self.control.setSegmentStyle(QtGui.QLCDNumber.Flat)
        self.set_tooltip()

    def update_editor(self):
        self.control.display(self.str_value)


class LEDEditor(BasicEditorFactory):

    #: The editor class to be created
    klass = _LEDEditor
    # Alignment is not supported for QT backend
    alignment = undefined
