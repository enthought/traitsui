#-------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------


# FIXME: PopupEditor is a proxy class defined here just for backward
# compatibility. The class (which represents the editor factory) has been moved
# to the traitsui.editors.list_editor file.
from __future__ import absolute_import
from traitsui.editors.popup_editor \
    import _PopupEditor as BasePopupEditor, PopupEditor

from .ui_editor \
    import UIEditor

#-------------------------------------------------------------------------
#  '_PopupEditor' class:
#-------------------------------------------------------------------------


class _PopupEditor(BasePopupEditor, UIEditor):
    pass
#--EOF-------------------------------------------------------------------------
