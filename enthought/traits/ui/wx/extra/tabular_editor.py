#-------------------------------------------------------------------------------
#
#  A traits UI editor for editing tabular data (arrays, list of tuples, lists of 
#  objects, etc).
#
#  Written by: David C. Morrill
#
#  Date: 05/20/2007
#
#  (c) Copyright 2007 by Enthought, Inc.
#
#-------------------------------------------------------------------------------

""" A traits UI editor for editing tabular data (arrays, list of tuples, lists 
   of objects, etc).
"""

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

import wx

from enthought.traits.api \
    import HasPrivateTraits, Color, Str, Int, Enum, List, Bool, Instance, Any, \
           Dict, Event, Property, TraitListEvent, Interface, on_trait_change, \
           cached_property, implements
    
from enthought.traits.ui.wx.editor \
    import Editor
    
from enthought.traits.ui.wx.basic_editor_factory \
    import BasicEditorFactory

from enthought.pyface.image_resource \
    import ImageResource

try:
    from enthought.util.wx.drag_and_drop \
        import PythonDropSource, PythonDropTarget
except:
    PythonDropSource = PythonDropTarget = None

#-------------------------------------------------------------------------------
#  'ITabularAdapter' interface:
#-------------------------------------------------------------------------------

class ITabularAdapter ( Interface ):
    
    # The row index of the current item being adapted:
    row = Int
    
    # The current column id being adapted (if any):
    column = Any
    
    # Current item being adapted:
    item = Any
    
    # The current value (if any):
    value = Any
    
    # The list of columns the adapter supports. The items in the list have the
    # same format as the *columns* trait in the *TabularAdapter* class, with the
    # additional requirement that the *string* values must correspond to a
    # *string* value in the associated *TabularAdapter* class.
    columns = List( Str )
    
    # Does the adapter know how to handler the current *item* or not:
    accepts = Bool
    
    # Does the value of *accepts* depend only upon the type of *item*?
    is_cacheable = Bool
    
#-------------------------------------------------------------------------------
#  'AnITabularAdapter' class:
#-------------------------------------------------------------------------------

class AnITabularAdapter ( HasPrivateTraits ):
    
    implements( ITabularAdapter )
    
    #-- Implementation of the IListStrAdapter Interface ------------------------
    
    # The row index of the current item being adapted:
    row = Int
    
    # The current column id being adapted (if any):
    column = Any
    
    # Current item being adapted:
    item = Any
    
    # The current value (if any):
    value = Any
    
    # The list of columns the adapter supports. The items in the list have the
    # same format as the *columns* trait in the *TabularAdapter* class, with the
    # additional requirement that the *string* values must correspond to a
    # *string* value in the associated *TabularAdapter* class.
    columns = List( Str )
    
    # Does the adapter know how to handler the current *item* or not:
    accepts = Bool( True )
    
    # Does the value of *accepts* depend only upon the type of *item*?
    is_cacheable = Bool( True )
 
#-------------------------------------------------------------------------------
#  'TabularAdapter' class:
#-------------------------------------------------------------------------------

class TabularAdapter ( HasPrivateTraits ):
    """ The base class for adapting list items to values that can be edited 
        by a ListStrEditor.
    """
    
    #-- Trait Definitions ------------------------------------------------------
    
    # A list of columns that should appear in the table. Each entry can have one
    # of two forms: string or ( string, any ), where *string* is the UI name of
    # the column, and *any* is a value that identifies that column to the 
    # adapter. Normally this value is either a trait name or an index, but it 
    # can be any value that the adapter wants. If only *string* is specified,
    # then *any* is the index of the *string* within *columns*.
    columns = List( update = True )
    
    # Specifies the default value for a new row:
    default_value = Any( '' )
    
    # The default text color for table rows (even, odd, any rows):
    even_text_color = Color( None, update = True )
    odd_text_color  = Color( None, update = True )
    text_color      = Color( None, update = True )
    
    # The default background color for table rows (even, odd, any rows):
    even_bg_color = Color( None, update = True )
    odd_bg_color  = Color( None, update = True )
    bg_color      = Color( None, update = True )
    
    # The name of the default image to use for column items:
    image = Str( None, update = True )
    
    # Can the text value of each item be edited:
    can_edit = Bool( True )
    
    # Can any arbitrary value be dropped onto the tabular view:
    can_drop = Bool( False )
    
    # Specifies where a dropped item should be placed in the table relative to
    # the item it is dropped on:
    dropped = Enum( 'after', 'before' )
    
    # The tooltip information for row items:
    tooltip = Str
    
    # The row index of the current item being adapted:
    row = Int
    
    # The current column id being adapted (if any):
    column = Any
    
    # Current item being adapted:
    item = Any
    
    # The current value (if any):
    value = Any
    
    # List of optional delegated adapters:
    adapters = List( ITabularAdapter, update = True )
    
    #-- Private Trait Definitions ----------------------------------------------
    
    # Cache of attribute handlers:
    cache = Any( {} )
    
    # Event fired when the cache is flushed:
    cache_flushed = Event( update = True )
    
    # The mapping from column indices to column identifiers (defined by the
    # *columns* trait):
    column_map = Property( depends_on = 'columns' )
    
    # The mapping from column indices to column labels (defined by the *columns* 
    # trait):
    label_map = Property( depends_on = 'columns' )
    
    # For each adapter, specifies the column indices the adapter handles:
    adapter_column_indices = Property( depends_on = 'adapters,columns' )
    
    # For each adapter, specifies the mapping from column index to column id:
    adapter_column_map = Property( depends_on = 'adapters,columns' )
    
    #-- Adapter methods that are sensitive to item type ------------------------
    
    def get_can_edit ( self, object, trait, row ):
        """ Returns whether the user can edit a specified 
            *object.trait[row]* item. A True result indicates the value 
            can be edited, while a False result indicates that it cannot be 
            edited.
        """
        return self._result_for( 'get_can_edit', object, trait, row, 0 )
    
    def get_drag ( self, object, trait, row ):
        """ Returns the 'drag' value for a specified 
            *object.trait[row]* item. A result of *None* means that the 
            item cannot be dragged.
        """
        return self._result_for( 'get_drag', object, trait, row, 0 )
        
    def get_can_drop ( self, object, trait, row, value ):
        """ Returns whether the specified *value* can be dropped on the
            specified *object.trait[row]* item. A value of **True** means the
            *value* can be dropped; and a value of **False** indicates that it
            cannot be dropped.
        """
        return self._result_for( 'get_can_drop', object, trait, row, 0, value )
        
    def get_dropped ( self, object, trait, row, value ):
        """ Returns how to handle a specified *value* being dropped on a
            specified *object.trait[row]* item. The possible return values are:
                
            'before'
                Insert the specified *value* before the dropped on item.
            'after'
                Insert the specified *value* after the dropped on item.
        """
        return self._result_for( 'get_dropped', object, trait, row, 0, value )
        
    def get_text_color ( self, object, trait, row ):
        """ Returns the text color for a specified *object.trait[row].column* 
            item. A result of None means use the default text color. 
        """
        return self._result_for( 'get_text_color', object, trait, row, 0 )
     
    def get_bg_color ( self, object, trait, row ):
        """ Returns the background color for a specified 
            *object.trait[row].column* item. A result of None means use the 
            default background color.
        """
        return self._result_for( 'get_bg_color', object, trait, row, 0 )
        
    def get_image ( self, object, trait, row, column ):
        """ Returns the name of the image to use for a specified 
            *object.trait[row].column* item. A result of None means no image
            should be used. Otherwise, the result should either be the name of
            the image, or an ImageResource item specifying the image to use.
        """
        return self._result_for( 'get_image', object, trait, row, column )
        
    def get_item ( self, object, trait, row ):
        """ Returns the value of the *object.trait[row]* item.
        """
        return self._result_for( 'get_item', object, trait, row, 0 )
     
    def get_text ( self, object, trait, row, column ):
        """ Returns the text to display for a specified 
            *object.trait[row].column* item. 
        """
        return self._result_for( 'get_text', object, trait, row, column )
     
    def set_text ( self, object, trait, row, text ):
        """ Sets the text for a specified *object.trait[row].column* item to
            *text*.
        """
        self._result_for( 'set_text', object, trait, row, 0, text )
        
    def get_tooltip ( self, object, trait, row, column ):
        """ Returns the tooltip for a specified row.
        """
        return self._result_for( 'get_tooltip', object, trait, row, column )
 
    #-- Adapter methods that are not sensitive to item type --------------------
    
    def len ( self, object, trait ):
        """ Returns the number of items in the specified *object.trait" list.
        """
        return len( getattr( object, trait ) )
    
    def get_default_value ( self, object, trait ):
        """ Returns a new default value for the specified *object.trait* list.
        """
        return self.default_value
        
    def set_row ( self, object, trait, row, value ):
        """ Sets the value of the *object.trait[row]* item.
        """
        getattr( object, trait )[ row ] = value
        
    def delete ( self, object, trait, row ):
        """ Deletes the specified *object.trait[row]* item.
        """
        del getattr( object, trait )[ row ]
        
    def insert ( self, object, trait, row, value ):
        """ Inserts a new value at the specified *object.trait[row]* index.
        """
        getattr( object, trait ) [ row: row ] = [ value ]
        
    #-- Private Adapter Implementation Methods ---------------------------------
        
    def _get_can_edit ( self ):
        return self.can_edit
        
    def _get_drag ( self ):
        return self.item
        
    def _get_can_drop ( self ):
        return self.can_drop
        
    def _get_dropped ( self ):
        return self.dropped

    def _get_text_color ( self ):
        if (self.row % 2) == 0:
            return self.even_text_color_ or self.text_color_
            
        return self.odd_text_color or self.text_color_
        
    def _get_bg_color ( self ):
        if (self.row % 2) == 0:
            return self.even_bg_color_ or self.bg_color_
            
        return self.odd_bg_color or self.bg_color_
        
    def _get_image ( self ):
        return self.image
        
    def _get_item ( self ):
        return self.item
        
    def _set_item ( self ):
        if isinstance( self.column, int ):
            self.item[ self.column ] = self.value
        else:
            setattr( self.item, self.column, self.value )
        
    def _get_text ( self ):
        if isinstance( self.column, int ):
            return str( self.item[ self.column ] )
            
        return str( getattr( self.item, self.column ) )
     
    def _set_text ( self ):
        if isinstance( self.column, int ):
            self.item[ column ] = self.value
        else:    
            setattr( self.item, self.column, self.value )
        
    def _get_tooltip ( self ):
        return self.tooltip
        
    #-- Property Implementations -----------------------------------------------
    
    @cached_property
    def _get_column_map ( self ):
        map = []
        for i, value in enumerate( self.columns ):
            if isinstance( value, basestring ):
                map.append( i )
            else:
                map.append( value[1] )
                
        return map
    
    @cached_property
    def _get_label_map ( self ):
        map = []
        for i, value in enumerate( self.columns ):
            if isinstance( value, basestring ):
                map.append( value )
            else:
                map.append( value[0] )
                
        return map
        
    @cached_property
    def _get_adapter_column_indices ( self ):
        labels = self.label_map
        map    = []
        for adapter in self.adapters:
            indices = []
            for label in adapter.columns:
                if not isinstance( label, basestring ):
                    label = label[0]
                    
                indices.append( labels.index( label ) )
                
        return map
                
    @cached_property
    def _get_adapter_column_map ( self ):
        labels = self.label_map
        map    = []
        for adapter in self.adapters:
            mapping = {}
            for label in adapter.columns:
                id = None
                if not isinstance( label, basestring ):
                    label, id = label
                    
                key = labels.index( label )
                if id is None:
                    id = key
                    
                mapping[ key ] = id
                
            map.append( mapping )
            
        return map
    
    #-- Private Methods --------------------------------------------------------
    
    def _result_for ( self, name, object, trait, row, column, value = None ):
        """ Returns/Sets the value of the specified *name* attribute for the
            specified *object.trait[row].column* item.
        """
        self.value  = value
        self.row    = row
        self.column = column_id = self.column_map[ column ]
        item        = None
        try:
            items = getattr( object, trait )
            if row < len( items ):
                item = items[ row ]
        except:
            pass
            
        self.item  = item
        item_class = item.__class__
        key        = '%s:%s:%d' % ( item_class.__name__, name, column )
        handler    = self.cache.get( key )
        if handler is not None:
            return handler()
            
        prefix     = name[:4]
        trait_name = name[4:]   
            
        for i, adapter in enumerate( self.adapters ):
            if column in self.adapter_column_indices[i]:
                adapter.row    = row
                adapter.item   = item
                adapter.value  = value
                adapter.column = column_id = self.adapter_column_map[i][column]
                if adapter.accepts:
                    get_name = '%s_%s' % ( column_id, trait_name )
                    if adapter.trait( get_name ) is not None:
                        if prefix == 'get_':
                            handler = lambda: getattr( adapter.set(
                                row  = self.row, column = column_id, 
                                item = self.item ), get_name )
                        else:
                            handler = lambda: setattr( adapter.set(
                                row  = self.row, column = column_id, 
                                item = self.item ), get_name, self.value )
                                
                        if adapter.is_cacheable:
                            break
                            
                        return handler()
        else:
            for klass in item_class.__mro__:
                handler = (self._get_handler_for(
                        '%s_%s_%s' % ( klass.__name__, column_id, trait_name ),
                        prefix ) or 
                    self._get_handler_for(
                        '%s_%s' % ( klass.__name__, trait_name ), prefix ))
                if handler is not None:
                    break
                    
            else:  
                handler = (self._get_handler_for( '%s_%s' % ( column_id, 
                              trait_name ), prefix ) or
                          getattr( self, '_' + name ))
            
        self.cache[ key ] = handler
        return handler()

    def _get_handler_for ( self, name, prefix ):
        """ Returns the handler for a specified trait name (or None if not
            found).
        """
        if self.trait( name ) is not None:
            if prefix == 'get_':
                return lambda: getattr( self, name )
                
            return lambda: setattr( self, name, self.value )
            
        return None
        
    @on_trait_change( 'columns,adapters.+update' )        
    def _flush_cache ( self ):
        """ Flushes the cache when the columns or any trait on any adapter 
            changes.
        """
        self.cache = {}
        self.cache_flushed = True
        
#-------------------------------------------------------------------------------
#  'wxListCtrl' class:  
#-------------------------------------------------------------------------------
    
class wxListCtrl ( wx.ListCtrl ):
    """ Subclass of wx.ListCtrl to provide correct virtual list behavior.
    """
    
    def OnGetItemAttr ( self, row ):
        """ Returns the display attributes to use for the specified list item.
        """
        # fixme: There appears to be a bug in wx in that they do not correctly 
        # manage the reference count for the returned object, and it seems to be
        # gc'ed before they finish using it. So we store an object reference to
        # it to prevent it from going away too soon...
        self._attr = attr = wx.ListItemAttr()
        editor = self._editor
        
        color = editor.adapter.get_bg_color( editor.object, editor.name, row )
        if color is not None:
            attr.SetBackgroundColour( color )
                
        color = editor.adapter.get_text_color( editor.object, editor.name, row )
        if color is not None:
            attr.SetTextColour( color )
            
        return attr
    
    def OnGetItemImage ( self, row ):
        """ Returns the image index to use for the specified list item.
        """
        editor = self._editor
        image  = editor._get_image( editor.adapter.get_image( editor.object, 
                                                         editor.name, row, 0 ) )
        if image is not None:
            return image
            
        return -1
    
    def OnGetItemColumnImage ( self, row, column ):
        """ Returns the image index to use for the specified list item.
        """
        editor = self._editor
        image  = editor._get_image( editor.adapter.get_image( editor.object, 
                                                    editor.name, row, column ) )
        if image is not None:
            return image
            
        return -1
        
    def OnGetItemText ( self, row, column ):
        """ Returns the text to use for the specified list item.
        """
        editor = self._editor
                                    
        return editor.adapter.get_text( editor.object, editor.name, row, 
                                        column )

#-------------------------------------------------------------------------------
#  '_TabularEditor' class:
#-------------------------------------------------------------------------------
                               
class _TabularEditor ( Editor ):
    """ A traits UI editor for editing tabular data (arrays, list of tuples, 
        lists of objects, etc).
    """
    
    #-- Trait Definitions ------------------------------------------------------
    
    # The current set of selected items (which one is used depends upon the 
    # initial state of the editor factory 'multi_select' trait):
    selected       = Any
    multi_selected = List
    
    # The current set of selected item indices (which one is used depends upon 
    # the initial state of the editor factory 'multi_select' trait):
    selected_row        = Int
    multi_selected_rows = List( Int )
    
    # The most recently actived item and its index:
    activated     = Any
    activated_row = Int
    
    # The most recently right_clicked item and its index:
    right_clicked     = Event
    right_clicked_row = Event

    # Is the tabular editor scrollable? This value overrides the default.
    scrollable = True
    
    # Row index of item to select after rebuilding editor list:
    row = Any
    
    # Should the selected item be edited after rebuilding the editor list:
    edit = Bool( False )
           
    # The adapter from trait values to editor values:                       
    adapter = Instance( TabularAdapter )
    
    # Dictionaly mapping image names to wx.ImageList indices:
    images = Any( {} )
    
    # Dictionary mapping ImageResource objects to wx.ImageList indices:
    image_resources = Any( {} )
        
    #---------------------------------------------------------------------------
    #  Finishes initializing the editor by creating the underlying toolkit
    #  widget:
    #---------------------------------------------------------------------------
        
    def init ( self, parent ):
        """ Finishes initializing the editor by creating the underlying toolkit
            widget.
        """
        factory = self.factory
        
        # Set up the adapter to use:
        self.adapter = factory.adapter
        self.sync_value( factory.adapter_name, 'adapter', 'from' )
        
        # Determine the style to use for the list control:
        style = wx.LC_REPORT | wx.LC_VIRTUAL
        
        if factory.editable:
            style |= wx.LC_EDIT_LABELS 
        
        if factory.horizontal_lines:
            style |= wx.LC_HRULES
        
        if factory.vertical_lines:
            style |= wx.LC_VRULES
            
        if not factory.multi_select:
            style |= wx.LC_SINGLE_SEL
            
        # Create the list control and link it back to us:
        self.control = control = wxListCtrl( parent, -1, style = style )
        control._editor = self
        
        # Create the list control column:
        #fixme: what do we do here?
        control.InsertColumn( 0, '' )
        
        # Set up the list control's event handlers:
        id = control.GetId()
        wx.EVT_LIST_BEGIN_DRAG(       parent, id, self._begin_drag )
        wx.EVT_LIST_BEGIN_LABEL_EDIT( parent, id, self._begin_label_edit )
        wx.EVT_LIST_END_LABEL_EDIT(   parent, id, self._end_label_edit )
        wx.EVT_LIST_ITEM_SELECTED(    parent, id, self._item_selected )
        wx.EVT_LIST_ITEM_DESELECTED(  parent, id, self._item_selected )
        wx.EVT_LIST_KEY_DOWN(         parent, id, self._key_down )
        wx.EVT_LIST_ITEM_RIGHT_CLICK( parent, id, self._right_clicked )
        wx.EVT_LIST_ITEM_ACTIVATED(   parent, id, self._item_activated )
        wx.EVT_MOTION(                control, self._mouse_move )

        # Set up the drag and drop target:
        if PythonDropTarget is not None:
            control.SetDropTarget( PythonDropTarget( self ) )
            
        # Set up the selection listener (if necessary):
        if factory.multi_select:
            self.sync_value( factory.selected, 'multi_selected', 'both',
                             is_list = True )
            self.sync_value( factory.selected_row, 'multi_selected_rows', 
                             'both', is_list = True )
        else:
            self.sync_value( factory.selected, 'selected', 'both' )
            self.sync_value( factory.selected_row, 'selected_row', 'both' )
            
        # Synchronize other interesting traits as necessary:
        self.sync_value( factory.activated, 'activated', 'to' )
        self.sync_value( factory.activated_row, 'activated_row', 'to' )
            
        self.sync_value( factory.right_clicked, 'right_clicked', 'to' )
        self.sync_value( factory.right_clicked_row, 'right_clicked_row', 
                         'to' )
            
        # Make sure we listen for 'items' changes as well as complete list
        # replacements:
        self.context_object.on_trait_change( self.update_editor,
                                self.extended_name + '_items', dispatch = 'ui' )
                                
        # Create the mapping from user supplied images to wx.ImageList indices:
        for image_resource in factory.images:
            self._add_image( image_resource )
            
        # Refresh the editor whenever the adapter changes:
        self.on_trait_change( self._refresh, 'adapter.+update', 
                              dispatch = 'ui' )
                              
        # Rebuild the editor columns and headers whenever the adapter's
        # 'columns' changes:
        self.on_trait_change( self._rebuild, 'adapter.columns', 
                              dispatch = 'ui' )
                              
        # Make sure the tabular view gets initialized:
        self._rebuild()
        
        # Set the list control's tooltip:
        self.set_tooltip()

    def dispose ( self ):
        """ Disposes of the contents of an editor.
        """
        super( _TabularEditor, self ).dispose()
        
        self.context_object.on_trait_change( self.update_editor,
                                  self.extended_name + '_items', remove = True )
        self.on_trait_change( self._refresh, 'adapter.+update',  remove = True ) 
        self.on_trait_change( self._rebuild, 'adapter.columns',  remove = True )
                        
    def update_editor ( self ):
        """ Updates the editor when the object trait changes externally to the
            editor.
        """
        control = self.control
        n       = self.adapter.len( self.object, self.name )
        top     = control.GetTopItem()
        pn      = control.GetCountPerPage()
        
        control.DeleteAllItems()
        control.SetItemCount( n )
        control.RefreshItems( 0, n - 1 )
        
        edit, self.edit = self.edit, False
        row,  self.row  = self.row,  None
        
        if row is not None:
            if row >= n:
                row -= 1
                if row < 0:
                    row = None
        
        if row is None:
            control.EnsureVisible( top + pn - 2 )
            return
         
        if 0 <= (row - top) < pn:
            control.EnsureVisible( top + pn - 2 )
        elif row < top:
            control.EnsureVisible( row + pn - 1 )
        else:
            control.EnsureVisible( row )

        control.SetItemState( row, 
            wx.LIST_STATE_SELECTED | wx.LIST_STATE_FOCUSED,
            wx.LIST_STATE_SELECTED | wx.LIST_STATE_FOCUSED  )
                                         
        if edit:
            control.EditLabel( row )
        
    #-- Trait Event Handlers ---------------------------------------------------
    
    def _selected_changed ( self, selected ):
        """ Handles the editor's 'selected' trait being changed.
        """
        if not self._no_update:
            try:
                self.control.SetItemState( self.value.index( selected ), 
                                wx.LIST_STATE_SELECTED, wx.LIST_STATE_SELECTED )
            except:
                pass
        
    def _selected_row_changed ( self, selected_row ):
        """ Handles the editor's 'selected_index' trait being changed.
        """
        if not self._no_update:
            self.control.SetItemState( selected_row, wx.LIST_STATE_SELECTED, 
                                                     wx.LIST_STATE_SELECTED ) 
        
    def _multi_selected_changed ( self, selected ):
        """ Handles the editor's 'multi_selected' trait being changed.
        """
        if not self._no_update:
            values = self.value
            try:
                self._multi_selected_rows_changed( [ values.index( item )
                                                     for item in selected ] )
            except:
                pass
        
    def _multi_selected_items_changed ( self, event ):
        """ Handles the editor's 'multi_selected' trait being modified.
        """
        values = self.values
        try:
            self._multi_selected_rows_items_changed( TraitListEvent( 0,
                [ values.index( item ) for item in event.removed ],
                [ values.index( item ) for item in event.added   ] ) )
        except:
            pass
        
    def _multi_selected_rows_changed ( self, selected_rows ):
        """ Handles the editor's 'multi_selected_rows' trait being changed.
        """
        if not self._no_update:
            control  = self.control
            selected = self._get_selected()
            
            # Select any new items that aren't already selected:
            for row in selected_rows:
                if row in selected:
                    selected.remove( row )
                else:
                    control.SetItemState( row, wx.LIST_STATE_SELECTED, 
                                               wx.LIST_STATE_SELECTED )
                              
            # Unselect all remaining selected items that aren't selected now:
            for row in selected:
                control.SetItemState( row, 0, wx.LIST_STATE_SELECTED ) 
        
    def _multi_selected_rows_items_changed ( self, event ):
        """ Handles the editor's 'multi_selected_rows' trait being modified.
        """
        control = self.control
        
        # Remove all items that are no longer selected:
        for row in event.removed:
            control.SetItemState( row, 0, wx.LIST_STATE_SELECTED ) 
            
        # Select all newly added items:
        for row in event.added:
            control.SetItemState( row, wx.LIST_STATE_SELECTED, 
                                       wx.LIST_STATE_SELECTED ) 
        
    #-- List Control Event Handlers --------------------------------------------
    
    def _begin_drag ( self, event ):
        """ Handles the user beginning a drag operation with the left mouse
            button.
        """
        if PythonDropSource is not None:
            adapter      = self.adapter
            object, name = self.object, self.name
            selected     = self._get_selected()
            drag_items   = []
            
            # Collect all of the selected items to drag:
            for row in selected:
                drag = adapter.get_drag( object, name, row )
                if drag is None:
                    return
                    
                drag_items.append( drag )
                
            # Save the drag item indices, so that we can later handle a 
            # completed 'move' operation:
            self._drag_rows = selected
            
            try:
                # If only one item is being dragged, drag it as an item, not a
                # list:
                if len( drag_items ) == 1:
                    drag_items = drag_items[0]
                
                # Perform the drag and drop operation:
                ds = PythonDropSource( self.control, drag_items )
                
                # If moves are allowed and the result was a drag move:
                if ((ds.result == wx.DragMove) and 
                    (self._drag_local or self.factory.drag_move)):
                    # Then delete all of the original items (in reverse order
                    # from highest to lowest, so the indices don't need to be
                    # adjusted):
                    rows = self._drag_rows
                    rows.reverse()
                    for row in rows:
                        adapter.delete( object, name, row )
            finally:
                self._drag_rows  = None
                self._drag_local = False
        
    def _begin_label_edit ( self, event ):
        """ Handles the user starting to edit an item label.
        """
        if not self.adapter.get_can_edit( self.object, self.name, 
                                          event.GetIndex() ):
            event.Veto()
        
    def _end_label_edit ( self, event ):
        """ Handles the user finishing editing an item label.
        """
        self.adapter.set_text( self.object, self.name, event.GetIndex(),
                               event.GetText() )
        self.row = event.GetIndex() + 1
       
    def _item_selected ( self, event ):
        """ Handles an item being selected.
        """
        self._no_update = True
        try:
            get_item      = self.adapter.get_item
            object, name  = self.object, self.name
            selected_rows = self._get_selected()
            if self.factory.multi_select:
                self.multi_selected_rows = selected_rows
                self.multi_selected = [ get_item( object, name, row ) 
                                        for row in selected_rows ]
            elif len( selected_rows ) == 0:
                self.selected_row = -1
                self.selected     = None
            else:
                self.selected_row = selected_rows[0]
                self.selected     = get_item( object, name, selected_rows[0] )
        finally:
            self._no_update = False
            
    def _item_activated ( self, event ):
        """ Handles an item being activated (double-clicked or enter pressed).
        """
        self.activated_row = event.GetIndex()
        self.activated     = self.adapter.get_item( self.object, self.name,
                                                    self.activated_row )
            
    def _right_clicked ( self, event ):
        """ Handles an item being right clicked.
        """
        self.right_clicked_row = row = event.GetIndex()
        self.right_clicked     = self.adapter.get_item( self.object, self.name,
                                                        row )
            
    def _key_down ( self, event ):
        """ Handles the user pressing a key in the list control.
        """
        key = event.GetKeyCode()
        if key == wx.WXK_PAGEDOWN:
            self._append_new()
        elif key in ( wx.WXK_BACK, wx.WXK_DELETE ):
            self._delete_current()
        elif key == wx.WXK_INSERT:
            self._insert_current()
        elif key == wx.WXK_LEFT:
            self._move_up_current()
        elif key == wx.WXK_RIGHT:
            self._move_down_current()
        elif key in ( wx.WXK_RETURN, wx.WXK_ESCAPE ):
            self._edit_current()
        else:
            event.Skip()
            
    def _mouse_move ( self, event ):
        """ Handles the user moving the mouse.
        """
        x          = event.GetX()
        column     = self._get_column( x )
        row, flags = self.control.HitTest( wx.Point( x, event.GetY() ) )
        if (row != self._last_row) or (column != self._last_column):
            self._last_row, self._last_column = row, column
            if (row == -1) or (column is None):
                tooltip = ''
            else:
                tooltip = self.adapter.get_tooltip( self.object, self.name,
                                                    row, column )
            if tooltip != self._last_tooltip:
                self._last_tooltip = tooltip
                wx.ToolTip.Enable( False )
                wx.ToolTip.Enable( True )
                self.control.SetToolTip( wx.ToolTip( tooltip ) )

    #-- Drag and Drop Event Handlers -------------------------------------------

    def wx_dropped_on ( self, x, y, data, drag_result ):
        """ Handles a Python object being dropped on the list control.
        """
        row, flags = self.control.HitTest( wx.Point( x, y ) )
        
        # If the user dropped it on an empty list, set the target as past the 
        # end of the list:
        if ((row == -1) and 
            ((flags & wx.LIST_HITTEST_NOWHERE) != 0) and
            (self.control.GetItemCount() == 0)):
            row = 0
            
        # If we have a valid drop target row, proceed:
        if row != -1:
            if not isinstance( data, list ):
                # Handle the case of just a single item being dropped:
                self._wx_dropped_on( row, data )
            else:
                # Handles the case of a list of items being dropped, being 
                # careful to preserve the original order of the source items if
                # possible:
                data.reverse()
                for item in data:
                    self._wx_dropped_on( row, item )
            
            # If this was an inter-list drag, mark it as 'local':
            if self._drag_indices is not None:
                self._drag_local = True
                
            # Return a successful drop result:
            return drag_result
            
        # Indicate we could not process the drop:
        return wx.DragNone

    def _wx_dropped_on ( self, row, item ):
        """ Helper method for handling a single item dropped on the list 
            control.
        """
        adapter      = self.adapter
        object, name = self.object, self.name
        
        # Obtain the destination of the dropped item relative to the target: 
        destination = adapter.get_dropped( object, name, row, item )
        
        # Adjust the target index accordingly:
        if destination == 'after':
            row += 1
            
        # Insert the dropped item at the requested position:
        adapter.insert( object, name, row, item )
        
        # If the source for the drag was also this list control, we need to
        # adjust the original source indices to account for their new position
        # after the drag operation:
        rows = self._drag_rows
        if rows is not None:
            for i in range( len( rows ) - 1, -1, -1 ):
                if rows[i] < row:
                    break
                    
                rows[i] += 1
        
    def wx_drag_over ( self, x, y, data, drag_result ):
        """ Handles a Python object being dragged over the tree.
        """
        if isinstance( data, list ):
            rc = wx.DragNone
            for item in data:
                rc = self.wx_drag_over( x, y, item, drag_result )
                if rc == wx.DragNone:
                    break
                    
            return rc
            
        row, flags = self.control.HitTest( wx.Point( x, y ) )
        
        # If the user is dragging over an empty list, set the target to the end
        # of the list:
        if ((row == -1) and 
            ((flags & wx.LIST_HITTEST_NOWHERE) != 0) and
            (self.control.GetItemCount() == 0)):
            row = 0
           
        # If the drag target index is valid and the adapter says it is OK to
        # drop the data here, then indicate the data can be dropped:
        if ((row != -1) and 
            self.adapter.get_can_drop( self.object, self.name, row, data )):
            return drag_result
            
        # Else indicate that we will not accept the data:
        return wx.DragNone
        
    #-- Private Methods --------------------------------------------------------
    
    def _refresh ( self ):
        """ Refreshes the contents of the editor's list control.
        """
        self.control.RefreshItems( 0, len( self.value ) - 1 )
    
    def _rebuild ( self ):
        """ Rebuilds the contents of the editor's list control.
        """
        control = self.control
        control.ClearAll()
        for i, label in enumerate( self.adapter.label_map ):
            control.InsertColumn( i, label )
    
    def _add_image ( self, image_resource ):
        """ Adds a new image to the wx.ImageList and its associated mapping.
        """
        bitmap = image_resource.create_image().ConvertToBitmap()
        
        image_list = self._image_list
        if image_list is None:
            self._image_list = image_list = wx.ImageList( bitmap.GetWidth(), 
                                                          bitmap.GetHeight() )
            self.control.AssignImageList( image_list, wx.IMAGE_LIST_SMALL )
           
        self.image_resources[image_resource] = \
        self.images[ image_resource.name ]   = row = image_list.Add( bitmap )
        
        return row
        
    def _get_image ( self, image ):
        """ Converts a user specified image to a wx.ListCtrl image index.
        """
        if isinstance( image, ImageResource ):
            result = self.image_resources.get( image )
            if result is not None:
                return result
                
            return self._add_image( image )
            
        return self.images.get( image )
        
    def _get_selected ( self ):
        """ Returns a list of the rows of all currently selected list items.
        """
        selected = []
        item     = -1
        control  = self.control
        while True:
            item = control.GetNextItem( item, wx.LIST_NEXT_ALL, 
                                              wx.LIST_STATE_SELECTED )
            if item == -1:
                break;
                
            selected.append( item )
            
        return selected
        
    def _append_new ( self ):
        """ Append a new item to the end of the list control.
        """
        if 'append' in self.factory.operations:
            adapter   = self.adapter
            self.row  = self.control.GetItemCount()
            self.edit = True
            adapter.insert( self.object, self.name, self.row,
                           adapter.get_default_value( self.object, self.name ) )
        
    def _insert_current ( self ):
        """ Inserts a new item after the currently selected list control item.
        """
        if 'insert' in self.factory.operations:
            selected = self._get_selected()
            if len( selected ) == 1:
                adapter = self.adapter
                adapter.insert( self.object, self.name, selected[0],
                           adapter.get_default_value( self.object, self.name ) )
                self.row  = selected[0]
                self.edit = True
        
    def _delete_current ( self ):
        """ Deletes the currently selected items from the list control.
        """
        if 'delete' in self.factory.operations:
            selected = self._get_selected()
            if len( selected ) == 0:
                return
                
            delete = self.adapter.delete
            selected.reverse()
            for row in selected:
                delete( self.object, self.name, row )
                    
            self.row = row
        
    def _move_up_current ( self ):
        """ Moves the currently selected item up one line in the list control.
        """
        if 'move' in self.factory.operations:
            selected = self._get_selected()
            if len( selected ) == 1:
                row = selected[0]
                if row > 0:
                    adapter      = self.adapter
                    object, name = self.object, self.name
                    item         = adapter.get_item( object, name, row )
                    adapter.delete( object, name, row )
                    adapter.insert( object, name, row - 1, item )
                    self.row = row - 1
        
    def _move_down_current ( self ):
        """ Moves the currently selected item down one line in the list control.
        """
        if 'move' in self.factory.operations:
            selected = self._get_selected()
            if len( selected ) == 1:
                row = selected[0]
                if row < (self.control.GetItemCount() - 1):
                    adapter      = self.adapter
                    object, name = self.object, self.name
                    item         = adapter.get_item( object, name, row )
                    adapter.delete( object, name, row )
                    adapter.insert( object, name, row + 1, item )
                    self.row = row + 1
                    
    def _edit_current ( self ):
        """ Allows the user to edit the current item in the list control.
        """
        if 'edit' in self.factory.operations:
            selected = self._get_selected()
            if len( selected ) == 1:
                self.control.EditLabel( selected[0] )
                
    def _get_column ( self, x ):
        """ Returns the column index corresponding to a specified x position.
        """
        if x >= 0:
            control = self.control
            for i in range( control.GetColumnCount() ):
                x -= control.GetColumnWidth( i )
                if x < 0:
                    return i
                
        return None
                    
#-------------------------------------------------------------------------------
#  'TabularEditor' editor factory class:
#-------------------------------------------------------------------------------

class TabularEditor ( BasicEditorFactory ):
    """ wxPython editor factory for tabular editors.
    """
  
    #-- Trait Definitions ------------------------------------------------------
    
    # The editor class to be created:
    klass = _TabularEditor
    
    # The optional extended name of the trait to synchronize the selection 
    # values with:
    selected = Str
    
    # The optional extended name of the trait to synchronize the selection rows 
    # with:
    selected_row = Str
    
    # The optional extended name of the trait to synchronize the activated value
    # with:
    activated = Str
    
    # The optional extended name of the trait to synchronize the activated 
    # value's row with:
    activated_row = Str
    
    # The optional extended name of the trait to synchronize the right clicked
    # value with:
    right_clicked = Str
    
    # The optional extended name of the trait to synchronize the right clicked
    # value's row with:
    right_clicked_row = Str
    
    # Can the user edit the values?
    editable = Bool( True )
                 
    # Are multiple selected items allowed?
    multi_select = Bool( False )
    
    # Should horizontal lines be drawn between items?
    horizontal_lines = Bool( True )
    
    # Should vertical lines be drawn between items?
    vertical_lines = Bool( True )
           
    # The adapter from trait values to editor values:                       
    adapter = Instance( TabularAdapter, () )
    
    # The optional extended name of the trait containing the adapter:
    adapter_name = Str
    
    # What type of operations are allowed on the list:
    operations = List( Enum( 'delete', 'insert', 'append', 'edit', 'move' ),
                       [ 'delete', 'insert', 'append', 'edit', 'move' ] )
                       
    # Are 'drag_move' operations allowed (i.e. True), or should they always be 
    # treated as 'drag_copy' operations (i.e. False):
    drag_move = Bool( False )
                       
    # The set of images that can be used:                       
    images = List( ImageResource )  
    
