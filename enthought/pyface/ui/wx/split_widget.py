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
""" Mix-in class for split widgets. """


# Major package imports.
import wx

# Enthought library imports.
from enthought.traits.api import Callable, Enum, Float, HasTraits, implements

# Local imports.
from enthought.pyface.i_split_widget import ISplitWidget, MSplitWidget


class SplitWidget(MSplitWidget, HasTraits):
    """ The toolkit specific implementation of a SplitWidget.  See the
    ISPlitWidget interface for the API documentation.
    """

    implements(ISplitWidget)

    #### 'ISplitWidget' interface #############################################

    direction = Enum('vertical', 'vertical', 'horizontal')

    ratio = Float(0.5)

    lhs = Callable

    rhs = Callable

    ###########################################################################
    # Protected 'ISplitWidget' interface.
    ###########################################################################

    def _create_splitter(self, parent):
        """ Create the toolkit-specific control that represents the widget. """

        sizer = wx.BoxSizer(wx.VERTICAL)
        splitter = wx.SplitterWindow(parent, -1, style=wx.CLIP_CHILDREN)
        splitter.SetSizer(sizer)
        splitter.SetAutoLayout(True)

        # If we don't set the minimum pane size, the user can drag the sash and
        # make one pane disappear!
        splitter.SetMinimumPaneSize(50)

        # Left hand side/top.
        lhs = self._create_lhs(splitter)
        sizer.Add(lhs, 1, wx.EXPAND)

        # Right hand side/bottom.
        rhs = self._create_rhs(splitter)
        sizer.Add(rhs, 1, wx.EXPAND)
        
        # Resize the splitter to fit the sizer's minimum size.
        sizer.Fit(splitter)

        # Split the window in the appropriate direction.
        #
        # fixme: Notice that on the initial split, we DON'T specify the split
        # ratio.  If we do then sadly, wx won't let us move the sash 8^()
        if self.direction == 'vertical':
            splitter.SplitVertically(lhs, rhs)

        else:
            splitter.SplitHorizontally(lhs, rhs)

        # We respond to the FIRST size event to make sure that the split ratio
        # is correct when the splitter is laid out in its parent.
        wx.EVT_SIZE(splitter, self._on_size)

        return splitter

    def _create_lhs(self, parent):
        """ Creates the left hand/top panel depending on the direction. """

        if self.lhs is not None:
            lhs = self.lhs(parent)
            if hasattr(wx, 'WindowPtr'):
                if not isinstance(lhs, (wx.Window, wx.WindowPtr)):
                    lhs = lhs.control
            else:
                # wx 2.8 did away with WindowPtr
                if not isinstance(lhs, wx.Window):
                    lhs = lhs.control
                
        else:
            # Dummy implementation - override!
            lhs = wx.Panel(parent, -1)
            lhs.SetBackgroundColour("yellow")
            lhs.SetSize((300, 200))

        return lhs

    def _create_rhs(self, parent):
        """ Creates the right hand/bottom panel depending on the direction. """

        if self.rhs is not None:
            rhs = self.rhs(parent)
            if hasattr(wx, 'WindowPtr'):
                if not isinstance(rhs, (wx.Window, wx.WindowPtr)):
                    rhs = rhs.control
            else:
                # wx 2.8 did away with WindowPtr
                if not isinstance(rhs, wx.Window):
                    rhs = rhs.control
        
        else:
            # Dummy implementation - override!
            rhs = wx.Panel(parent, -1)
            rhs.SetBackgroundColour("green")
            rhs.SetSize((100, 200))

        return rhs
    
    ###########################################################################
    # Private interface.
    ###########################################################################

    #### wx event handlers ####################################################

    def _on_size(self, event):
        """ Called when the frame is resized. """

        splitter = event.GetEventObject()
        width, height = splitter.GetSize()

        # Make sure that the split ratio is correct.
        if self.direction == 'vertical':
            position = int(width * self.ratio)

        else:
            position = int(height * self.ratio)
        
        splitter.SetSashPosition(position)

        # Since we only care about the FIRST size event, remove ourselves as
        # a listener.
        #wx.EVT_SIZE(splitter, None)

        return
    
#### EOF ######################################################################
