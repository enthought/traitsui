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
from PyQt4 import QtCore, QtGui

# Enthought library imports.
from enthought.traits.api import Bool, Dict, Enum, implements, Instance, Unicode

# Local imports.
from enthought.pyface.i_confirmation_dialog import IConfirmationDialog, MConfirmationDialog
from enthought.pyface.constant import CANCEL, YES, NO
from enthought.pyface.image_resource import ImageResource
from dialog import Dialog


class ConfirmationDialog(MConfirmationDialog, Dialog):
    """ The toolkit specific implementation of a ConfirmationDialog.  See the
    IConfirmationDialog interface for the API documentation.
    """

    implements(IConfirmationDialog)

    #### 'IConfirmationDialog' interface ######################################

    cancel = Bool(False)

    default = Enum(NO, YES, CANCEL)

    image = Instance(ImageResource)

    message = Unicode
    
    informative = Unicode
    
    detail = Unicode

    no_label = Unicode

    yes_label = Unicode

    # If we create custom buttons with the various roles, then we need to 
    # keep track of the buttons so we can see what the user clicked.  It's
    # not correct nor sufficient to check the return result from QMessageBox.exec_().
    # (As of Qt 4.5.1, even clicking a button with the YesRole would lead to
    # exec_() returning QDialog.Rejected.
    _button_result_map = Dict()

    ###########################################################################
    # Protected 'IDialog' interface.
    ###########################################################################

    def _create_contents(self, parent):
        # In PyQt this is a canned dialog.
        pass

    ###########################################################################
    # Protected 'IWidget' interface.
    ###########################################################################

    def _create_control(self, parent):
        dlg = QtGui.QMessageBox(parent)

        dlg.setWindowTitle(self.title)
        dlg.setText(self.message)
        dlg.setInformativeText(self.informative)
        dlg.setDetailedText(self.detail)

        if self.image is None:
            dlg.setIcon(QtGui.QMessageBox.Warning)
        else:
            dlg.setIconPixmap(self.image.create_image())

        # The 'Yes' button.
        if self.yes_label:
            btn = dlg.addButton(self.yes_label, QtGui.QMessageBox.YesRole)
        else:
            btn = dlg.addButton(QtGui.QMessageBox.Yes)
        self._button_result_map[btn] = YES

        if self.default == YES:
            dlg.setDefaultButton(btn)

        # The 'No' button.
        if self.no_label:
            btn = dlg.addButton(self.no_label, QtGui.QMessageBox.NoRole)
        else:
            btn = dlg.addButton(QtGui.QMessageBox.No)
        self._button_result_map[btn] = NO

        if self.default == NO:
            dlg.setDefaultButton(btn)

        # The 'Cancel' button.
        if self.cancel:
            if self.cancel_label:
                btn = dlg.addButton(self.cancel_label, QtGui.QMessageBox.RejectRole)
            else:
                btn = dlg.addButton(QtGui.QMessageBox.Cancel)

            self._button_result_map[btn] = CANCEL

            if self.default == CANCEL:
                dlg.setDefaultButton(btn)

        return dlg

    def _show_modal(self):
        self.control.setWindowModality(QtCore.Qt.ApplicationModal)
        retval = self.control.exec_()
        clicked_button = self.control.clickedButton()
        if clicked_button in self._button_result_map:
            retval = self._button_result_map[clicked_button]
        else:
            retval = _RESULT_MAP[retval]
        return retval

#### EOF ######################################################################
