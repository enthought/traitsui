import time

from pyface.qt import QtGui, QtCore

from traits.api import Instance, Int, Str
from traitsui.qt4.editor import Editor
from pyface.ui.qt4.progress_dialog import ProgressDialog

class _ProgressDialog(ProgressDialog):
    def close(self):
        """ Overwritten to disable closing.
        """
        pass


class SimpleEditor(Editor):
    """
    Show a progress bar with all the optional goodies

    """
    progress = Instance(_ProgressDialog)

    # The message to be displayed along side the progress guage
    message = Str

    # The starting value
    min = Int

    # The ending value
    max = Int

    #-- Editor interface ------------------------------------------------------

    def init ( self, parent ):
        """ Finishes initializing the editor by creating the underlying toolkit
            widget.
        """
        self.control = self.create_control( parent )
        factory = self.factory
        self.min = factory.min
        self.max = factory.max
        self.message = factory.message
        self.sync_value( factory.min_name,  'min',  'from' )
        self.sync_value( factory.max_name, 'max', 'from' )
        self.sync_value( factory.message_name, 'message', 'from' )
        
        self.set_tooltip()

    def create_control (self, parent):
        """
        Finishes initializing the editor by creating the underlying widget.
        """

        self.progress = _ProgressDialog( title=self.factory.title,
                                        message=self.factory.message,
                                        min=self.factory.min,
                                        max=self.factory.max,
                                        can_cancel=self.factory.can_cancel,
                                        show_time=self.factory.show_time,
                                        show_percent=self.factory.show_percent)

        control = QtGui.QWidget()
        self.control = control
        layout = QtGui.QVBoxLayout(self.control)
        layout.setContentsMargins(0, 0, 0, 0)

        # The 'guts' of the dialog.
        self.progress._create_message(control, layout)
        self.progress._create_gauge(control, layout)
        self.progress._create_percent(control, layout)
        self.progress._create_timer(control, layout)
        self.progress._create_buttons(control, layout)
        return self.control


    def update_editor ( self ):
        """
        Updates the editor when the object trait changes externally to the
        editor.
        """
        self.progress.min = self.min
        self.progress.max = self.max
        self.progress.message = self.message
        if self.value:
            self.progress.update(self.value)
        return

    def _min_changed ( self ):
        self.update_editor()

    def _max_changed ( self ):
        self.update_editor()

    def _message_changed ( self ):
        self.update_editor()
