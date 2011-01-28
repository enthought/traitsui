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

""" A tool bar manager realizes itself in a tool palette control.
"""

# Major package imports.
import wx

# Enthought library imports.
from enthought.traits.api import Any, Bool, Enum, Instance, Tuple

# Local imports.
from enthought.pyface.image_cache import ImageCache
from enthought.pyface.action.action_manager import ActionManager
from tool_palette import ToolPalette


class ToolPaletteManager(ActionManager):
    """ A tool bar manager realizes itself in a tool palette bar control. """

    #### 'ToolPaletteManager' interface #######################################

    # The size of tool images (width, height).
    image_size = Tuple((16, 16))

    # Should we display the name of each tool bar tool under its image?
    show_tool_names = Bool(True)

    #### Private interface ####################################################

    # Cache of tool images (scaled to the appropriate size).
    _image_cache = Instance(ImageCache)

    ###########################################################################
    # 'object' interface.
    ###########################################################################

    def __init__(self, *args, **traits):
        """ Creates a new tool bar manager. """

        # Base class contructor.
        super(ToolPaletteManager, self).__init__(*args, **traits)

        # An image cache to make sure that we only load each image used in the
        # tool bar exactly once.
        self._image_cache = ImageCache(self.image_size[0], self.image_size[1])

        return

    ###########################################################################
    # 'ToolPaletteManager' interface.
    ###########################################################################

    def create_tool_palette(self, parent, controller=None):
        """ Creates a tool bar. """

        # Create the control.
        tool_palette = ToolPalette(parent)

        # Add all of items in the manager's groups to the tool bar.
        self._add_tools(tool_palette, self.groups)

        self._set_initial_tool_state(tool_palette, self.groups)

        return tool_palette

    ###########################################################################
    # Private interface.
    ###########################################################################

    def _add_tools(self, tool_palette, groups):
        """ Adds tools for all items in a list of groups. """

        previous_non_empty_group = None
        for group in self.groups:
            if len(group.items) > 0:
                # Is a separator required?
## FIXME : Does the palette need the notion of a separator?
##                 if previous_non_empty_group is not None and group.separator:
##                     tool_bar.AddSeparator()
##
##                 previous_non_empty_group = group

                # Create a tool bar tool for each item in the group.
                for item in group.items:
                    control_id = item.add_to_palette(
                        tool_palette,
                        self._image_cache,
                        self.show_tool_names
                    )
                    item.control_id = control_id

        tool_palette.realize()

        return

    def _set_initial_tool_state(self, tool_palette, groups):
        """ Workaround for the wxPython tool bar bug.

        Without this,  only the first item in a radio group can be selected
         when the tool bar is first realised 8^()

        """

        for group in groups:
            checked = False
            for item in group.items:
                # If the group is a radio group,  set the initial checked state
                # of every tool in it.
                if item.action.style == 'radio':
                    tool_palette.toggle_tool(item.control_id, item.action.checked)
                    checked = checked or item.action.checked

                # Every item in a radio group MUST be 'radio' style, so we
                # can just skip to the next group.
                else:
                    break

            # We get here if the group is a radio group.
            else:
                # If none of the actions in the group is specified as 'checked'
                # we will check the first one.
                if not checked and len(group.items) > 0:
                    group.items[0].action.checked = True

        return

#### EOF ######################################################################
