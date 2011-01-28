#------------------------------------------------------------------------------
# Copyright (c) 2007, Riverbank Computing Limited
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD license.
# However, when used with the GPL version of PyQt the additional terms described in the PyQt GPL exception also apply

#
# Author: Riverbank Computing Limited
# Description: <Enthought pyface package component>
#------------------------------------------------------------------------------


# Major package imports.
from enthought.qt import QtCore, QtGui

# Enthought library imports.
from enthought.traits.api import Bool, Enum, implements, Int, Str, Unicode

# Local imports.
from enthought.pyface.i_dialog import IDialog, MDialog
from enthought.pyface.constant import OK, CANCEL, YES, NO
from window import Window


# Map PyQt dialog related constants to the pyface equivalents.
_RESULT_MAP = {
    QtGui.QDialog.Accepted:     OK,
    QtGui.QDialog.Rejected:     CANCEL,
    QtGui.QMessageBox.Ok:       OK,
    QtGui.QMessageBox.Cancel:   CANCEL,
    QtGui.QMessageBox.Yes:      YES,
    QtGui.QMessageBox.No:       NO
}


class Dialog(MDialog, Window):
    """ The toolkit specific implementation of a Dialog.  See the IDialog
    interface for the API documentation.
    """

    implements(IDialog)

    #### 'IDialog' interface ##################################################

    cancel_label = Unicode

    help_id = Str

    help_label = Unicode

    ok_label = Unicode

    resizeable = Bool(True)

    return_code = Int(OK)

    style = Enum('modal', 'nonmodal')

    #### 'IWindow' interface ##################################################

    title = Unicode("Dialog")

    ###########################################################################
    # Protected 'IDialog' interface.
    ###########################################################################

    def _create_buttons(self, parent):
        buttons = QtGui.QDialogButtonBox()

        # 'OK' button.
        if self.ok_label:
            btn = buttons.addButton(self.ok_label,
                                    QtGui.QDialogButtonBox.AcceptRole)
        else:
            btn = buttons.addButton(QtGui.QDialogButtonBox.Ok)

        btn.setDefault(True)
        QtCore.QObject.connect(btn, QtCore.SIGNAL('clicked()'),
                               self.control, QtCore.SLOT('accept()'))

        # 'Cancel' button.
        if self.cancel_label:
            btn = buttons.addButton(self.cancel_label,
                                    QtGui.QDialogButtonBox.RejectRole)
        else:
            btn = buttons.addButton(QtGui.QDialogButtonBox.Cancel)

        QtCore.QObject.connect(btn, QtCore.SIGNAL('clicked()'),
                               self.control, QtCore.SLOT('reject()'))

        # 'Help' button.
        # FIXME v3: In the original code the only possible hook into the help
        # was to reimplement self._on_help().  However this was a private
        # method.  Obviously nobody uses the Help button.  For the moment we
        # display it but can't actually use it.
        if len(self.help_id) > 0:
            if self.help_label:
                buttons.addButton(self.help_label, QtGui.QDialogButtonBox.HelpRole)
            else:
                buttons.addButton(QtGui.QDialogButtonBox.Help)

        return buttons

    def _create_contents(self, parent):
        layout = QtGui.QVBoxLayout()

        if not self.resizeable:
            layout.setSizeConstraint(QtGui.QLayout.SetFixedSize)

        layout.addWidget(self._create_dialog_area(parent))
        layout.addWidget(self._create_buttons(parent))

        parent.setLayout(layout)

    def _create_dialog_area(self, parent):
        panel = QtGui.QWidget(parent)
        panel.setMinimumSize(QtCore.QSize(100, 200))

        palette = panel.palette()
        palette.setColor(QtGui.QPalette.Window, QtGui.QColor('red'))
        panel.setPalette(palette)
        panel.setAutoFillBackground(True)

        return panel

    def _show_modal(self):
        self.control.setWindowModality(QtCore.Qt.ApplicationModal)
        retval = self.control.exec_()
        return _RESULT_MAP[retval]

    ###########################################################################
    # Protected 'IWidget' interface.
    ###########################################################################

    def _create_control(self, parent):
        dlg = QtGui.QDialog(parent)

        # Setting return code and firing close events is handled for 'modal' in
        # MDialog's open method. For 'nonmodal', we do it here.
        if self.style == 'nonmodal':
            QtCore.QObject.connect(dlg, QtCore.SIGNAL('finished(int)'),
                                   self._finished_fired)

        if self.size != (-1, -1):
            dlg.resize(*self.size)

        dlg.setWindowTitle(self.title)

        return dlg

    ###########################################################################
    # Private interface.
    ###########################################################################

    def _finished_fired(self, result):
        """ Called when the dialog is closed (and nonmodal). """

        self.return_code = _RESULT_MAP[result]
        self.close()

#### EOF ######################################################################
