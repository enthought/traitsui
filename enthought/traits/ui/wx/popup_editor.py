#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

    
# FIXME: PopupEditor is a proxy class defined here just for backward
# compatibility. The class (which represents the editor factory) has been moved 
# to the enthought.traits.ui.editors.list_editor file.
from enthought.traits.ui.editors.popup_editor \
    import _PopupEditor as BasePopupEditor, PopupEditor

from ui_editor \
    import UIEditor
    
#-------------------------------------------------------------------------------
#  '_PopupEditor' class:
#-------------------------------------------------------------------------------

class _PopupEditor ( BasePopupEditor, UIEditor ):
    pass
#--EOF-------------------------------------------------------------------------