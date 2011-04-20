import wx

from traits.api import Instance
from traitsui.wx.editor import Editor
from pyface.ui.wx.progress_dialog import ProgressDialog

class SimpleEditor(Editor):
    """
    Show a progress bar with all the optional goodies

    """

    progress = Instance(ProgressDialog)

    #-- Editor interface ------------------------------------------------------

    def init ( self, parent ):
        """ Finishes initializing the editor by creating the underlying toolkit
            widget.
        """
        self.control = self.create_control( parent )
        self.set_tooltip()

    def create_control (self, parent):
        """
        Finishes initializing the editor by creating the underlying widget.
        """

        self.progress = ProgressDialog( title=self.factory.title,
                                        message=self.factory.message,
                                        min=self.factory.min,
                                        max=self.factory.max,
                                        can_cancel=self.factory.can_cancel,
                                        show_time=self.factory.show_time,
                                        show_percent=self.factory.show_percent)

        panel = wx.Panel(parent, -1)

        sizer = wx.BoxSizer(wx.VERTICAL)
        panel.SetSizer(sizer)
        panel.SetAutoLayout(True)
        panel.SetBackgroundColour(wx.NullColor)

        self.progress.dialog_size = wx.Size()

        # The 'guts' of the dialog.
        self.progress._create_message(panel, sizer)
        self.progress._create_gauge(panel, sizer)
        self.progress._create_percent(panel, sizer)
        self.progress._create_timer(panel, sizer)
        self.progress._create_buttons(panel, sizer)

        panel.SetClientSize(self.progress.dialog_size)

        panel.CentreOnParent()

        self.control = panel
        return self.control


    def update_editor ( self ):
        """
        Updates the editor when the object trait changes externally to the
        editor.
        """
        if self.value:
            self.progress.update(self.value)
        return
