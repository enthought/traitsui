#------------------------------------------------------------------------------
# Copyright (c) 2005, Enthought, Inc.
# All rights reserved.
# 
# This software is provided without warranty under the terms of the BSD
# license included in enthought/LICENSE.txt and may be redistributed only
# under the conditions described in the aforementioned license.  The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
# Thanks for using Enthought open source!
# 
# Author: Enthought, Inc.
# Description: <Enthought pyface package component>
#------------------------------------------------------------------------------
""" The base class for all pyface wizards. """


# Major package imports.
import wx

# Enthought library imports.
from enthought.traits.api import Bool, implements, Instance, Unicode
from enthought.pyface.api import Dialog, LayeredPanel
from enthought.pyface.wizard.i_wizard import IWizard, MWizard
from enthought.pyface.wizard.wizard_controller import WizardController


class Wizard(MWizard, Dialog):
    """ The base class for all pyface wizards.

    See the IWizard interface for the API documentation.

    """

    implements(IWizard)

    #### 'IWizard' interface ##################################################

    controller = Instance(WizardController)

    show_cancel = Bool(True)
    
    #### 'IWindow' interface ##################################################

    title = Unicode('Wizard')
    
    ###########################################################################
    # Protected 'IDialog' interface.
    ###########################################################################

    def _create_dialog_area(self, parent):
        """ Creates the main content of the dialog. """

        self._layered_panel = panel = LayeredPanel(parent)
        # fixme: Specific size?
        panel.control.SetSize((100, 200))

        return panel.control

    def _create_buttons(self, parent):
        """ Creates the buttons. """

        sizer = wx.BoxSizer(wx.HORIZONTAL)

        # 'Back' button.
        self._back = back = wx.Button(parent, -1, "Back")
        wx.EVT_BUTTON(parent, back.GetId(), self._on_back)
        sizer.Add(back, 0)

        # 'Next' button.
        self._next = next = wx.Button(parent, -1, "Next")
        wx.EVT_BUTTON(parent, next.GetId(), self._on_next)
        sizer.Add(next, 0, wx.LEFT, 5)
        next.SetDefault()
        
        # 'Finish' button.
        self._finish = finish = wx.Button(parent, wx.ID_OK, "Finish")
        finish.Enable(self.controller.complete)
        wx.EVT_BUTTON(parent, wx.ID_OK, self._wx_on_ok)
        sizer.Add(finish, 0, wx.LEFT, 5)
        
        # 'Cancel' button.
        if self.show_cancel:
            self._cancel = cancel = wx.Button(parent, wx.ID_CANCEL, "Cancel")
            wx.EVT_BUTTON(parent, wx.ID_CANCEL, self._wx_on_cancel)
            sizer.Add(cancel, 0, wx.LEFT, 10)

        # 'Help' button.
        if len(self.help_id) > 0:
            help = wx.Button(parent, wx.ID_HELP, "Help")
            wx.EVT_BUTTON(parent, wx.ID_HELP, self._wx_on_help)
            sizer.Add(help, 0, wx.LEFT, 10)

        return sizer

    ###########################################################################
    # Protected 'MWizard' interface.
    ###########################################################################

    def _show_page(self, page):
        """ Show the page at the specified index. """

        panel = self._layered_panel

        # If the page has not yet been shown then create it.
        if not panel.has_layer(page.id):
            panel.add_layer(page.id, page.create_page(panel.control))

        # Show the page.
        layer = panel.show_layer(page.id)
        layer.SetFocus()
        
        # Set the current page in the controller.
        #
        # fixme: Shouldn't this interface be reversed?  Maybe calling
        # 'next_page' on the controller should cause it to set its own current
        # page?
        self.controller.current_page = page
        
        return

    def _update(self):
        """ Enables/disables buttons depending on the state of the wizard. """

        controller = self.controller
        current_page = controller.current_page

        is_first_page = controller.is_first_page(current_page)
        is_last_page  = controller.is_last_page(current_page)
        
        # 'Next button'.
        if self._next is not None:
            self._next.Enable(current_page.complete and not is_last_page)

        # 'Back' button.
        if self._back is not None:
            self._back.Enable(not is_first_page)

        # 'Finish' button.
        if self._finish is not None:
            self._finish.Enable(controller.complete)
        
        # If this is the last page then the 'Finish' button is the default
        # button, otherwise the 'Next' button is the default button.
        if is_last_page:
            if self._finish is not None:
                self._finish.SetDefault()

        else:
            if self._next is not None:
                self._next.SetDefault()
            
        return

    #### wx event handlers ####################################################

    def _on_next(self, event):
        """ Called when the 'Next' button is pressed. """

        self.next()
        
        return

    def _on_back(self, event):
        """ Called when the 'Back' button is pressed. """

        self.previous()
        
        return
    
#### EOF ######################################################################
