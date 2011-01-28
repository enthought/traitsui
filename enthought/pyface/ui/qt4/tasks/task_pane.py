# Enthought library imports.
from enthought.pyface.tasks.i_task_pane import MTaskPane
from enthought.traits.api import Bool, Property

# System library imports.
from enthought.qt import QtGui


class TaskPane(MTaskPane):
    """ The toolkit-specific implementation of a TaskPane.

    See the ITaskPane interface for API documentation.
    """

    #### 'ITaskPane' interface ################################################

    has_focus = Property(Bool)

    ###########################################################################
    # 'ITaskPane' interface.
    ###########################################################################

    def create(self, parent):
        """ Create and set the toolkit-specific control that represents the
            pane.
        """
        self.control = QtGui.QWidget(parent)

    def destroy(self):
        """ Destroy the toolkit-specific control that represents the pane.
        """
        if self.control is not None:
            self.control.hide()
            self.control.deleteLater()
            self.control = None

    def set_focus(self):
        """ Gives focus to the control that represents the pane.
        """
        if self.control is not None:
            self.control.setFocus()

    ###########################################################################
    # Protected interface.
    ###########################################################################

    def _get_has_focus(self):
        if self.control is not None:
            return self.control.hasFocus()
        return False
