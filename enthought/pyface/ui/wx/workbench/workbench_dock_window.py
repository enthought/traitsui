#------------------------------------------------------------------------------
#
#  Copyright (c) 2005, Enthought, Inc.
#  All rights reserved.
# 
#  This software is provided without warranty under the terms of the BSD
#  license included in enthought/LICENSE.txt and may be redistributed only
#  under the conditions described in the aforementioned license.  The license
#  is also available online at http://www.enthought.com/licenses/BSD.txt
#
#  Thanks for using Enthought open source!
# 
#  Author: Enthought, Inc.
#
#------------------------------------------------------------------------------

""" Base class for workbench dock windows.
"""

# Standard library imports.
import logging

# Enthought library imports.
from enthought.pyface.dock.api import DockGroup, DockRegion, DockWindow


logger = logging.getLogger(__name__)

class WorkbenchDockWindow(DockWindow):
    """ Base class for workbench dock windows.

    This class just adds a few useful methods to the standard 'DockWindow'
    interface. Hopefully at some stage these can be part of that API too!

    """

    ###########################################################################
    # Protected 'DockWindow' interface.
    ###########################################################################

    def _right_up(self, event):
        """ Handles the right mouse button being released.

        We override this to stop the default dock window context menus from
        appearing.

        """

        pass

    ###########################################################################
    # 'WorkbenchDockWindow' interface.
    ###########################################################################

    def activate_control(self, id):
        """ Activates the dock control with the specified Id.

        Does nothing if no such dock control exists (well, it *does* write
        a debug message to the logger).

        """

        control = self.get_control(id)
        if control is not None:
            logger.debug('activating control <%s>', id)
            control.activate()

        else:
            logger.debug('no control <%s> to activate', id)

        return

    def close_control(self, id):
        """ Closes the dock control with the specified Id.

        Does nothing if no such dock control exists (well, it *does* write
        a debug message to the logger).

        """

        control = self.get_control(id)
        if control is not None:
            logger.debug('closing control <%s>', id)
            control.close()

        else:
            logger.debug('no control <%s> to close', id)

        return
    
    def get_control(self, id, visible_only=True):
        """ Returns the dock control with the specified Id.

        Returns None if no such dock control exists.

        """
        
        for control in self.get_controls(visible_only):
            if control.id == id:
                break

        else:
            control = None

        return control

    def get_controls(self, visible_only=True):
        """ Returns all of the dock controls in the window. """
        
        sizer   = self.control.GetSizer()
        section = sizer.GetContents()

        return section.get_controls(visible_only=visible_only)

    def get_regions(self, group):
        """ Returns all dock regions in a dock group (recursively). """

        regions = []
        for item in group.contents:
            if isinstance(item, DockRegion):
                regions.append(item)

            if isinstance(item, DockGroup):
                regions.extend(self.get_regions(item))

        return regions

    def get_structure(self):
        """ Returns the window structure (minus the content). """

        sizer = self.control.GetSizer()

        return sizer.GetStructure()

    def reset_regions(self):
        """ Activates the first dock control in every region. """

        sizer   = self.control.GetSizer()
        section = sizer.GetContents()

        for region in self.get_regions(section):
            if len(region.contents) > 0:
                region.contents[0].activate(layout=False)

        return

    def set_structure(self, structure, handler=None):
        """ Sets the window structure. """

        sizer = self.control.GetSizer()
        sizer.SetStructure(self.control.GetParent(), structure, handler)
        
        return

#### EOF ######################################################################
