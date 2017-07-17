""" Creates a ipywidgets user interface for a specified UI object, where the UI
is "live", meaning that it immediately updates its underlying object(s).
"""

# -----------------------------------------------------------------------------
#  Create the different 'live update' ipywidgets user interfaces.
# -----------------------------------------------------------------------------


def ui_live(ui, parent):
    """Creates a live, non-modal ipywidgets user interface for a specified UI
    object.
    """
    _ui_dialog(ui, parent)


def ui_livemodal(ui, parent):
    """Creates a live, modal ipywidgets user interface for a specified UI
    object.
    """
    raise NotImplementedError


def ui_popup(ui, parent):
    """Creates a live, modal popup ipywidgets user interface for a specified UI
    object.
    """
    raise NotImplementedError


def _ui_dialog(ui, parent):
    """Creates a live ipywidgets user interface for a specified UI object.
    """
    from .ui_base import BaseDialog

    BaseDialog.display_ui(ui, parent)
