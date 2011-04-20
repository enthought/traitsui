#------------------------------------------------------------------------------
# Copyright (c) 2010, Enthought Inc
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD license.

#
# Author: Enthought Inc
# Description: <Enthought pyface code editor>
#------------------------------------------------------------------------------

import weakref

from enthought.qt import QtGui, QtCore

from find_widget import FindWidget

class ReplaceWidget(FindWidget):

    def __init__(self, parent):
        super(FindWidget, self).__init__(parent)
        self.adv_code_widget = weakref.ref(parent)

        self.button_size = self.fontMetrics().width(u'Replace All') + 20

        form_layout = QtGui.QFormLayout()
        form_layout.addRow('Fin&d', self._create_find_control())
        form_layout.addRow('Rep&lace', self._create_replace_control())

        layout = QtGui.QHBoxLayout()
        layout.addLayout(form_layout)

        close_button = QtGui.QPushButton('Close')
        layout.addWidget(close_button, 1, QtCore.Qt.AlignRight)
        close_button.clicked.connect(self.hide)

        self.setLayout(layout)

    def _create_replace_control(self):
        control = QtGui.QWidget(self)

        self.replace_edit = QtGui.QLineEdit()
        self.replace_button = QtGui.QPushButton('&Replace')
        self.replace_button.setFixedWidth(self.button_size)
        self.replace_all_button = QtGui.QPushButton('Replace &All')
        self.replace_all_button.setFixedWidth(self.button_size)

        layout = QtGui.QHBoxLayout()
        layout.addWidget(self.replace_edit)
        layout.addWidget(self.replace_button)
        layout.addWidget(self.replace_all_button)
        layout.addStretch(2)
        layout.setMargin(0)

        control.setLayout(layout)
        return control

