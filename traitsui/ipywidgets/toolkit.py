from traitsui.toolkit import assert_toolkit_import
assert_toolkit_import(['ipywidgets'])

from traits.trait_notifiers import set_ui_handler
from pyface.base_toolkit import Toolkit as PyfaceToolkit
from traitsui.toolkit import Toolkit

import ipywidgets


toolkit = PyfaceToolkit(
    'pyface',
    'ipywidgets',
    'traitsui.ipywidgets'
)

def ui_handler(handler, *args, **kwds):
    """ Handles UI notification handler requests that occur on a thread other
        than the UI thread.
    """
    handler(*args, **kwds)

set_ui_handler(ui_handler)


class GUIToolkit(Toolkit):
    """ Implementation class for ipywidgets toolkit """

    def ui_panel(self, ui, parent):
        from .ui_panel import ui_panel
        ui_panel(ui, parent)

    def ui_live(self, ui, parent):
        from .ui_panel import ui_panel
        ui_panel(ui, parent)

    def rebuild_ui(self, ui):
        """ Rebuilds a UI after a change to the content of the UI.
        """
        if ui.control is not None:
            ui.recycle()
            ui.info.ui = ui
        ui.rebuild(ui, ui.parent)

    def constants(self):
        """ Returns a dictionary of useful constants.

            Currently, the dictionary should have the following key/value pairs:

            - 'WindowColor': the standard window background color in the toolkit
              specific color format.
        """
        return {'WindowColor': None}


    def color_trait(self, *args, **traits):
        #import color_trait as ct
        #return ct.PyQtColor(*args, **traits)
        from traits.api import Unicode
        return Unicode

    def rgb_color_trait(self, *args, **traits):
        #import rgb_color_trait as rgbct
        #return rgbct.RGBColor(*args, **traits)
        from traits.api import Unicode
        return Unicode

    def font_trait(self, *args, **traits):
        #import font_trait as ft
        #return ft.PyQtFont(*args, **traits)
        from traits.api import Unicode
        return Unicode
