#------------------------------------------------------------------------------
# Copyright (c) 2008, Riverbank Computing Limited
# All rights reserved.
#
# This software is provided without warranty under the terms of the GPL v2
# license.
#
# Author: Riverbank Computing Limited
# Description: <Enthought pyface package component>
#------------------------------------------------------------------------------
""" A page in a wizard. """


# Major package imports.
from PyQt4 import QtCore, QtGui

# Enthought library imports.
from enthought.traits.api import Bool, implements, HasTraits, Str, Tuple, \
        Unicode
from enthought.pyface.wizard.i_wizard_page import IWizardPage, MWizardPage


class WizardPage(MWizardPage, HasTraits):
    """ The toolkit specific implementation of a WizardPage.

    See the IWizardPage interface for the API documentation.

    """

    implements(IWizardPage)

    #### 'IWizardPage' interface ##############################################

    id = Str

    next_id = Str

    last_page = Bool(False)

    complete = Bool(False)

    heading = Unicode

    subheading = Unicode

    size = Tuple

    ###########################################################################
    # 'IWizardPage' interface.
    ###########################################################################

    def create_page(self, parent):
        """ Creates the wizard page. """

        content = self._create_page_content(parent)

        # We allow some flexibility with the sort of control we are given.
        if not isinstance(content, QtGui.QWizardPage):
            wp = _WizardPage(self)

            if isinstance(content, QtGui.QLayout):
                wp.setLayout(content)
            else:
                assert isinstance(content, QtGui.QWidget)

                lay = QtGui.QVBoxLayout()
                lay.addWidget(content)

                wp.setLayout(lay)

            content = wp

        # Honour any requested page size.
        if self.size:
            width, height = self.size

            if width > 0:
                content.setMinimumWidth(width)

            if height > 0:
                content.setMinimumHeight(height)

        content.setTitle(self.heading)
        content.setSubTitle(self.subheading)

        return content

    ###########################################################################
    # Protected 'IWizardPage' interface.
    ###########################################################################

    def _create_page_content(self, parent):
        """ Creates the actual page content. """

        # Dummy implementation - override! 
        control = QtGui.QWidget(parent)

        palette = control.palette()
        palette.setColor(QtGui.QPalette.Window, QtGui.QColor('yellow'))
        control.setPalette(palette)
        control.setAutoFillBackground(True)

        return control


class _WizardPage(QtGui.QWizardPage):
    """ A QWizardPage sub-class that hooks into the IWizardPage's 'complete'
    trait. """

    def __init__(self, page):
        """ Initialise the object. """

        QtGui.QWizardPage.__init__(self)

        page.on_trait_change(self._on_complete_changed, 'complete')

        self._page = page

    def isComplete(self):
        """ Reimplemented to return the state of the 'complete' trait. """

        return self._page.complete

    def _on_complete_changed(self):
        """ The trait handler for when the page's completion state changes. """

        self.emit(QtCore.SIGNAL('completeChanged()'))

#### EOF ######################################################################
