from traitsui.toolkit import assert_toolkit_import
assert_toolkit_import(['ipywidgets'])

from traitsui.toolkit import Toolkit

import ipywidgets


class GUIToolkit(Toolkit):
    """ Implementation class for ipywidgets toolkit """

    def ui_panel(self, ui, parent):
        from .ui_panel import ui_panel
        ui_panel(ui, parent)
