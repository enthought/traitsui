#------------------------------------------------------------------------------
# Copyright (c) 2008, Riverbank Computing Limited
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD license.
# However, when used with the GPL version of PyQt the additional terms described in the PyQt GPL exception also apply

#
# Author: Riverbank Computing Limited
# Description: <Enthought pyface package component>
#------------------------------------------------------------------------------
""" The base class for all pyface wizards. """


# Major package imports.
from PyQt4 import QtCore, QtGui

# Enthought library imports.
from enthought.traits.api import Bool, implements, Instance, List, Property, \
        Unicode
from enthought.pyface.api import Dialog
from enthought.pyface.wizard.i_wizard import IWizard, MWizard
from enthought.pyface.wizard.i_wizard_controller import IWizardController
from enthought.pyface.wizard.i_wizard_page import IWizardPage


class Wizard(MWizard, Dialog):
    """ The base class for all pyface wizards.

    See the IWizard interface for the API documentation.

    """

    implements(IWizard)

    #### 'IWizard' interface ##################################################

    pages = Property(List(IWizardPage))

    controller = Instance(IWizardController)

    show_cancel = Bool(True)

    #### 'IWindow' interface ##################################################

    title = Unicode('Wizard')

    ###########################################################################
    # 'IWizard' interface.
    ###########################################################################

    # Override MWizard implementation to do nothing. We still call these methods
    # because it expected by IWizard, and users may wish to hook in custom code
    # before changing a page.

    def next(self):
        pass

    def previous(self):
        pass

    ###########################################################################
    # Protected 'IDialog' interface.
    ###########################################################################

    def _create_contents(self, parent):
        pass

    ###########################################################################
    # Protected 'IWidget' interface.
    ###########################################################################

    def _create_control(self, parent):
        control = _Wizard(parent, self)
        control.setOptions(QtGui.QWizard.NoDefaultButton |
                           QtGui.QWizard.NoBackButtonOnStartPage)
        control.setModal(self.style == 'modal')
        control.setWindowTitle(self.title)

        if self.size != (-1, -1):
            size = QtCore.QSize(*self.size)
            control.setMaximumSize(size)
            control.resize(size)

        if not self.show_cancel:
            control.setOption(QtGui.QWizard.NoCancelButton)

        if self.help_id:
            control.setOption(QtGui.QWizard.HaveHelpButton)
            QtCore.QObject.connect(control, QtCore.SIGNAL('helpRequested()'),
                    self._help_requested)

        # Add the initial pages.
        for page in self.pages:
            page.pyface_wizard = self
            control.addWizardPage(page)

        # Set the start page.
        control.setStartWizardPage()

        return control

    ###########################################################################
    # Private interface.
    ###########################################################################

    def _help_requested(self):
        """ Called when the 'Help' button is pressed. """

        # FIXME: Hook into a help system.
        print "Show help for", self.help_id

    #### Trait handlers #######################################################

    def _get_pages(self):
        """ The pages getter. """

        return self.controller.pages

    def _set_pages(self, pages):
        """ The pages setter. """

        # Remove pages from the old list that appear in the new list.  The old
        # list will now contain pages that are no longer in the wizard.
        old_pages = self.pages
        new_pages = []

        for page in pages:
            try:
                old_pages.remove(page)
            except ValueError:
                new_pages.append(page)

        # Dispose of the old pages.
        for page in old_pages:
            page.dispose_page()

        # If we have created the control then we need to add the new pages,
        # otherwise we leave it until the control is created.
        if self.control:
            for page in new_pages:
                self.control.addWizardPage(page)

        self.controller.pages = pages

    def _controller_default(self):
        """ Provide a default controller. """

        from enthought.pyface.wizard.wizard_controller import WizardController

        return WizardController()


class _Wizard(QtGui.QWizard):
    """ A QWizard sub-class that hooks into the controller to determine the
    next page to show. """

    def __init__(self, parent, pyface_wizard):
        """ Initialise the object. """

        QtGui.QWizard.__init__(self, parent)

        self._pyface_wizard = pyface_wizard
        self._controller = pyface_wizard.controller
        self._ids = {}

        QtCore.QObject.connect(self, QtCore.SIGNAL('currentIdChanged(int)'),
                self._update_controller)

    def addWizardPage(self, page):
        """ Add a page that implements IWizardPage. """

        # We must pass a parent otherwise TraitsUI does the wrong thing.
        qpage = page.create_page(self)
        qpage.pyface_wizard = self._pyface_wizard
        id = self.addPage(qpage)
        self._ids[id] = page

    def setStartWizardPage(self):
        """ Set the first page. """

        page = self._controller.get_first_page()
        id = self._page_to_id(page)

        if id >= 0:
            self.setStartId(id)

    def nextId(self):
        """ Reimplemented to return the id of the next page to display. """

        if self.currentId() < 0:
            return self._page_to_id(self._controller.get_first_page())
        current = self._ids[self.currentId()]
        next = self._controller.get_next_page(current)

        return self._page_to_id(next)

    def _update_controller(self, id):
        """ Called when the current page has changed. """

        # Keep the controller in sync with the wizard.
        self._controller.current_page = self._ids.get(id)

    def _page_to_id(self, page):
        """ Return the id of the given page. """

        if page is None:
            id = -1
        else:
            for id, p in self._ids.items():
                if p is page:
                    break
            else:
                id = -1

        return id

#### EOF ######################################################################
