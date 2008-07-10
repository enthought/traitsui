#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from enthought.traits.api \
    import Float, Enum, Any

from enthought.traits.ui.api \
    import View, Item, EditorFactory, BasicEditorFactory, TextEditor
    
from enthought.traits.ui.ui_traits \
    import EditorStyle

from enthought.traits.ui.wx.ui_editor \
    import UIEditor

#-------------------------------------------------------------------------------
#  '_PopupEditor' class:
#-------------------------------------------------------------------------------

class _PopupEditor ( UIEditor ):
        
    #---------------------------------------------------------------------------
    #  Creates the traits UI for the editor:
    #---------------------------------------------------------------------------
                
    def init_ui ( self, parent ):
        """ Creates the traits UI for the editor.
        """
        return self.object.edit_traits( view   = self.base_view(), 
                                        parent = parent )
        
    def base_view ( self ):
        """ Returns the View that allows the popup view to be displayed.
        """
        return View(
            Item( self.name, 
                  show_label = False,
                  style      = 'readonly',
                  editor     = TextEditor( view = self.popup_view() ),
                  padding    = -4,
            ),
            kind = 'subpanel'
        )

    def popup_view ( self ):
        """ Returns the popup View.
        """
        factory = self.factory
        item    = Item( self.name, 
                        show_label = False,
                        padding    = -4,
                        style      = factory.style,
                        height     = factory.height,
                        width      = factory.width )
        
        editor = factory.editor
        if editor is not None:
            if not isinstance( editor, EditorFactory ):
                editor = editor()
            item.editor = editor
            
        return View( item, kind = factory.kind ) 

#-------------------------------------------------------------------------------
#  'PopupEditor' class:
#-------------------------------------------------------------------------------

class PopupEditor ( BasicEditorFactory ):
    
    # The class used to construct editor objects:
    klass = _PopupEditor
    
    # The kind of popup to use:
    kind = Enum( 'popover', 'popup', 'info' )
    
    # The editor to use for the pop-up view (can be None (use default editor),
    # an EditorFactory instance, or a callable that returns an EditorFactory
    # instance):
    editor = Any

    # The style of editor to use for the popup editor (same as Item.style):
    style = EditorStyle
    
    # The height of the popup (same as Item.height):
    height = Float( -1.0 )
    
    # The width of the popup (same as Item.width):
    width = Float( -1.0 )

