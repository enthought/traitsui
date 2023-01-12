# (C) Copyright 2004-2023 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

""" Defines the theme style information for a DockWindow and its components.
"""

from pyface.ui_traits import Image
from traits.api import HasPrivateTraits, Bool, Property, cached_property

from .ui_traits import ATheme


class DockWindowTheme(HasPrivateTraits):
    """Defines the theme style information for a DockWindow and its components."""

    # -- Public Trait Definitions ---------------------------------------------

    #: Use the theme background color as the DockWindow background color?
    use_theme_color = Bool(True)

    #: Draw notebook tabs at the top (True) or the bottom (False)?
    tabs_at_top = Bool(True)

    #: Active tab theme:
    tab_active = ATheme

    #: Inactive tab theme:
    tab_inactive = ATheme

    #: Optional image to use for right edge of rightmost inactive tab:
    tab_inactive_edge = Image

    #: Tab hover theme (used for inactive tabs):
    tab_hover = ATheme

    #: Optional image to use for right edge of rightmost hover tab:
    tab_hover_edge = Image

    #: Tab background theme:
    tab_background = ATheme

    #: Tab theme:
    tab = ATheme

    #: Vertical splitter bar theme:
    vertical_splitter = ATheme

    #: Horizontal splitter bar theme:
    horizontal_splitter = ATheme

    #: Vertical drag bar theme:
    vertical_drag = ATheme

    #: Horizontal drag bar theme:
    horizontal_drag = ATheme

    #: The bitmap for the 'tab_inactive_edge' image:
    tab_inactive_edge_bitmap = Property(observe="tab_inactive_edge")

    #: The bitmap for the 'tab_hover_edge' image:
    tab_hover_edge_bitmap = Property(observe="tab_hover_edge")

    # -- Property Implementations ---------------------------------------------

    @cached_property
    def _get_tab_inactive_edge_bitmap(self):
        image = self.tab_inactive_edge
        if image is None:
            return None

        return image.create_bitmap()

    @cached_property
    def _get_tab_hover_edge_bitmap(self):
        image = self.tab_hover_edge
        if image is None:
            return self.tab_inactive_edge_bitmap

        return image.create_bitmap()


# -------------------------------------------------------------------------
#  Default theme handling
# -------------------------------------------------------------------------

#: The current default DockWindow theme
_dock_window_theme = None


def dock_window_theme(theme=None):
    """Get or set the default DockWindow theme."""
    global _dock_window_theme

    if _dock_window_theme is None:
        from .default_dock_window_theme import default_dock_window_theme

        _dock_window_theme = default_dock_window_theme

    old_theme = _dock_window_theme
    if theme is not None:
        _dock_window_theme = theme

    return old_theme
