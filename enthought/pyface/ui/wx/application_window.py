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


# Major package imports.
import wx

# Enthought library imports.
from enthought.pyface.action.api import MenuBarManager, StatusBarManager
from enthought.pyface.action.api import ToolBarManager
from enthought.traits.api import implements, Instance, Unicode

# Local imports.
from enthought.pyface.i_application_window import IApplicationWindow, MApplicationWindow
from enthought.pyface.image_resource import ImageResource
from window import Window


class ApplicationWindow(MApplicationWindow, Window):
    """ The toolkit specific implementation of an ApplicationWindow.  See the
    IApplicationWindow interface for the API documentation.
    """

    implements(IApplicationWindow)

    #### 'IApplicationWindow' interface #######################################

    icon = Instance(ImageResource)

    menu_bar_manager = Instance(MenuBarManager)

    status_bar_manager = Instance(StatusBarManager)

    tool_bar_manager = Instance(ToolBarManager)

    #### 'IWindow' interface ##################################################

    # fixme: We can't set the default value of the actual 'size' trait here as
    # in the toolkit-specific event handlers for window size and position
    # changes, we set the value of the shadow '_size' trait. The problem is
    # that by doing that traits never knows that the trait has been set and
    # hence always returns the default value! Using a trait initializer method
    # seems to work however (e.g. 'def _size_default'). Hmmmm....
##     size = (800, 600)

    title = Unicode("Pyface")

    ###########################################################################
    # Protected 'IApplicationWindow' interface.
    ###########################################################################

    def _create_contents(self, parent):
        panel = wx.Panel(parent, -1)
        panel.SetSize((500, 400))
        panel.SetBackgroundColour('blue')

        return panel

    def _create_menu_bar(self, parent):
        if self.menu_bar_manager is not None:
            menu_bar = self.menu_bar_manager.create_menu_bar(parent)
            self.control.SetMenuBar(menu_bar)

    def _create_status_bar(self, parent):
        if self.status_bar_manager is not None:
            status_bar = self.status_bar_manager.create_status_bar(parent)
            self.control.SetStatusBar(status_bar)

    def _create_tool_bar(self, parent):
        if self.tool_bar_manager is not None:
            tool_bar = self.tool_bar_manager.create_tool_bar(parent)
            self.control.SetToolBar(tool_bar)

    def _set_window_icon(self):
        if self.icon is None:
            icon = ImageResource('application.ico')
        else:
            icon = self.icon

        self.control.SetIcon(icon.create_icon())

    ###########################################################################
    # 'Window' interface.
    ###########################################################################

    def _size_default(self):
        """ Trait initialiser. """

        return (800, 600)

    ###########################################################################
    # Protected 'IWidget' interface.
    ###########################################################################

    def _create(self):
        super(ApplicationWindow, self)._create()

        self._create_contents(self.control)

        self._create_trim_widgets(self.control)

    def _create_control(self, parent):
        style = wx.DEFAULT_FRAME_STYLE | wx.FRAME_NO_WINDOW_MENU | wx.CLIP_CHILDREN
        control =  wx.Frame(parent, -1, self.title, style=style, size=self.size,
                            pos=self.position)

        control.SetBackgroundColour(
            wx.SystemSettings_GetColour( wx.SYS_COLOUR_BTNFACE ))
            
        return control
    
#### EOF ######################################################################
