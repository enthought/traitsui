#-------------------------------------------------------------------------------
#
#  An editor for displaying list items as themed Traits UI Views on a themed
#  free-form canvas.
#
#  Written by: David C. Morrill
#
#  Date: 08/10/2007
#
#  (c) Copyright 2007 by Enthought, Inc.
#
#-------------------------------------------------------------------------------

""" An editor for displaying list items as themed Traits UI Views on a themed
    free-form canvas.
"""

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

import wx

from enthought.traits.api \
    import HasTraits, HasPrivateTraits, HasStrictTraits, Interface, Instance, \
           List, Enum, Color, Bool, Range, Str, Float, Int, Event, Tuple, \
           Property, Delegate, Any, Missing, Undefined, implements, \
           on_trait_change, cached_property
           
from enthought.traits.trait_base \
    import SequenceTypes
    
from enthought.traits.trait_base \
    import user_name_for
           
from enthought.traits.ui.api \
    import UI, View, Item, Theme, Editor
    
from enthought.traits.ui.ui_traits \
    import ATheme, AView
           
from enthought.traits.ui.menu \
    import Menu, Action
    
from enthought.traits.ui.wx.editor \
    import Editor
    
from enthought.traits.ui.wx.basic_editor_factory \
    import BasicEditorFactory
    
from enthought.traits.ui.wx.image_panel \
    import ImagePanel
    
from enthought.traits.ui.wx.themed_checkbox_editor \
    import ThemedCheckboxEditor
    
from enthought.traits.ui.wx.themed_slider_editor \
    import ThemedSliderEditor
    
from enthought.traits.ui.wx.helper \
    import init_wx_handlers
    
from enthought.pyface.api \
    import confirm, YES
    
from enthought.pyface.dock.api \
    import add_feature
    
from enthought.pyface.timer.api \
    import do_later

from enthought.pyface.image_resource \
    import ImageResource

from enthought.util.wx.drag_and_drop \
    import PythonDropSource, PythonDropTarget
    
#-------------------------------------------------------------------------------
#  Constants:
#-------------------------------------------------------------------------------
        
# Have the contents of an item been modified:
Modified = None

# wx pen styles:
pen_styles = {
    'solid': wx.SOLID,
    'dash':  wx.SHORT_DASH,
    'dot':   wx.DOT
}

# Dictionay of standard images used:
images = {
    'feature':  ImageResource( 'feature' ),
    'selected': ImageResource( 'selected' ),
    'clone':    ImageResource( 'clone' ),
    'drag':     ImageResource( 'drag' ),
    'minimize': ImageResource( 'minimize' ),
    'maximize': ImageResource( 'maximize' ),
    'close':    ImageResource( 'close' ),
    
    'add':      ImageResource( 'add' ),
    'clear':    ImageResource( 'clear' ),
    'load':     ImageResource( 'load' ),
    'save':     ImageResource( 'save' ),
}

# The numeric value of the 'move mode' bit mask:
MOVE_MODE = 12

#-------------------------------------------------------------------------------
#  Trait definitions:
#-------------------------------------------------------------------------------

# Operations allowed on a list canvas:
CanvasOperations = List( Enum( 'move', 'size', 'add', 'clone', 'drag', 'drop', 
                               'load', 'save', 'close', 'clear', 'minimize', 
                               'status', 'tooltip' ) )

#-------------------------------------------------------------------------------
#  Helper functions:
#-------------------------------------------------------------------------------

# wx stock cursor cache:
stock_cursors = {}

def get_cursor ( cursor_id ):
    """ Returns the wx stock cursor corresponding to a specified cursor id.
    """
    global stock_cursors
    
    cursor = stock_cursors.get( cursor_id )
    if cursor is None:
        stock_cursors[ cursor_id ] = cursor = wx.StockCursor( cursor_id )
        
    return cursor
        
#-------------------------------------------------------------------------------
#  'IListCanvasAdapter' interface:
#-------------------------------------------------------------------------------

class IListCanvasAdapter ( Interface ):
    """ The interface that any sub-adapter of a ListCanvasAdapter must
        implement.
    """

    # The current list canvas item:
    item = Instance( HasTraits )

    # The current item being dropped (if any):
    drop = Instance( HasTraits )    
    
    # Does the adapter know how to handle the current *item* or not:
    accepts = Bool
    
    # Does the value of *accepts* depend only upon the type of *item*?
    is_cacheable = Bool

#-------------------------------------------------------------------------------
#  'AnIListCanvasAdapter' interface:
#-------------------------------------------------------------------------------

class AnIListCanvasAdapter ( HasPrivateTraits ):
    """ A concrete implementation of the IListCanvasAdapter interface.
    """
    
    implements( IListCanvasAdapter )

    # The current list canvas item:
    item = Instance( HasTraits )

    # The current item being dropped (if any):
    drop = Instance( HasTraits )    
    
    # Does the adapter know how to handle the current *item* or not:
    accepts = Bool( True )
    
    # Does the value of *accepts* depend only upon the type of *item*?
    is_cacheable = Bool( True )
    
#-------------------------------------------------------------------------------
#  'IListCanvasItem' interface:
#-------------------------------------------------------------------------------

class IListCanvasItem ( Interface ):
    """ An interface that items on a list canvas can implement to supply
        information that would normally be supplied by a ListCanvasAdapter.
        
        Note that it is not necessary for a class to implement the entire
        interface. If a list canvas adapter sees that an item implements the
        IListCanvasItem interface, it will check to see if the class implements
        the particular aspect of the interface it needs. If it does not, then
        the adapter will satisfy the request itself.
    """
    
    # The theme to use for the list canvas item when it is active:
    list_canvas_item_theme_active = ATheme
    
    # The theme to use for the list canvas item when it is inactive:
    list_canvas_item_theme_inactive = ATheme
    
    # The theme to use while the pointer hovers over the list canvas item:
    list_canvas_item_theme_hover = ATheme
    
    # The title to use for the list canvas item:
    list_canvas_item_title = Str
    
    # The unique id of the list canvas item:
    list_canvas_item_unique_id = Str
    
    # Can the list canvas item be moved?
    list_canvas_item_can_move = Bool
    
    # Can the list canvas item be resized?
    list_canvas_item_can_resize = Bool
    
    # Can the current drag object be dropped on the list canvas item?
    list_canvas_item_can_drop = Bool
    
    # The item (or list of items) to be added to the canvas when the current
    # drag object is dropped on the list canvas item:
    list_canvas_item_dropped = Any # List/Instance/None
    
    # If the preceding two traits are implemented, then this trait should be 
    # implemented as well if you need to know what object is being dropped:
    list_canvas_item_drop = Instance( HasTraits )
    
    # Can the list canvas item be closed?
    list_canvas_item_can_close = Enum( True, False, Modified )
    
    # Returns the draggable form of the list canvas item:
    list_canvas_item_drag = Instance( HasTraits )
    
    # Specifies the clone of the list canvas item:
    list_canvas_item_clone = Instance( HasTraits )
    
    # Specifies the Traits UI View to use for the canvas list item when it is
    # added to the canvas:
    list_canvas_item_view = AView
    
    # Specifies the view model used to represent the canvas list item when it 
    # is added to the canvas:
    list_canvas_item_view_model = Instance( HasTraits )
    
    # Specifies the initial size to make the canvas list item when it is added
    # to the canvas. The value is a tuple of the form: (width,height), where 
    # the width and height values have the following meaning:
    # - <= 0: Use the default size.
    # - 0 < value <= 1: Use the specified fraction of the corresponding width
    #     or height dimension.
    # > 1: Use int(value) as the actual width or height specified in pixels.
    list_canvas_item_size = Tuple( Float, Float )
    
    # Specifies the initial position of the canvas list item when it is added 
    # to the canvas. The value is a tuple of the form: (x,y), where x and y 
    # values have the following meaning:
    # - <= 0: Use the default coordinate.
    # - 0 < value <= 1: Use the specified fraction of the corresponding width
    #     or height dimension as the coordinate value.
    # > 1: Use int(value) as the actual x or y coordinate specified in pixels.
    list_canvas_item_position = Tuple( Float, Float )
    
    # Specifies the tooltip to display for the list canvas item:
    list_canvas_item_tooltip = Str
    
    # Event fired when the list canvas item is closed:
    list_canvas_item_closed = Event
    
    # The event fired when the list canvas item is activated:
    list_canvas_item_activated = Event
    
    # The event fired when the list canvas item is de-activated:
    list_canvas_item_deactivated = Event
    
#-------------------------------------------------------------------------------
#  'IListCanvasAware' interface:
#-------------------------------------------------------------------------------

class IListCanvasAware ( Interface ):
    """ Interface for objects that want to be aware that they are being used
        on a list canvas.
    """
    
    # The list canvas item associated with this object:
    list_canvas_item = Instance( 'ListCanvasItem' )
    
#-------------------------------------------------------------------------------
#  'ListCanvasAdapter' class:
#-------------------------------------------------------------------------------

class ListCanvasAdapter ( HasPrivateTraits ):
    """ The base class for all list canvas editor adapter classes.
    """
    
    #-- Traits that are item specific ------------------------------------------
    
    # The default theme to use for the current active list canvas item:
    theme_active = ATheme( Theme( 'default_active', 
                                  label = ( 0, 2 ), content = ( -15, 2 ) ) )
    
    # The default theme to use for the current inactive list canvas item (if 
    # None is returned, the value of *theme_active* is used):
    theme_inactive = ATheme( Theme( 'default_inactive', 
                                    label = ( 0, 2 ), content = ( -15, 2 ) ) )
    
    # The default theme to use while the pointer hovers over the current
    # inactive list canvas item (if None is returned, the value of 
    # *theme_inactive* is used):
    theme_hover = ATheme( Theme( 'default_hover', 
                                 label = ( 0, 2 ), content = ( -15, 2 ) ) )
    
    # The title to use for the current list canvas item:
    title = Property # Str
    
    # The unique id of the current list canvas item:
    unique_id = Str
    
    # Can the current list canvas item be moved?
    can_move = Bool( True )
    
    # Can the current list canvas item be resized?
    can_resize = Bool( True )
    
    # Can the current list canvas item be minimized/restored?
    can_minimize = Bool( True )
    
    # Can the current drag object be dropped on the current item (or on the 
    # canvas itself if the current item is an instance of ListCanvas)? 
    can_drop = Property # Bool
    
    # The item or list of items to be added to the canvas when the current drag
    # object is dropped on the current item (or on the canvas itself of the 
    # current item is an instance of ListCanvas). A value of *None* means that
    # no object should be added to the canvas:
    dropped = Property # List/Instance/None
    
    # Can the current list canvas item be deleted (i.e. is close allowed)?
    can_delete = Bool( False )
    
    # Can the current list canvas item be closed? The possible values are:
    # - True: Yes.
    # - False: No.
    # - Modified: The item has been modified. Prompt the user whether the item
    #     should be closed before closing it.
    can_close = Enum( True, False, Modified )
    
    # Can the current list canvas item be dragged?
    can_drag = Bool( False )
    
    # Returns the draggable form of the current list canvas item (or None if
    # the current item can not be dragged):
    drag = Any( Missing )
    
    # Can the current list canvas item be cloned?
    can_clone = Bool( False )
    
    # Specifies the clone of the current list canvas item:
    clone = Any( Missing )
    
    # Specifies the Traits UI View to use for the current canvas list item when
    # it is added to the canvas:
    view = AView
    
    # Specifies the view model used to represent the current canvas list item
    # when it is added to the canvas:
    view_model = Instance( HasTraits )
    
    # Specifies the 'ListCanvasItemMonitor' object used to monitor the current
    # list canvas item:
    monitor = Instance( 'ListCanvasItemMonitor' )
    
    # Specifies the initial size to make the current canvas list item when it
    # is added to the canvas. The value is a tuple of the form: (width,height),
    # where the width and height values have the following meaning:
    # - <= 0: Use the default size.
    # - 0 < value <= 1: Use the specified fraction of the corresponding width
    #     or height dimension.
    # > 1: Use int(value) as the actual width or height specified in pixels.
    size = Tuple( Float, Float )
    
    # Specifies the initial position of the current canvas list item when it
    # is added to the canvas. The value is a tuple of the form: (x,y), where
    # x and y values have the following meaning:
    # - <= 0: Use the default coordinate.
    # - 0 < value <= 1: Use the specified fraction of the corresponding width
    #     or height dimension as the coordinate value.
    # > 1: Use int(value) as the actual x or y coordinate specified in pixels.
    position = Tuple( Float, Float )
    
    # Specified the tooltip to display for the current list canvas item:
    tooltip = Str
    
    #-- Events fired by the editor ---------------------------------------------
    
    # Event fired when the current list canvas item is closed:
    closed = Event
    
    # Event fired when the current list canvas item is activated:
    activated = Event
    
    # Event fired when the current list canvas item is de-activated:
    deactivated = Event

    #-- Traits that the editor listens for changes on --------------------------
    
    # Specifies the current message to display on the list canvas status line:
    status = Str
    
    #-- Traits set by the editor -----------------------------------------------
    
    # The current list canvas item (an instance of **ListCanvas** means the 
    # entire canvas):
    item = Instance( HasTraits )

    # The current item being dropped (if any):
    drop = Instance( HasTraits )    
    
    #-- Traits not used by the editor ------------------------------------------
    
    # The list of optional delegated adapters:
    adapters = List( IListCanvasAdapter, update = True )

    #-- Private Traits ---------------------------------------------------------
    
    # Cache of attribute handlers:
    cache = Any( {} )
    
    #-- Adapter methods called by the editor -----------------------------------

    def get_theme_active ( self, item ):
        """ Returns the theme to use for the specified item when it is active.
        """
        return self._result_for( 'get_theme_active', item )
        
    def get_theme_inactive ( self, item ):
        """ Returns the theme to use for the specified item when it is inactive.
        """
        return (self._result_for( 'get_theme_inactive', item ) or
                self._result_for( 'get_theme_active',   item ))
        
    def get_theme_hover ( self, item ):
        """ Returns the theme to use for the specified item when it is inactive
            and the mouse pointer is hovering over it.
        """
        return (self._result_for( 'get_theme_hover',    item ) or
                self._result_for( 'get_theme_inactive', item ) or
                self._result_for( 'get_theme_active',   item ))
                
    def get_title ( self, item ):     
        """ Returns the title to use for the specified item.
        """
        return self._result_for( 'get_title', item )
                
    def get_unique_id ( self, item ):     
        """ Returns the unique id for the specified item.
        """
        return self._result_for( 'get_unique_id', item )
                
    def get_can_move ( self, item ):     
        """ Returns whether or not the specified item can be moved on the
            canvas.
        """
        return self._result_for( 'get_can_move', item )
                
    def get_can_resize ( self, item ):     
        """ Returns whether or not the specified item can be resized on the
            canvas.
        """
        return self._result_for( 'get_can_resize', item )
                
    def get_can_minimize ( self, item ):     
        """ Returns whether or not the specified item can be minimized/restored
            on the canvas.
        """
        return self._result_for( 'get_can_minimize', item )
                
    def get_can_drop ( self, item, drop ):     
        """ Returns whether or not the specified droppable object can be
            dropped on the specified item.
        """
        return self._result_for( 'get_can_drop', item, drop )
        
    def get_dropped ( self, item, drop ):
        """ Returns the item (or list of items) to be added to the canvas when
            the specified droppable object is dropped on the specified item 
            (or canvas).
        """
        return self._result_for( 'get_dropped', item, drop )
                
    def get_can_delete ( self, item ):     
        """ Returns whether or not the specified item can be deleted from the
            canvas.
        """
        return self._result_for( 'get_can_delete', item )
                
    def get_can_close ( self, item ):     
        """ Returns whether or not the specified item can be closed on the 
            canvas.
        """
        return self._result_for( 'get_can_close', item )
                
    def get_can_drag ( self, item ):     
        """ Returns whether or not the specified item can be dragged.
        """
        return self._result_for( 'get_can_drag', item )
                
    def get_drag ( self, item ):
        """ Returns the draggable form of the specified item.
        """
        result = self._result_for( 'get_drag', item )
        if result is Missing:
            result = item
            
        return result
                
    def get_can_clone ( self, item ):     
        """ Returns whether or not the specified item can be cloned on the 
            canvas.
        """
        return self._result_for( 'get_can_clone', item )
                
    def get_clone ( self, item ):     
        """ Returns the clone of the specified item.
        """
        result = self._result_for( 'get_clone', item )
        if result is Missing:
            result = item.__class__( **item.get( transient = None ) )
            
        return result
                
    def get_view ( self, item ):     
        """ Returns the view to use for the specified item when it is added to
            the canvas.
        """
        return self._result_for( 'get_view', item )
                
    def get_view_model ( self, item ):     
        """ Returns the view model to use for the specified item when it is 
            added to the canvas.
        """
        return self._result_for( 'get_view_model', item )
                
    def get_monitor ( self, item ):
        """ Returns the 'ListCanvasItemMonitor' object used to monitor the
            specified item when it is added to the canvas.
        """
        result = self._result_for( 'get_monitor', item )
        if result is not None:
            if not isinstance( result, ListCanvasItemMonitor ):
                result = result()
            result.adapter = self
            
        return result
                
    def get_size ( self, item ):     
        """ Returns the size to use for the view of the specified item when it
            is added to the canvas.
        """
        return self._result_for( 'get_size', item )
                
    def get_position ( self, item ):     
        """ Returns the position to use for the view of the specified item when 
            it is added to the canvas.
        """
        return self._result_for( 'get_position', item )
                
    def get_tooltip ( self, item ):     
        """ Returns the tooltip to display for the specified item when the 
            mouse pointer is over its view on the canvas.
        """
        return self._result_for( 'get_tooltip', item )
                
    def set_closed ( self, item ):     
        """ Notifies that the specified item has been closed on the canvas.
        """
        self._result_for( 'set_closed', item )
                
    def set_activated ( self, item ):     
        """ Notifies that the specified item has been activated on the canvas.
        """
        self._result_for( 'set_activated', item )
                
    def set_deactivated ( self, item ):     
        """ Notifies that the specified item has been deactivated on the canvas.
        """
        self._result_for( 'set_deactivated', item )
    
    #-- Trait Event Handlers ---------------------------------------------------
    
    @on_trait_change( ' adapters' )
    def _on_adapters_changed ( self ):
        """ Handles any change to the list of sub-adapters by flushing the 
            handler cache.
        """
        self.cache = {}
        
    #-- Property Implementations -----------------------------------------------
    
    def _get_title ( self ):
        return user_name_for( self.item.__class__.__name__ )
        
    def _get_can_drop ( self ):
        result = self._result_for(
                      'get_can_receive_%s' % self.drop.__class__.__name__,
                      self.item, self.drop )
        if result is not Undefined:
            return result
            
        return False
                    
    def _get_dropped ( self ):
        result = self._result_for(
                      'get_received_%s' % self.drop.__class__.__name__,
                      self.item, self.drop )
        if result is not Undefined:
            return result
            
        return self.drop
        
    #-- Private Methods --------------------------------------------------------
    
    def _result_for ( self, name, item, drop = None ):
        """ Returns/Sets the value of the specified *name* attribute for the
            specified list canvas item.
        """
        # Split the name into a prefix (get_/set_) and a trait name: 
        prefix     = name[:4]
        trait_name = name[4:]   
        
        # Check to see if the item itself implements the required trait:
        if item.has_traits_interface( IListCanvasItem ):
            lci_name = 'list_canvas_item_' + trait_name
            if item.trait( lci_name ) is not None:
                if prefix == 'get_':
                    if ((trait_name == 'can_drop') and
                        (item.trait( 'list_canvas_item_drop' ) is not None)):
                        item.list_canvas_item_drop = drop
                        
                    return getattr( item, lci_name )
                
                setattr( item, lci_name, True )
                
                return
                
        # Otherwise, we'll handle the request:
        self.item = item
        self.drop = drop
        
        # Check to see if we have already cached a handler for the trait:
        item_class = item.__class__
        key        = '%s:%s' % ( item_class.__name__, name )
        handler    = self.cache.get( key )
        if handler is not None:
            return handler()
            
        # If not, check to see if any sub-adapter can handle the request:
        for i, adapter in enumerate( self.adapters ):
            adapter.item = item
            adapter.drop = drop
            if adapter.accepts and adapter.trait( trait_name ) is not None:
                if prefix == 'get_':
                    handler = lambda: getattr( adapter.set(
                                          item = self.item, drop = self.drop ),
                                          trait_name ) 
                else:
                    handler = lambda: setattr( adapter.set(
                                          item = self.item, drop = self.drop ),
                                          trait_name, True )
                 
                # If the handler is cacheable, then proceed normally:
                if adapter.is_cacheable:
                    break
                    
                # Otherwise, invoke it and we'll do same thing the next time:
                return handler()
        else:
            # Look for a specialized handler based on a class in the item's mro:
            for klass in item_class.__mro__:
                handler = self._get_handler_for(
                              '%s_%s' % ( klass.__name__, trait_name ), prefix )
                if handler is not None:
                    break
                    
            else:  
                # If none found, just use the generic trait for the handler:
                handler = self._get_handler_for( trait_name, prefix )
                
                # If we couldn't resolve it, it must be one of the
                # 'can_receive_xxx' or 'received_xxx' special cases, so indicate 
                # that the result is undefined:
                if handler is None:
                    return Undefined
            
        # Cache the resulting handler, so we don't have to look it up again:
        self.cache[ key ] = handler
        
        # Invoke the handler and return the result:
        return handler()

    def _get_handler_for ( self, name, prefix ):
        """ Returns the handler for a specified trait name (or None if not
            found).
        """
        if self.trait( name ) is not None:
            if prefix == 'get_':
                return lambda: getattr( self, name )
                
            return lambda: setattr( self, name, True )
            
        return None

#-------------------------------------------------------------------------------
#  'SnapInfo' class:  
#-------------------------------------------------------------------------------
                
class SnapInfo ( HasStrictTraits ):
    """ Defines item 'snapping' information for a canvas.
    """
    
    #-- Public Traits ----------------------------------------------------------
    
    # The magnetic 'snap' distance for edge snapping while dragging (a distance
    # of 0 means no snapping):
    distance = Range( 0, 15, 0 )
    
    #-- Trait View Definitions -------------------------------------------------
    
    view = View(
        Item( 'distance',
              editor  = ThemedSliderEditor(),
              tooltip = 'The magnetic snap distance for edge snapping while '
                        'dragging (a distance of 0 means no snapping)'
        )
    )
    
#-------------------------------------------------------------------------------
#  'GuideInfo' class:
#-------------------------------------------------------------------------------

class GuideInfo ( HasStrictTraits ):
    """ Defines 'guideline' information for a canvas.
    """
    
    #-- Public Traits ----------------------------------------------------------
    
    # When should guide lines be visible. The possible values are:
    # - always: Always display guide lines.
    # - never: Never display guide lines.
    # - drag: Display guide lines only during drag operations (move/resize).
    visible = Enum( 'never', 'always', 'drag' )
    
    # Is snapping allowed?
    snapping = Bool( True )
    
    # The color used for drawing guide lines:
    color = Color( 0xC8C8C8 )
    
    # The style used to draw guide lines:
    style = Enum( 'solid', 'dash', 'dot' )
    
    #-- Trait View Definitions -------------------------------------------------
    
    view = View(
        Item( 'visible',
              tooltip = 'Specifies when guide lines are visible'
        ),
        Item( 'snapping',
              editor  = ThemedCheckboxEditor(),
              tooltip = 'Specifies whether or not snapping is allowed?'
        ),
        Item( 'color',
              tooltip = 'Specifies the color used for drawing guide lines'
        ),
        Item( 'style',
              tooltip = 'Specifies the style used to draw guide lines'
        )
    )
    
#-------------------------------------------------------------------------------
#  'GridInfo' class:
#-------------------------------------------------------------------------------

class GridInfo ( HasStrictTraits ):
    """ Defines grid information for a coanvas.
    """
    
    #-- Public Traits ----------------------------------------------------------
    
    # When should the grid visible. The possible values are:
    # - always: Always display the grid.
    # - never: Never display the grid.
    # - drag: Display the grid only during drag operations (move/resize).
    visible = Enum( 'never', 'always', 'drag' )
    
    # Is snapping allowed?
    snapping = Bool( True )
    
    # The color used for drawing grid lines:
    color = Color( 0xC8C8C8 ) 
    
    # The style used for drawing grid lines:
    style = Enum( 'solid', 'dash', 'dot' )
    
    # The size of each grid cell (in pixels):
    size = Range( 5, 200, 50 )
    
    # The offset from the top-left corner of the canvas to the first grid cell
    # corner:
    offset = Range( 0, 200, 0 )
    
    #-- Trait View Definitions -------------------------------------------------
    
    view = View(
        Item( 'visible',
              tooltip = 'Specifies when grid lines are visible'
        ),
        Item( 'snapping',
              editor  = ThemedCheckboxEditor(),
              tooltip = 'Specifies whether or not snapping is allowed?'
        ),
        Item( 'color',
              tooltip = 'Specifies the color used for drawing grid lines'
        ),
        Item( 'style',
              tooltip = 'Specifies the style used to draw grid lines'
        ),
        Item( 'size',
              editor  = ThemedSliderEditor(),
              tooltip = 'Specifies the size of each grid cell in pixels'
        ),
        Item( 'offset',
              editor  = ThemedSliderEditor(),
              tooltip = 'Specifies the offset from the top-left corner of the '
                        'canvas to the first grid cell'
        )
    )
    
#-------------------------------------------------------------------------------
#  'ListCanvasPanel' class:  
#-------------------------------------------------------------------------------
        
class ListCanvasPanel ( ImagePanel ):
    """ Base class for list canvas widgets.
    """

    #-- Private Traits ---------------------------------------------------------
    
    # The layout bounds dictionary:
    layout = Any( {} )
 
    #-- ThemedWindow Method Overrides ------------------------------------------
    
    def refresh ( self, item = None ):
        """ Refreshes the contents of the control.
        """
        if self.control is not None:
            if item is None:
                self.control.Refresh()
            else:
                self.control.RefreshRect( wx.Rect( *self.layout[ item ] ), 
                                          False )
    
    #-- wx.Python Event Handlers -----------------------------------------------
           
    def _paint ( self, event ):
        """ Paint the background using the associated ImageSlice object.
        """
        global images
        
        # Note that we specifically skip our parent class's method 
        # implementation since it doesn't quite do what we want. So we just use
        # it's parent class's implementation:
        dc, slice = super( ImagePanel, self )._paint( event )
        
        # Draw each item in the layout dictionary:
        for name, bounds in self.layout.items():
            x, y, dx, dy = bounds
            
            # Check if the item is defined by a bitmap:
            bitmap = images.get( name )
            if bitmap is not None:
                # Display the item's bitmap:
                dc.DrawBitmap( images[ name ], x, y, True )
            else:
                # Otherwise, it must be a text string:
                text = getattr( self, name ).strip()
                if text != '':
                    dc.SetBackgroundMode( wx.TRANSPARENT )
                    dc.SetTextForeground( slice.label_color )
                    dc.SetFont( self.control.GetFont() )
                    dc.SetClippingRegion( x, y, dx, dy )
                    dc.DrawText( text, x, y )
                    dc.DestroyClippingRegion()
        
    def _size ( self, event ):
        """ Handles the control being resized.
        """
        self._layout()
        
        super( ListCanvasPanel, self )._size( event )
    
    #-- Mouse Event Handlers ---------------------------------------------------
    
    def normal_left_down ( self, x, y, event ):
        """ Handles the user pressing the left mouse button.
        """
        # Search for a layout item containing the (x,y) point:
        for name, bounds in self.layout.items():
            xb, yb, dxb, dyb = bounds
            if (xb <= x < (xb + dxb)) and (yb <= y < (yb + dyb)):
                # See if we have a handler for it:
                method = getattr( self, '%s_left_down' % name, None )
                if method is not None:
                    # Invoke the handler:
                    method( x, y, event )
                    return True
                
                method = getattr( self, '%s_left_up' % name, None )
                if method is not None:
                    self._pending_button = name
                    return True
                    
                break
                
        return False
                
    def normal_left_up ( self, x, y, event ):
        """ Handles the left mouse button being released.
        """
        name   = self._pending_button
        bounds = self.layout.get( name )
        if bounds is not None:
            self._pending_button = None
            xb, yb, dxb, dyb     = bounds
            if (xb <= x < (xb + dxb)) and (yb <= y < (yb + dyb)):
                getattr( self, '%s_left_up' % name )( x, y, event )
    
    #-- Private Methods --------------------------------------------------------
    
    def _layout ( self ):
        """ Lays out the contents of the control's title bar.
        """
        self.layout = {}
        dxt, dyt, descent, leading = self.control.GetFullTextExtent( 'Myj' )
        theme   = self.theme
        slice   = theme.image_slice
        dyt    += 4
        xtop    = slice.xtop
        xbottom = slice.xbottom
        if (dyt <= xtop) or (dyt <= xbottom):
            dxw, dyw = self.control.GetClientSizeTuple()
            label    = theme.label
            xo       = label.left
            yo       = label.top
            if (dyt <= xtop) and (xtop >= xbottom):
                yt = yo + ((xtop - dyt + 4) / 2)
                yc = (2 * yo) + xtop
            else:
                yt = yo + dyw - ((xbottom + dyt - 2) / 2)
                yc = (2 * (yo + dyw)) - xbottom
            
            xl = xo  + slice.xleft
            xr = dxw - slice.xright - label.right
              
            self._layout_items ( xl, xr, yc, yt, dyt - 4 )
            
    def _layout_items ( self, xl, xr, yc, yt, dyt ):
        """ Must be overridden in sub-class.
        """
        raise NotImplementedError
            
    def _layout_button ( self, name, x, y, direction = -1 ):
        """ Lays out the position of an image button.
        """
        global images
        
        bm = images[ name ]
        if isinstance( bm, ImageResource ):
            images[ name ] = bm = bm.create_image().ConvertToBitmap()
            
        dx = bm.GetWidth()
        dy = bm.GetHeight()
        
        if direction < 0:
            x -= dx
            rx = x - 2
        else:
            rx = x + dx + 2
            
        self.layout[ name ] = ( x, (y - dy) / 2, dx, dy )
        
        return rx
        
#-------------------------------------------------------------------------------
#  'ListCanvasItem' class:
#-------------------------------------------------------------------------------

class ListCanvasItem ( ListCanvasPanel ):
    """ Defines a list canvas item, one or more of which can be added to a list 
        canvas.
    """
    
    #-- Public Traits ----------------------------------------------------------
    
    # The HasTraits object this is a list canvas item for:
    object = Instance( HasTraits )
    
    # The list canvas this item is displayed on:
    canvas = Instance( 'ListCanvas' )
    
    # The monitor object (if any) associated with this item:
    monitor = Instance( 'ListCanvasItemMonitor' )
    
    # The current mouse event state (override):
    state = 'inactive'
    
    # The position of the item on the list canvas:
    position = Property
    
    # The size of the item on the list canvas:
    size = Property
    
    # The bounds of the item on the list canvas:
    bounds = Property
    
    # The list of immediate neighbors of the item:
    neighbors = Property # List( ListCanvasItem )
    
    # Is the item initially hidden?
    hidden = Bool( False )
    
    # The item has been moved or resized:
    moved = Event
    
    #-- Private Traits ---------------------------------------------------------
    
    # The title of this item:
    title = Str
    
    # The Traits UI for the associated object:
    ui = Instance( UI )
    
    # Is the item minimized?
    minimized = Bool( False )
    
    #-- Public Methods ---------------------------------------------------------
    
    def dispose ( self ):
        """ Removes the item from the canvas it is contained in.
        """
        # Unhook the monitor:
        self.monitor = None
        
        # Close the Traits UI contained in the item:
        if self.ui is not None:
            self.ui.dispose()
            
        # Now destroy the list canvas item control:
        if self.control is not None:
            self.control.Destroy()
            self.control = None

    def initialize_position ( self ):
        """ Initializes the position and size of the item.
        """
        # fixme: This is a hack to prevent 'flashing' when a clone is created:
        if self.hidden:
            self.hidden = False
            self.control.Show( False )
            
            return
            
        # Get the values needed to compute the initial postion and size of the
        # item:
        canvas   = self.canvas
        adapter  = canvas.adapter
        bdx, bdy = self.best_size
        cdx, cdy = canvas.size
        x, y     = adapter.get_position( self.object )
        dx, dy   = adapter.get_size( self.object )
            
        # Calculate the initial size of the item:
        if dx <= 0.0:
            dx = bdx
        elif dx <= 1.0:
            dx = int( dx * cdx )
        else:
            dx = int( dx )
            
        if dy <= 0.0:
            dy = bdy
        elif dy <= 1.0:
            dy = int( dy * cdy )
        else:
            dy = int( dy )
        
        # Calculate the initial position of the item:
        if x <= 0.0:
            if y > 0.0:
                x = 0
        elif x <= 1.0:
            x = int( x * cdx )
        else:
            x = int( x )
        
        if y <= 0.0:
            if x <= 0.0:
                x, y = canvas.initial_position_for( dx, dy )
            else:
                y = 0
        elif y <= 1.0:
            y = int( y * cdy )
        else:
            y = int( y )
            
        # Set the item's position and size:
        self.control.SetDimensions( x, y, dx, dy )
        
        # Set the tooltip for the control:
        self._set_tooltip()
        
        # Set up to handle drop events:
        self.control.SetDropTarget( PythonDropTarget( self ) )
        
    def resize ( self, mode, xo, yo, dxo, dyo, dx, dy ):
        """ Resize the control while in drag mode.
        """
        # Adjust axes that are not being dragged:
        if (mode & 0x05) == 0:
            dx = 0
            
        if (mode & 0x0A) == 0:
            dy = 0
        
        # Adjust the x-axis size and position:
        canvas = self.canvas
        if (mode & 0x04) != 0:
            dxs = canvas.snap_x( xo, dx )
            if (mode & 0x01) != 0:
                xo  += dxs
                dxo -= dxs
            elif dxs == dx:
                xo += canvas.snap_x( xo + dxo, dx )
            else:
                xo += dxs
        elif (mode & 0x01) != 0:
            dxo += canvas.snap_x( xo + dxo, dx )
            
        # Adjust the y-axis size and position:
        if (mode & 0x08) != 0:
            dys = canvas.snap_y( yo, dy )
            if (mode & 0x02) != 0:
                yo  += dys
                dyo -= dys
            elif dys == dy:
                yo += canvas.snap_y( yo + dyo, dy )
            else:
                yo += dys
        elif (mode & 0x02) != 0:
            dyo += canvas.snap_y( yo + dyo, dy )
            
        # Get the current control position and size:
        cx,  cy  = self.position
        cdx, cdy = self.size
        
        # Update the position and size of the control:
        if (xo != cx) or (yo != cy) or (dxo != cdx) or (dyo != cdy):
            self.bounds = ( xo, yo, dxo, dyo )
            
        # Return the net change:
        return ( (xo - cx), (yo - cy), (dxo - cdx), (dyo - cdy) )
        
    def activate ( self ):
        """ Activates this list canvas item.
        """
        self.canvas.activate( self )
        
    #-- Property Implementations -----------------------------------------------
    
    def _get_position ( self ):
        return self.control.GetPositionTuple()
        
    def _set_position ( self, position ):
        old_position = self.control.GetPositionTuple()
        if position != old_position:
            old_bounds = self.bounds
            self.control.SetPosition( position )
            self.trait_property_changed( 'position', old_position, position )
            self.trait_property_changed( 'bounds',   old_bounds,   self.bounds )
        
    def _get_size ( self ):
        return self.control.GetSizeTuple()
        
    def _set_size ( self, size ):
        old_size = self.control.GetSizeTuple()
        if size != old_size:
            old_bounds = self.bounds
            self.control.SetSize( size )
            self.trait_property_changed( 'size',   old_size,   size )
            self.trait_property_changed( 'bounds', old_bounds, self.bounds )
            
    def _get_bounds ( self ):
        return (self.control.GetPositionTuple() + self.control.GetSizeTuple())
        
    def _set_bounds ( self, bounds ):
        control    = self.control
        old_bounds = control.GetPositionTuple() + control.GetSizeTuple()
        if bounds != old_bounds:
            self.control.SetDimensions( *bounds )
            self.trait_property_changed( 'bounds',   old_bounds,     bounds )
            self.trait_property_changed( 'position', old_bounds[:2], bounds[:2])
            self.trait_property_changed( 'size',     old_bounds[2:], bounds[2:])
            
    def _get_neighbors ( self ):
        return self.canvas.neighbor_set_for( self )
            
    #-- Trait Event Handlers ---------------------------------------------------
    
    def _object_changed ( self, object ):
        """ Handles the 'object' trait being changed.
        """
        canvas     = self.canvas
        adapter    = canvas.adapter
        self.theme = adapter.get_theme_inactive( object )
        control    = self.create_control( canvas.canvas )
        self.title = adapter.get_title( object ) 
        view_model = adapter.get_view_model( object ) or object
        self.ui    = ui = view_model.edit_traits(
                              parent = control, 
                              view   = adapter.get_view( object ),
                              kind   = 'subpanel' ).set(
                              parent = canvas.editor.ui )
            
        control.GetSizer().Add( ui.control, 1, wx.EXPAND )
        
        # Check to see if the object is list canvas aware:
        if object.has_traits_interface( IListCanvasAware ):
            object.list_canvas_item = self
        
    def _monitor_changed ( self, old, new ):
        """ Handles the 'monitor' trait being changed.
        """
        if old is not None:
            old.item = None
            
        if new is not None:
            new.item = self
        
    def _state_changed ( self, state ):
        """ Handles the control 'state' being changed.
        """
        self.theme = getattr( self.canvas.adapter, 'get_theme_' + state )(
                              self.object )
                              
        # If we have been activate, make sure we are on top of every other item:                              
        if state == 'active':
            self.control.Raise()
                              
    def _theme_changed ( self, theme ):
        """ Handles the 'theme' trait being changed.
        """
        super( ListCanvasItem, self )._theme_changed( theme )
        
        control = self.control
        if control is not None:
            self.ui.control.SetBackgroundColour( control.GetBackgroundColour() )
            
    @on_trait_change( 'minimized' )
    def _on_layout ( self ):
        """ Handles a trait requiring layout to be run being changed.
        """
        self._layout()
            
    @on_trait_change( 'title' )
    def _on_update ( self ):
        """ Handles a trait changing that requires the item to be refreshed on
            the display.
        """
        self.refresh()
        
    #-- Mouse Event Handlers ---------------------------------------------------
        
    def active_motion ( self, x, y, event ):
        """ Handles a mouse motion event while in the active state.
        """
        self._set_cursor( x, y )
        
    def active_left_down ( self, x, y, event ):
        """ Handles the user pressing the left mouse button while in the active
            state.
        """
        mode = self._set_cursor( x, y )
        if (mode == MOVE_MODE) and self.normal_left_down( x, y, event ):
            return
            
        if mode > 0:
            self.control.ReleaseMouse()
            self.canvas.begin_drag( self, mode, x, y, event )
        
    def active_left_up ( self, x, y, event ):
        """ Handles the user releasing the left mouse button while in the active
            state.
        """
        self._drag_mode = None
        self._set_cursor( x, y )
        
        self.normal_left_up( x, y, event )
    
    def inactive_motion ( self, x, y, event ):
        """ Handles a mouse motion event while in the inactive state.
        """
        self.state = 'hover'
        self.control.CaptureMouse()
        self._set_cursor( x, y )
        self._set_tooltip()
        
    def hover_motion ( self, x, y, event ):
        """ Handles a mouse motion event while in the hover state.
        """
        if not self.in_control( x, y ):
            self.state = 'inactive'
            self.control.ReleaseMouse()
            return
            
        self._set_cursor( x, y )
        
    def hover_left_down ( self, x, y, event ):
        """ Handles the user pressing the left mouse button while in the 
            inactive state.
        """
        self.activate()
        self.control.ReleaseMouse()
        self.active_left_down( x, y, event )
        
    #-- Toolbar Button Event Handlers ------------------------------------------
    
    def clone_left_down ( self, x, y, event ):
        """ Handles the user clicking the 'clone' button.
        """
        canvas = self.canvas
        clone  = canvas.adapter.get_clone( self.object )
        if clone is not None:
            self.control.ReleaseMouse()
            canvas.add_object( clone, hidden = True )
            do_later( self._drag_clone, x, y, event )
    
    def drag_left_down ( self, x, y, event ):
        """ Handles the user clicking the 'drag' button.
        """
        drag_object = self.canvas.adapter.get_drag( self.object )
        if drag_object is not None:
            self.control.ReleaseMouse()
            PythonDropSource( self.control, drag_object )
    
    def minimize_left_up ( self, x, y, event ):
        """ Handles the user clicking the 'minimize' button.
        """
        has_lego_set = event.ControlDown()
        if has_lego_set:
            strict = event.ShiftDown()
            items  = self.canvas.lego_set_for( self, strict )
            
        dxi, dyi, dyc = self._minimize()
        
        if has_lego_set:
            xi, yi = self.position
            for item in items:
                x, y, dx, dy = item.bounds
                if strict:
                    if (y == yi) and (dy == dyi):
                        item._minimize()
                        continue
                        
                elif max( y, yi ) < min( y + dy, yi + dyi ):
                    item._minimize()
                    continue
                        
                if y >= (yi + dyi):
                    item.position = ( x, y + dyc )
        
        # Update the canvas:
        self.canvas.update()
    
    def maximize_left_up ( self, x, y, event ):
        """ Handles the user clicking the 'maximize' button.
        """
        strict = event.ShiftDown()
        items  = self.canvas.lego_set_for( self, False )
        
        dxi, dyi, dyc = self._maximize()
        
        xi, yi, dxin, dyin = self.bounds
        for item in items:
            x, y, dx, dy = item.bounds
            if strict:
                if (y == yi) and (dy == dyi):
                    item._maximize( dyin )
                    continue
                    
            elif max( y, yi ) < min( y + dy, yi + dyi ):
                item._maximize()
                continue
                
            if y >= (yi + dyi):
                item.position = ( x, y + dyc )
        
        # Update the canvas:
        self.canvas.update()
    
    def close_left_up ( self, x, y, event ):
        """ Handles the user clicking the 'close' button.
        """
        adapter = self.canvas.adapter
        rc      = adapter.get_can_close( self.object )
        if rc == Modified:
            rc = (confirm( self.control, 
                           'Changes have been made.\n\nAre you sure you want '
                           'to close this item?', 'Confirm close' ) == YES)
                          
        if rc:
            self.canvas.remove_item( self )
            adapter.set_closed( self.object )
        
    #-- Drag and Drop Event Handlers -------------------------------------------

    def wx_dropped_on ( self, x, y, data, drag_result ):
        """ Handles an object being dropped on a list item.
        """
        canvas = self.canvas
        xi, yi = self.position
        x     += xi
        y     += yi
        if not isinstance( data, SequenceTypes ):
            # Handle the case of just a single item being dropped:
            canvas.dropped_on( self, data, x, y )
        else:
            # Handles the case of a list of items being dropped:
            for item in data:
                canvas.dropped_on( self, item, x, y )
            
        # Return a successful drop result:
        return drag_result
         
    def wx_drag_any ( self, x, y, data, drag_result ):
        """ Handles a Python object being dragged over the tree.
        """
        if isinstance( data, SequenceTypes ):
            rc = wx.DragNone
            for item in data:
                rc = self.wx_drag_any( x, y, item, drag_result )
                if rc == wx.DragNone:
                    break
                    
            return rc
           
        # If the adapter says it is OK to drop the data here, then indicate the
        # data can be dropped:
        if self.canvas.adapter.get_can_drop( self.object, data ):
            return drag_result
            
        # Else indicate that we will not accept the data:
        return wx.DragNone

    #-- Private Methods --------------------------------------------------------

    def _minimize ( self ):
        """ Minimizes the item and returns the original size.
        """
        dxi, dyi = self.size
        if self.minimized:
            return ( dxi, dyi, 0 )
            
        control = self.ui.control
        control.Show( False )
        control.SetSize( wx.Size( 0, 0 ) )
        
        self._original_size = ( dxi, dyi )
        dxa, dya  = self.adjusted_size
        self.size = ( dxi, dya ) 
        
        self.minimized = True
            
        return ( dxi, dyi, dya - dyi )
        
    def _maximize ( self, height = None ):
        """ Maximizes the item and returns the original size.
        """
        dxi, dyi = self.size
        if not self.minimized:
            return ( dxi, dyi, 0 )
            
        self.ui.control.Show( True )
        
        dxo, dyo = self._original_size
        if height is not None:
            dyo = height
        self.size = ( dxo, dyo )
        del self._original_size
        
        self.minimized = False
        
        return ( dxi, dyi, dyo - dyi )        
        
    def _drag_clone ( self, x, y, event ):
        """ Drag the new created clone of this item.
        """
        # fixme: Shouldn't be reaching into the canvas items to get the clone...
        item   = self.canvas.items[-1]
        xs,  ys  = self.position
        dxs, dys = self.size
        item.control.SetDimensions( xs, ys, dxs, dys )
        item.control.Show( True )
        self.canvas.begin_drag( item, MOVE_MODE, x, y, event )
   
    def _set_cursor ( self, x, y ):
        """ Sets the correct mouse cursor for a specified mouse position.
        """
        n      = 4
        theme  = self.theme
        border = theme.border
        cursor = wx.CURSOR_ARROW
        dx, dy = self.size
        mode   = 0
        if ((x >= border.left) and (x < (dx - border.right)) and 
            (y >= border.top)  and (y < (dy - border.bottom))):
            adapter = self.canvas.adapter
            
            # Check if the pointer is in a valid 'resize' position:
            if adapter.get_can_resize( self.object ):
                if x < (border.left + n):
                    cursor = wx.CURSOR_SIZEWE
                    mode   = 5
                    if y < (border.top + n):
                        cursor = wx.CURSOR_SIZENWSE
                        mode   = 15
                    elif y >= (dy - border.bottom - n):
                        cursor = wx.CURSOR_SIZENESW
                        mode   = 7
                elif x >= (dx - border.right - n):
                    cursor = wx.CURSOR_SIZEWE
                    mode   = 1
                    if y < (border.top + n):
                        cursor = wx.CURSOR_SIZENESW
                        mode   = 11
                    elif y >= (dy - border.bottom - n):
                        cursor = wx.CURSOR_SIZENWSE
                        mode   = 3
                elif (y < (border.top + n)) or (y >= (dy - border.bottom - n)):
                    cursor = wx.CURSOR_SIZENS
                    mode   = 2
                    if y < (border.top + n):
                        mode = 10
                 
            # If not, check if the pointer is in a valid 'move' position:
            if (mode == 0) and adapter.get_can_move( self.object ):
                slice = theme.image_slice
                if ((y < max( slice.xtop + theme.content.top, 6)) or
                    (y >= (dy - max( slice.xbottom - theme.content.bottom, 
                                     6 )))):
                    mode = MOVE_MODE
                
        self.control.SetCursor( get_cursor( cursor ) )
        
        return mode
        
    def _set_tooltip ( self ):
        """ Sets the tooltip for the item's control.
        """
        self.control.SetToolTip( 
            wx.ToolTip( self.canvas.adapter.get_tooltip( self.object ) ) )
    
    #-- ListCanvasPanel Method Overrides ---------------------------------------
    
    def _layout_items ( self, xl, xr, yc, yt, dyt ):
        """ Lays out the contents of the item's title bar.
        """
        adapter = self.canvas.adapter
        object  = self.object
        
        # fixme: Add support for the 'feature' button...
        if adapter.get_can_delete( object ):
            xr = self._layout_button( 'close', xr, yc )
         
        if adapter.get_can_minimize( object ):
            if self.minimized:
                xr = self._layout_button( 'maximize', xr, yc )
            else:
                xr = self._layout_button( 'minimize', xr, yc )
        
        if adapter.get_can_drag( object ):
            xr = self._layout_button( 'drag', xr, yc )
            
        if adapter.get_can_clone( object ):
            xr = self._layout_button( 'clone', xr, yc )
        # fixme: Add support for the 'select' button...
        
        # Add the layout information for the title:
        self.layout[ 'title' ] = ( xl, yt, xr - xl, dyt )
    
#-------------------------------------------------------------------------------
#  'ListCanvas' class:
#-------------------------------------------------------------------------------

class ListCanvas ( ListCanvasPanel ):
    """ Defines the main list canvas editor widget, which contains and manages
        all of the list canvas items.
    """
    
    #-- Public Traits ----------------------------------------------------------
    
    # The preferred position for the next item added to the canvas:
    preferred_position = Tuple( Int, Int )
    
    #-- Private Traits ---------------------------------------------------------
    
    # Is the canvas scrollable?
    scrollable = Bool( False )
    
    # The current set of items on the canvas:
    items = List( ListCanvasItem )
    
    # The current active item (if any):
    active_item = Instance( ListCanvasItem )
    
    # The adapter used to control canvas operations:
    adapter = Instance( ListCanvasAdapter )
   
    # The snapping information to use:
    snap_info = Instance( SnapInfo, () )
    
    # The guide line information to use:
    guide_info = Instance( GuideInfo, () )
    
    # The grid information to use:
    grid_info = Instance( GridInfo, () )

    # What operations are allowed on the list canvas:
    operations = CanvasOperations
    
    # The list of classes that can be added to the canvas using the canvas
    # toolbar and/or context menu:
    add = List
    
    # The current position of the canvas:
    position = Property
    
    # The current size of the canvas:
    size = Property
    
    # The wx Control acting as the list canvas:
    canvas = Instance( wx.Window )
    
    # The Traits editor the list canvas is associated with:
    editor = Instance( Editor )
    
    # fixme: This is a hack used when cloning list item's
    # Should the next list canvas item created be initially hidden:
    hidden = Bool( False )
    
    # The current adapter status:
    status = Delegate( 'adapter' )
    
    # Can the canvas use the 'fast layout' algorithm (used when all canvas
    # items are being replaced at once):
    fast_layout = Bool( False )
    
    # The menu used to select an item to be added:
    add_menu = Property( depends_on = 'add' ) # Instance( Menu )
    
    # The list of classes referenced by the 'add_menu' and derived from the
    # 'add' list:
    add_classes = Any( [] )
    
    #-- Public Methods ---------------------------------------------------------
    
    def create_control ( self, parent, scrollable = False ):
        """ Creates the underlying wx.Panel control.
        """
        control = super( ListCanvas, self ).create_control( parent )
        
        self.scrollable = scrollable
        if scrollable:
            self.canvas = canvas = wx.ScrolledWindow( control )
            canvas.SetScrollRate( 1, 1 )
            canvas.SetMinSize( wx.Size( 0, 0 ) )
        else:
            self.canvas = canvas = wx.Panel( control, -1, 
                                           style = wx.TAB_TRAVERSAL          |
                                                   wx.FULL_REPAINT_ON_RESIZE | 
                                                   wx.CLIP_CHILDREN )
                                                   
        canvas.SetBackgroundColour( control.GetBackgroundColour() )
                                                   
        # Initialize the wx event handlers for the canvas control:                                                   
        init_wx_handlers( self.canvas, self, 'canvas' )
        
        # Set up to handle drop events:
        canvas.SetDropTarget( PythonDropTarget( self ) )
            
        control.GetSizer().Add( self.canvas, 1, wx.EXPAND )
        
        return control
        
    def create_object ( self, object ):
        """ Creates a specified HasTraits object as a new list canvas item.
        """ 
        result = ListCanvasItem( canvas  = self, 
                                 hidden  = self.hidden ).set( 
                                 object  = object,
                                 monitor = self.adapter.get_monitor( object ) )
                                         
        self.hidden = False
        
        return result
        
    def replace_items ( self, items = [], i = 0, j = -1 ):
        """ Replaces the [i:j] items in the current items list with the 
            specified set of replacement items.
        """
        self_items = self.items
        
        # If 'j' was not specified, replace all items until the end of the list:
        if j < 0:
            j = len( self_items )
        
        # If the currently active item is in the group being deleted, then
        # indicate that there is no active item currently:
        if self.active_item in self_items[i:j]:
            self.active_item = None
            
        # Destroy all items being removed from the list:
        for item in self_items[i:j]:
            item.dispose()
            
        # Delete the removed items from the list:
        del self_items[i:j]
        
        # Initialize each item's position, then add it to the list:
        for item in items:
            item.initialize_position()
            self_items.insert( i, item )
            i += 1
            
        # Update the canvas bounds (if necessary):
        self._adjust_size()
        
    def remove_item ( self, item ):
        """ Removes a specified list canvas item from the canvas.
        """
        del self.editor.value[ self.items.index( item ) ]
        
    def add_object ( self, object, hidden = False ):
        """ Adds a new object to the canvas.
        """
        self.hidden = hidden
        self.editor.value.append( object )
        
    def initial_position_for ( self, dx, dy ):
        """ Returns the initial position for an item of the specified width and
            height.
        """
        x, y = self.preferred_position
        if (x > 0) or (y > 0):
            self.preferred_position = ( 0, 0 )
            return self.best_position_for( x, y, dx, dy )
        
        if self.fast_layout:
            # Fast layout mode is used when the contents of the canvas are being
            # completely replaced, and so all of the items need to be laid out.
            # The 'fast_layout' takes advantage of that by simply laying out 
            # each item just after the last item laid out, and then saving the
            # new layout position for the next item:
            x, y, max_dy = self._last_layout
            cdx, cdy     = self.size
            
            if (x + dx) > cdx:
                x      = 0
                y     += max_dy
                max_dy = dy
            else:
                max_dy = max( max_dy, dy )
                
            self._last_layout = ( x + dx, y, max_dy )
                
            return ( x, y )
            
        xmax = ymax = ynext = 0
        cdx, cdy = self.size
        
        for item in self.items:
            x, y     = item.position
            idx, idy = item.size
            if y > ymax:
                xmax, ymax, ynext = x + idx, y, y + idy
            elif y == ymax:
                xmax  = max( xmax, x + idx )
                ynext = max( ynext, y + idy )
        
        if (xmax + dx) > cdx:
            ymax = ynext
            xmax = 0
            
        return ( xmax, ymax )
        
    def best_position_for ( self, x, y, dx, dy, vertical = True ):
        """ Returns the best position for an item of the specified width and
            height that is closest to a specified position.
        """
        # Start with the entire canvas (extended in the favored direction):
        cdx, cdy = self.size
        if vertical:
            rects = [ ( 0, 0, cdx, 1000000 ) ]
        else:
            rects = [ ( 0, 0, 1000000, cdy ) ]
        
        # Now carve up the space in a set of unfilled rectangles big enough to
        # hold the target rectangle:
        for item in self.items:
            new_rects = []
            xli, yti = item.position
            dxi, dyi = item.size
            xri      = xli + dxi
            ybi      = yti + dyi
            for rect in rects:
                xlr, ytr, xrr, ybr = rect
                if (xri <= xlr) or (xli >= xrr) or (ybi <= ytr) or (yti >= ybr):
                    # No intersection, pass the rectangle through unchanged:
                    new_rects.append( rect )
                else:
                    # Otherwise, split it up into 4 smaller rectangles, but
                    # only pass ones big enough to hold the target rectangle:
                    if (xli - xlr) >= dx:
                        new_rects.append( ( xlr, ytr, xli, ybr ) )
                    if (xrr - xri) >= dx:
                        new_rects.append( ( xri, ytr, xrr, ybr ) )
                    if (yti - ytr) >= dy:
                        new_rects.append( ( xlr, ytr, xrr, yti ) )
                    if (ybr - ybi) >= dy:
                        new_rects.append( ( xlr, ybi, xrr, ybr ) )
                        
            # Set up this pass's result for use with the next rectangle:
            rects = new_rects
            
        # Find the rectangle closest to the desired point from the set of
        # rectangles large enough to hold the target rectangle:
        best_dist = 1000000000
        for xl, yt, xr, yb in rects:
            dxl, dxr, dyt, dyb = x - xl, x - xr, y - yt, y - yb
            
            if (dxl >= 0) and (dxr < 0):
                dxb = 0
            else:
                dxb = min( abs( dxl ), abs( dxr ) )
                
            if (dyt >= 0) and (dyb < 0):
                dyb = 0
            else:
                dyb = min( abs( dyt ), abs( dyb ) )
                
            dist = (dxb * dxb) + (dyb * dyb)
            if dist < best_dist:
                best_rect = ( xl, yt, xr, yb )
                if dist == 0:
                    break
                best_dist = dist
            
        # Get the bounds of the selected rectangle:
        xl, yt, xr, yb = best_rect
        
        # Now determine the position within the selected rectangle closest to 
        # the desired point but still allowing the target retangle to be 
        # completely contained within the selected rectangle:
        x, y = min( max( x, xl ), xr - dx ), min( max( y, yt ), yb - dy )
        
        # Set up snapping guides if needed:
        if ((self.snap_info.distance > 0) and self.guide_info.snapping):
            self._drag_guides = self._guide_lines( self._drag_set )
        
        # Now perform snapping (if enabled):
        dxs = self.snap_x( x )
        if dxs == 0:
            x += self.snap_x( x + dx )
        else:
            x += dxs
            
        dys = self.snap_y( y )
        if dys == 0:
            y += self.snap_y( y + dy )
        else:
            y += dys
            
        # Discard the guide lines (if any):
        self._drag_guides = None
        
        # Return the best position:
        return ( min( max( x, xl ), xr - dx ), min( max( y, yt ), yb - dy ) )
        
    def adjust_positions_y ( self, x, y, dx0, dx, dy ):
        """ Adjust the position of all windows that are immediately below and
            lined up with the specified window position.
        """
        for item in self.items:
            xi,  yi  = item.position
            dxi, dyi = item.size
            if (x == xi) and (y == yi) and (dx0 == dxi):
                item.position = ( xi, yi + dy )
                item.size     = ( dx, dyi )
                self.adjust_positions_y( x, yi + dyi, dx0, dx, dy )
                self.adjust_positions_xl( xi, yi, dyi, dy )
                self.adjust_positions_xr( xi + dxi, yi, dyi, dx - dx0, dy )
                break
                
    def adjust_positions_xl ( self, x, y, dy0, dy ):
        for item in self.items:
            xi,  yi  = item.position
            dxi, dyi = item.size
            if (x == (xi + dxi)) and (y == yi) and (dy0 == dyi):
                item.position = ( xi, yi + dy )
                self.adjust_positions_y( xi, yi + dyi, dxi, dxi, dy )
                self.adjust_positions_xl( xi, yi, dyi, dy )
                break
                
    def adjust_positions_xr ( self, x, y, dy0, dx, dy ):
        for item in self.items:
            xi,  yi  = item.position
            dxi, dyi = item.size
            if (x == xi) and (y == yi) and (dy0 == dyi):
                item.position = ( xi + dx, yi + dy )
                self.adjust_positions_y( xi, yi + dyi, dxi, dxi, dy )
                self.adjust_positions_xr( xi + dxi, yi, dyi, dx, dy )
                break
                
    def lego_set_for ( self, item, strict ):
        """ Return the 'lego' (i.e. connected) set for the specified item.
        """
        return self._lego_set_for( item, strict, set() )
        
    def _lego_set_for ( self, item, strict, result ):
        result.add( item )
         
        x,  y  = item.position
        dx, dy = item.size
        for itemi in self.items:
            if itemi not in result:
                xi,  yi  = itemi.position
                dxi, dyi = itemi.size
                if strict:
                    if ((((x == xi) and (dx == dxi)) and 
                          (((yi + dyi) == y) or ((y + dy) == yi))) or
                         (((y == yi) and (dy == dyi)) and 
                          (((xi + dxi) == x) or ((x + dx) == xi)))):
                        self._lego_set_for( itemi, strict, result )
                else:
                    xl, xr = max( x, xi ), min( x + dx, xi + dxi )
                    yt, yb = max( y, yi ), min( y + dy, yi + dyi )
                    if (((xl < xr) and 
                         (((yi + dyi) == y) or ((y + dy) == yi))) or
                        ((yt < yb) and 
                         (((xi + dxi) == x) or ((x + dx) == xi)))):
                        self._lego_set_for( itemi, strict, result )
                    
        return result
                
    def neighbor_set_for ( self, item ):
        """ Return the set of neighbors which share an edge with the specified 
            item.
        """
        result = []
        x,  y  = item.position
        dx, dy = item.size
        dx     += x
        dy     += y
        for itemi in self.items:
            xi,  yi  = itemi.position
            dxi, dyi = itemi.size
            if (((max( x, xi ) < min( dx, xi + dxi )) and 
                 (((yi + dyi) == y) or (dy == yi))) or
                ((max( y, yi ) < min( dy, yi + dyi )) and 
                 (((xi + dxi) == x) or (dx == xi)))):
                result.append( itemi )
                    
        return result
        
    def activate ( self, item ):
        """ Activates a specified list canvas item.
        """
        # If there is actually a change in the current active item:
        active_item = self.active_item
        if item is not active_item:
            
            # Deactivate the previous active item (if any):
            if active_item is not None:
                active_item.state = 'inactive'
                self.adapter.set_deactivated( active_item.object ) 
                
            # Active the new item (if any):
            self.active_item = item
            if item is not None:
                item.state = 'active'
                self.adapter.set_activated( item.object )
                
    def begin_drag ( self, item, mode, x, y, event ):
        """ Handles a drag operation for a specified list item.
        """
        x, y            = self._event_xy( x, y )
        x0, y0          = item.position
        dx, dy          = item.size
        x1, y1          = self.position
        self._drag_item = item
        if event.ControlDown():
            self._drag_set = self.lego_set_for( item, event.ShiftDown() )
        else:
            self._drag_set = set( [ item ] )
        self._drag_moved    = set()
        self._drag_info     = ( mode, x0, y0, dx, dy, x0 + x1 + x, y0 + y1 + y )
        self.state          = 'dragging'
        self._drag_snapping = (not event.AltDown())
        if ((self.snap_info.distance > 0) and self._drag_snapping and 
             self.guide_info.snapping):
            self._drag_guides = self._guide_lines( self._drag_set )
        self.control.CaptureMouse()
        self._refresh_canvas_drag( True )
        
    def snap_x ( self, x, dx = 0 ):
        """ Adjust an x-coordinate to take into account any grid or guide line
            snapping in effect.
        """
        # If snapping distance is 0, then it is effectively turned off, so just
        # return the original delta:
        snap = self.snap_info.distance
        if (snap == 0) or (not self._drag_snapping):
            return dx
            
        # Compute the adjusted x-coordinate:
        xt = x + dx
        
        # Check to see if grid snapping is allowed:
        gi = self.grid_info
        if gi.snapping:
            
            # Compute the nearest grid point to the left of the point:
            n  = (xt - gi.offset) / gi.size
            x0 = (n * gi.size) + gi.offset
            
            # If it is within snapping distance, return the snapped delta:
            if abs( xt - x0 ) <= snap:
                return (x0 - x)
                
            # Compute the nearest grid point to the right of the point:
            x0 += gi.size
            
            # If it is within snapping distance, return the snapped delta:
            if abs( xt - x0 ) <= snap:
                return (x0 - x)
                
        # Check to see if guide line snapping is allowed:
        if self.guide_info.snapping:
            xs, ys = self._drag_guides
            
            # Check to see if the point is within snapping distance of any of
            # the guide lines:
            for x0 in xs.keys():
                delta = abs( xt - x0 )
                if delta <= snap:
                    snap = delta
                    dx   = x0 - x
                
        # Return the delta:
        return dx
        
    def snap_y ( self, y, dy = 0 ):
        """ Adjust an y-coordinate to take into account any grid or guide line
            snapping in effect.
        """
        # If snapping distance is 0, then it is effectively turned off, so just
        # return the original delta:
        snap = self.snap_info.distance
        if (snap == 0) or (not self._drag_snapping):
            return dy
            
        # Compute the adjusted x-coordinate:
        yt = y + dy
        
        # Check to see if grid snapping is allowed:
        gi = self.grid_info
        if gi.snapping:
            
            # Compute the nearest grid point above the point:
            n  = (yt - gi.offset) / gi.size
            y0 = (n * gi.size) + gi.offset
            
            # If it is within snapping distance, return the snapped delta:
            if abs( yt - y0 ) <= snap:
                return (y0 - y)
                
            # Compute the nearest grid point below the point:
            y0 += gi.size
            
            # If it is within snapping distance, return the snapped delta:
            if abs( yt - y0 ) <= snap:
                return (y0 - y)
                
        # Check to see if guide line snapping is allowed:
        if self.guide_info.snapping:
            xs, ys = self._drag_guides
            
            # Check to see if the point is within snapping distance of any of
            # the guide lines:
            for y0 in ys.keys():
                delta = abs( yt - y0 )
                if delta <= snap:
                    snap = delta
                    dy   = y0 - y
                
        # Return the delta:
        return dy        

    def update ( self ):
        """ Updates the contents of the canvas and its bounds.
        """
        # Refresh all canvas items:
        self._refresh_items()
        
        # Update the canvas size:
        self._adjust_size()

    def dropped_on ( self, item, drop, x, y ):
        """ Handles a single item dropped on a list item or canvas.
        """
        objects = self.adapter.get_dropped( item, drop )
        if objects is not None:
            if isinstance( objects, SequenceTypes ):
                for object in objects:
                    self.preferred_position = ( x, y )
                    self.add_object( object )
            else:
                self.preferred_position = ( x, y )
                self.add_object( objects )
        
    #-- Property Implementations -----------------------------------------------
    
    def _get_position ( self ):
        return self.canvas.GetPositionTuple()
        
    def _get_size ( self ):
        return self.canvas.GetSizeTuple()
        
    @cached_property
    def _get_add_menu ( self ):
        self.add_classes = classes = []
        
        def menu_items ( items ):
            result = []
            name   = menu_name = ''
            for item in items:
                if isinstance( item, SequenceTypes ):
                    value = menu_items( item )
                    if value is not None:
                        result.append( value )
                elif isinstance( item, basestring ):
                    name = item
                    if menu_name == '':
                        menu_name = item
                else:
                    if name == '': 
                        name = user_name_for( item.__name__ )
                    result.append( Action( 
                            name   = name,
                            action = "self._add_object(%d)" % len( classes ) ) )
                    name = ''
                    classes.append( item )
                 
            if len( result ) == 1:
                return result[0]
            
            return Menu( name = menu_name, *result )
            
        result = menu_items( self.add )
        if isinstance( result, Menu ):
            return result
            
        return Menu( result, name = 'popup' )
            
        
    #-- Trait Event Handlers ---------------------------------------------------
    
    @on_trait_change( 'snap_info.+, grid_info.+, guide_info.+' )
    def _on_canvas_changed ( self ):
        """ Handles any trait change that affects the appearance of the
            canvas.
        """
        self._refresh_canvas()
            
    @on_trait_change( 'status' )
    def _on_update ( self ):
        """ Handles a trait changing that requires the list canvas to be 
            refreshed on the display.
        """
        do_later( self.refresh, 'status' )
        
    def _fast_layout_changed ( self ):
        """ Handles the 'fast_layout' mode being turned on or off.
        """
        self._last_layout = ( 9999999, 0, 0 )
        
    #-- Mouse Event Handlers ---------------------------------------------------
    
    def dragging_motion ( self, x, y, event ):
        """ Handles one of the list items being moved or resized.
        """
        x, y = self._event_xy( x, y )
        mode, x0, y0, dx, dy, xo, yo = self._drag_info
        drag_item = self._drag_item
        xi,  yi   = drag_item.position 
        dxi, dyi  = drag_item.size 
        rx, ry, rdx, rdy = drag_item.resize( mode, x0, y0, dx, dy,
                                                   x - xo, y - yo )
        if ((rx != 0) or (ry != 0)) or (rdx != 0) or (rdy != 0):
            drag_moved = self._drag_moved
            drag_moved.add( drag_item )
            for item in self._drag_set:
                if item is not drag_item:
                    x, y, dx, dy = bounds = item.bounds
                    if (mode & 0x03) != 0:
                        if (mode & 0x01) != 0:
                            if (mode & 0x04) != 0:
                                if x == xi:
                                    x  += rx
                                    dx += rdx
                                elif (x + dx) <= xi:
                                    x += rx
                            elif (x + dx) == (xi + dxi):
                                dx += rdx
                            elif x >= (xi + dxi):
                                x += rdx
                        if (mode & 0x02) != 0:
                            if (mode & 0x08) != 0:
                                if y == yi:
                                    y  += ry
                                    dy += rdy
                                elif (y + dy) <= yi:
                                    y += ry
                            elif (y + dy) == (yi + dyi):
                                dy += rdy
                            elif y >= (yi + dyi):
                                y += rdy
                    else:
                        x += rx
                        y += ry
                        
                    if bounds != ( x, y, dx, dy ):
                        item.bounds = x, y, dx, dy
                        drag_moved.add( item )
        
    def dragging_left_up ( self, x, y, event ):
        """ Handles the left mouse button being released while moving or
            resizing a list item.
        """
        for item in self._drag_moved:
            item.moved = True
        self._drag_item   = self._drag_set = self._drag_moved = \
        self._drag_guides = None 
        self.state        = 'normal'
        self._refresh_canvas_drag( False )
        
        # Update the canvas:
        self.update()
        
    #-- Toolbar Button Event Handlers ------------------------------------------
    
    def add_left_up ( self, x, y, event ):
        """ Handles the user clicking the 'add' button.
        """
        control = self.control
        control.PopupMenuXY( self.add_menu.create_menu( control, self ), 
                             x - 10, y - 10 )
    
    def clear_left_up ( self, x, y, event ):
        """ Handles the user clicking the 'clear' button.
        """
        if confirm( self.control, 'Are you sure you want delete all items?',
                    'Confirm delete' ) == YES:
            del self.editor.value[:]
    
    def load_left_up ( self, x, y, event ):
        """ Handles the user clicking the 'load' button.
        """
        pass # fixme: NOT IMPLEMENTED YET
    
    def save_left_up ( self, x, y, event ):
        """ Handles the user clicking the 'save' button.
        """
        pass # fixme: NOT IMPLEMENTED YET
        
    #-- Drag and Drop Event Handlers -------------------------------------------

    def wx_dropped_on ( self, x, y, data, drag_result ):
        """ Handles an object being dropped on a list canvas.
        """
        if not isinstance( data, SequenceTypes ):
            # Handle the case of just a single item being dropped:
            self.dropped_on( self, data, x, y )
        else:
            # Handles the case of a list of items being dropped:
            for item in data:
                self.dropped_on( self, item, x, y )
            
        # Return a successful drop result:
        return drag_result
        
    def wx_drag_any ( self, x, y, data, drag_result ):
        """ Handles a Python object being dragged over the tree.
        """
        if isinstance( data, SequenceTypes ):
            rc = wx.DragNone
            for item in data:
                rc = self.wx_drag_any( x, y, item, drag_result )
                if rc == wx.DragNone:
                    break
                    
            return rc
           
        # If the adapter says it is OK to drop the data here, then indicate the
        # data can be dropped:
        if self.adapter.get_can_drop( self, data ):
            return drag_result
            
        # Else indicate that we will not accept the data:
        return wx.DragNone
        
    #-- Other wx Event Handlers ------------------------------------------------
    
    def canvas_erase_background ( self, event ):
        """ Do not erase the background here (do it in the 'on_paint' handler).
        """
        pass
   
    def canvas_paint ( self, event ):
        """ Handles repainting the canvas.
        """
        # Set up to do the drawing:
        canvas   = self.canvas
        dc       = wx.PaintDC( canvas )
        wdx, wdy = canvas.GetClientSizeTuple()
        if self.scrollable:
            canvas.DoPrepareDC( dc )
            vdx, vdy = canvas.GetVirtualSize()
            wdx, wdy = max( wdx, vdx ), max( wdy, vdy )
        
        # Draw the canvas background:
        dc.SetBrush( wx.Brush( canvas.GetBackgroundColour() ) )
        dc.SetPen( wx.TRANSPARENT_PEN )
        dc.DrawRectangle( 0, 0, wdx, wdy )
        
        # Draw the grid (if necessary):
        gi = self.grid_info
        if ((gi.visible == 'always') or
            ((gi.visible == 'drag') and (self.state == 'dragging'))):
            dc.SetPen( wx.Pen( gi.color_, 1, pen_styles[ gi.style ] ) )
            
            size   = gi.size
            offset = gi.offset % size
            for x in range( offset, wdx, size ):
                dc.DrawLine( x, 0, x, wdy )
                
            for y in range( offset, wdy, size ):
                dc.DrawLine( 0, y, wdx, y )
        
        # Draw the guide lines (if necessary):
        gi = self.guide_info
        if ((gi.visible == 'always') or
            ((gi.visible == 'drag') and (self.state == 'dragging')) and
            (len( self.items ) > 0)):
                
            # Determine the set of guide lines to draw:
            xs, ys = self._guide_lines( self_drag_set )
            
            # Set up the pen for drawing guide lines:
            dc.SetPen( wx.Pen( gi.color_, 1, pen_styles[ gi.style ] ) )
            
            # Draw the x guide lines:
            for x in xs.keys():
                dc.DrawLine( x, 0, x, wdy )
                
            # Draw the y guide lines:
            for y in ys.keys():
                dc.DrawLine( 0, y, wdx, y )
    
    #-- ListCanvasPanel Method Overrides ---------------------------------------
    
    def _layout_items ( self, xl, xr, yc, yt, dyt ):
        """ Lays out the contents of the item's title bar.
        """
        operations = self.operations
        
        if 'save' in operations:
            xr = self._layout_button( 'save', xr, yc )
        
        if 'load' in operations:
            xr = self._layout_button( 'load', xr, yc )
        
        if 'clear' in operations:
            xr = self._layout_button( 'clear', xr, yc )
        
        if ('add' in operations) and (len( self.add ) > 0):
            xr = self._layout_button( 'add', xr, yc )
        
        if 'status' in operations:
            # Add the layout information for the title:
            self.layout[ 'status' ] = ( xl, yt, xr - xl, dyt )

    #-- Pyface Menu Interface Implementation -----------------------------------
            
    def add_to_menu ( self, menu_item ):
        """ Adds a menu item to the menu bar being constructed.
        """
        pass
                
    def add_to_toolbar ( self, toolbar_item ):
        """ Adds a tool bar item to the tool bar being constructed.
        """
        pass
        
    def can_add_to_menu ( self, action ):
        """ Returns whether the action should be defined in the user interface.
        """
        return True
        
    def can_add_to_toolbar ( self, action ):
        """ Returns whether the toolbar action should be defined in the user 
            interface.
        """
        return True
                
    def perform ( self, action ):
        """ Performs the action described by a specified Action object.
        """
        action = action.action
        if action[ : 5 ] == 'self.':
            eval( action, globals(), { 'self': self } )
        else:
            getattr( self, action )()
                
    #-- Private Methods --------------------------------------------------------
    
    def _add_object ( self, index ):
        """ Adds the object class with the specified 'add_classes' index to
            the list canvas.
        """
        self.editor.value.append( self.add_classes[ index ]() )
        
    def _refresh_canvas ( self ):
        """ Refresh the contents of the canvas.
        """
        if self.canvas is not None:
            self.canvas.Refresh()
            
    def _refresh_canvas_drag ( self, start = True ):
        """ Refreshes the canvas at the beginning or end of a drag operation if
            necessary.
        """
        visible = self.guide_info.visible
        if ((self.grid_info.visible == 'drag') or
            (visible == 'drag') or ((not start) and (visible == 'always'))):
            self._refresh_canvas()
            
    def _refresh_items ( self ):
        """ Refresh all list items on the canvas.
        """
        for item in self.items:
            item.refresh()
        
    def _guide_lines ( self, ignore ):
        """ Returns the x and y coordinates for all guide lines.
        """
        if ignore is None:
            ignore = set()
            
        dx, dy    = self.size
        xs        = { 0: None, dx - 1: None }
        ys        = { 0: None, dy - 1: None }
        for item in self.items:
            if item not in ignore:
                x,  y  = item.position
                dx, dy = item.size
                xs[ x ]      = None
                ys[ y ]      = None
                xs[ x + dx ] = None
                ys[ y + dy ] = None
                    
        # Return the x and y coordinate dictionaries:
        return ( xs, ys )

    def _adjust_size ( self ):
        """ Adjusts the size of the canvas (if necessary).
        """
        if self.scrollable:
            xvs, yvs   = self.canvas.GetViewStart()
            xppu, yppu = self.canvas.GetScrollPixelsPerUnit()
            xvs       *= xppu
            yvs       *= yppu
            cdx = cdy  = 0
            for item in self.items:
                x,  y  = item.position
                dx, dy = item.size
                cdx    = max( cdx, x + dx + xvs )
                cdy    = max( cdy, y + dy + yvs )
                
            self.canvas.SetVirtualSize( ( cdx, cdy ) )

    def _event_xy ( self, x, y ):
        """ Returns the translated (x,y) coordinates for an event.
        """
        if not self.scrollable:
            return ( x, y )
            
        xvs, yvs = self.canvas.GetViewStart()
        dx, dy   = self.canvas.GetScrollPixelsPerUnit()
        return ( x + (xvs * dx), y + (yvs * dy) )

#-------------------------------------------------------------------------------
#  'ListCanvasItemMonitor' class:
#-------------------------------------------------------------------------------

class ListCanvasItemMonitor ( HasPrivateTraits ):
    
    #-- Interface Traits -------------------------------------------------------
    
    # The list canvas item this is a monitor for:
    item = Instance( ListCanvasItem )
    
    # The list canvas adapter that created this monitor:
    adapter = Instance( ListCanvasAdapter )
            
#-------------------------------------------------------------------------------
#  '_ListCanvasEditor' class:
#-------------------------------------------------------------------------------
                               
class _ListCanvasEditor ( Editor ):
    """ An editor for displaying list items as themed Traits UI Views on a 
        themed free-form canvas.
    """
    
    #-- Private Traits ---------------------------------------------------------
    
    # The list canvas used by the editor:
    canvas = Instance( ListCanvas, () )
    
    #---------------------------------------------------------------------------
    #  Trait definitions:  
    #---------------------------------------------------------------------------
        
    # Is the shell editor is scrollable? This value overrides the default.
    scrollable = True
    
    #-- Editor Method Overrides ------------------------------------------------
        
    def init ( self, parent ):
        """ Finishes initializing the editor by creating the underlying toolkit
            widget.
        """
        factory = self.factory
        
        # Add all specified features to DockWindows:
        for feature in factory.features:
            add_feature( feature )
        
        # Create the underlying wx control:
        lc        = self.canvas
        lc.editor = self                               
        lc.set( **factory.get( 'theme', 'adapter', 'snap_info', 'guide_info',
                               'grid_info', 'operations', 'add' ) )
        self.control = lc.create_control( parent, factory.scrollable )
                     
        # Set up the additional 'list items changed' event handler needed for
        # a list based trait:
        self.context_object.on_trait_change( self.update_editor_item, 
                               self.extended_name + '_items?', dispatch = 'ui' )
                                                        
        # Add the developer specified tooltip information:
        self.set_tooltip()

    def update_editor ( self ):
        """ Updates the editor when the object trait changes externally to the
            editor.
        """
        if self._inited is None:
            self._inited = True
            do_later( self.update_editor )
            return
            
        self.control.Freeze()
        canvas = self.canvas
        canvas.fast_layout = True
        canvas.replace_items( [ canvas.create_object( object ) 
                                for object in self.value ] )
        canvas.fast_layout = False
        self.control.Thaw()                                
                
    def dispose ( self ):
        """ Disposes of the contents of an editor.
        """
        self.canvas.replace_items()
        
        super( _ListCanvasEditor, self ).dispose()
     
    #-- Private Methods --------------------------------------------------------
    
    def update_editor_item ( self, event ):
        """ Updates the editor when an item in the object trait changes 
            externally to the editor.
        """
        canvas = self.canvas
        canvas.replace_items(
            [ canvas.create_object( object ) for object in event.added ],
            event.index, event.index + len( event.removed )
        )

#-------------------------------------------------------------------------------
#  Create the editor factory object:
#-------------------------------------------------------------------------------

# wxPython editor factory for list canvas editors.
class ListCanvasEditor ( BasicEditorFactory ):
    
    # The class used to construct editor objects:
    klass = _ListCanvasEditor
    
    # The adapter used to control operations on the list canvas:
    adapter = Instance( ListCanvasAdapter, () )
    
    # The list of feature classes that items on the list canvas can support:
    features = List
    
    # The theme to use for the list canvas:
    theme = ATheme( Theme( 'default_canvas', label = ( 0, 2 ) ) )
    
    # The snapping information to use for the list canvas:
    snap_info = Instance( SnapInfo, () )
    
    # The guide line information to use for the list canvas:
    guide_info = Instance( GuideInfo, () )
    
    # The grid information to use for the list canvas:
    grid_info = Instance( GridInfo, () )

    # What operations are allowed on the list canvas:
    operations = CanvasOperations
    
    # The list of classes that can be added to the canvas using the canvas
    # toolbar and/or context menu:
    add = List
    
    # Is the list canvas scrollable?
    scrollable = Bool( False )

