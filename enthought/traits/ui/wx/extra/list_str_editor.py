#-------------------------------------------------------------------------------
#
#  Traits UI editor for editing lists of strings.
#
#  Written by: David C. Morrill
#
#  Date: 05/08/2007
#
#  (c) Copyright 2007 by Enthought, Inc.
#
#-------------------------------------------------------------------------------

""" Traits UI editor for editing lists of strings.
"""

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

import wx

from enthought.traits.api \
    import HasPrivateTraits, Color, Str, Int, Enum, List, Bool, Instance, Any, \
           Dict, Event, TraitListEvent, Interface, on_trait_change
    
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
#  Constants:
#-------------------------------------------------------------------------------

# Result indicating that no handler to produce a result was found:
NoResult = ( False, None )

#-------------------------------------------------------------------------------
#  'IListStrAdapter' interface:
#-------------------------------------------------------------------------------

class IListStrAdapter ( Interface ):
    
    # Current item being adapted:
    item = Any
    
    def accepts ( self, item ):
        """ Returns *True* if the adapter knows how to handle *item*, and 
            *False* otherwise.
        """
        
    def is_cacheable ( self, item ):
        """ Returns *True* if the value of *accepts* only depends only upon the 
            type of *item*, and *False* otherwise.
        """
 
#-------------------------------------------------------------------------------
#  'ListStrAdapter' class:
#-------------------------------------------------------------------------------

class ListStrAdapter ( HasPrivateTraits ):
    """ The base class for adapting list items to values that can be edited 
        by a ListStrEditor.
    """
    
    #-- Trait Definitions ------------------------------------------------------
    
    # Specifies the default value for a new list item:
    default_value = Any( '' )
    
    # The default text color for list items (even, odd, any rows):
    even_text_color = Color( None, update = True )
    odd_text_color  = Color( None, update = True )
    text_color      = Color( None, update = True )
    
    # The default background color for list items (even, odd, any rows):
    even_bg_color = Color( None, update = True )
    odd_bg_color  = Color( None, update = True )
    bg_color      = Color( None, update = True )
    
    # The name of the default image to use for list items:
    image = Str( None, update = True )
    
    # Can the text value of each list item be edited:
    can_edit = Bool( True )
    
    # Specifies where a dropped item should be placed in the list relative to
    # the item it is dropped on:
    dropped = Enum( 'after', 'before' )
    
    # The current item being adapted:
    item = Any
    
    # List of optional delegated adapters:
    adapters = List( IListStrAdapter, update = True )
    
    # Cache of attribute handlers:
    cache = Any( {} )
    
    # Event fired when the cache is flushed:
    cache_flushed = Event( update = True )
    
    #-- Adapter methods that are sensitive to item type ------------------------
    
    def get_can_edit ( self, object, trait, index ):
        """ Returns whether the user can edit a specified *object.trait[index]*
            list item. A True result indicates the value can be edited, while
            a False result indicates that it cannot be edited.
        """
        return self._result_for( 'get_can_edit', object, trait, index )
    
    def get_drag ( self, object, trait, index ):
        """ Returns the 'drag' value for a specified *object.trait[index]*
            list item. A result of *None* means that the item cannot be dragged.
        """
        return self._result_for( 'get_drag', object, trait, index )
        
    def get_can_drop ( self, object, trait, index, value ):
        """ Returns whether the specified *value* can be dropped on the
            specified *object.trait[index]* list item. A value of **True** means
            the *value* can be dropped; and a value of **False** indicates that
            it cannot be dropped.
        """
        return self._result_for( 'get_can_drop', object, trait, index, value )
        
    def get_dropped ( self, object, trait, index, value ):
        """ Returns how to handle a specified *value* being dropped on a
            specified *object.trait[index]* list item. The possible return
            values are:
                
            'before'
                Insert the specified *value* before the dropped on item.
            'after'
                Insert the specified *value* after the dropped on item.
        """
        return self._result_for( 'get_dropped', object, trait, index, value )
        
    def get_text_color ( self, object, trait, index ):
        """ Returns the text color for a specified *object.trait[index]* list
            item. A result of None means use the default list item text color. 
        """
        return self._result_for( 'get_text_color', object, trait, index )
     
    def get_bg_color ( self, object, trait, index ):
        """ Returns the background color for a specified *object.trait[index]*
            list item. A result of None means use the default list item 
            background color.
        """
        return self._result_for( 'get_bg_color', object, trait, index )
        
    def get_image ( self, object, trait, index ):
        """ Returns the name of the image to use for a specified 
            *object.trait[index]* list item. A result of None means no image
            should be used. Otherwise, the result should either be the name of
            the image, or an ImageResource item specifying the image to use.
        """
        return self._result_for( 'get_image', object, trait, index )
        
    def get_item ( self, object, trait, index ):
        """ Returns the value of the *object.trait[index]* list item.
        """
        return self._result_for( 'get_item', object, trait, index )
     
    def get_text ( self, object, trait, index ):
        """ Returns the text to display for a specified *object.trait[index]*
            list item. 
        """
        return self._result_for( 'get_text', object, trait, index )
     
    def set_text ( self, object, trait, index, text ):
        """ Sets the text for a specified *object.trait[index]* list item to
            *text*.
        """
        return self._result_for( 'set_text', object, trait, index )
 
    #-- Adapter methods that are not sensitive to item type --------------------
    
    def get_default_value ( self, object, trait ):
        """ Returns a new default value for the specified *object.trait* list.
        """
        return self.default_value
        
    def set_item ( self, object, trait, index, value ):
        """ Sets the value of the *object.trait[index]* list item.
        """
        getattr( object, trait )[ index ] = value
        
    def delete ( self, object, trait, index ):
        """ Deletes the specified *object.trait[index]* list item.
        """
        del getattr( object, trait )[ index ]
        
    def insert ( self, object, trait, index, value ):
        """ Inserts a new value at the specified *object.trait[index]* list 
            index.
        """
        getattr( object, trait ) [ index: index ] = [ value ]
        
    #-- Private Adapter Implementation Methods ---------------------------------
        
    def _get_can_edit ( self, object, trait, index ):
        return self.can_edit
        
    def _get_drag ( self, object, trait, index ):
        return self.get_text( object, trait, index )
        
    def _get_can_drop ( self, object, trait, index, value ):
        return isinstance( value, basestring )
        
    def _get_dropped ( self, object, trait, index, value ):
        return self.dropped

    def _get_text_color ( self, object, trait, index ):
        if (index % 2) == 0:
            return self.even_text_color_ or self.text_color_
            
        return self.odd_text_color or self.text_color_
        
    def _get_bg_color ( self, object, trait, index ):
        if (index % 2) == 0:
            return self.even_bg_color_ or self.bg_color_
            
        return self.odd_bg_color or self.self.bg_color_
        
    def _get_image ( self, object, trait, index ):
        return self.image
        
    def _get_item ( self, object, trait, index ):
        return getattr( object, trait )[ index ]
        
    def _get_text ( self, object, trait, index ):
        return str( self.get_item( object, trait, index ) )
     
    def _set_text ( self, object, trait, index, text ):
        self.set_item( object, trait, index, text )
    
    #-- Private Methods --------------------------------------------------------
    
    def _result_for ( self, name, object, trait, index, *args ):
        """ Returns the value of the specified *name* attribute for the
            specified *object.trait[index]* list item.
        """
        self.item  = item = getattr( object, trait )[ index ]
        item_class = item.__class__
        key        = '%s:%s' % ( item_class.__name__, name )
        handler    = self.cache.get( key )
        if handler is not None:
            return handler( item, *args )
            
        prefix     = name[:4]
        trait_name = name[4:]   
            
        for adapter in self.adapters:
            if adapter.accepts( item ):
                handler = getattr( adapter, name, None )
                if handler is not None:
                    if adapter.is_cacheable( item ):
                        break
                        
                    return handler( item, *args )
                    
                if ((prefix == 'get_') and 
                    (adapter.trait( trait_name ) is not None)):
                    handler = lambda item: getattr( adapter.set( item = item ),
                                                    trait_name )
                    if adapter.is_cacheable( item ):
                        break
                        
                    return handler( item, *args )
        else:
            for klass in item_class.__mro__:
                cname = '%s_%s' % ( klass.__name__, trait_name )
                
                handler = getattr( self, prefix + cname, None )
                if handler is not None:
                    break
                    
                if (prefix == 'get_') and (self.trait( cname ) is not None):
                    handler = lambda item: getattr( self, cname )
            else:   
                return getattr( self, '_' + name )( object, trait, index, 
                                                    *args )
            
        self.cache[ key ] = handler
        return handler( item, *args )
        
    @on_trait_change( 'adapters.+update' )        
    def _flush_cache ( self ):
        """ Flushes the cache when any trait on any adapter changes.
        """
        self.cache = {}
        self.cache_flushed = True
        
#-------------------------------------------------------------------------------
#  'wxListCtrl' class:  
#-------------------------------------------------------------------------------
    
class wxListCtrl ( wx.ListCtrl ):
    """ Subclass of wx.ListCtrl to provide correct virtual list behavior.
    """
    
    def OnGetItemAttr ( self, index ):
        """ Returns the display attributes to use for the specified list item.
        """
        # fixme: There appears to be a bug in wx in that they do not correctly 
        # manage the reference count for the returned object, and it seems to be
        # gc'ed before they finish using it. So we store an object reference to
        # it to prevent it from going away too soon...
        self._attr = attr = wx.ListItemAttr()
        editor = self._editor
        
        color = editor.adapter.get_bg_color( editor.object, editor.name, index )
        if color is not None:
            attr.SetBackgroundColour( color )
                
        color = editor.adapter.get_text_color( editor.object, editor.name,
                                               index ) 
        if color is not None:
            attr.SetTextColour( color )
            
        return attr
    
    def OnGetItemImage ( self, index ):
        """ Returns the image index to use for the specified list item.
        """
        editor = self._editor
        image  = editor._get_image( editor.adapter.get_image( editor.object, 
                                                          editor.name, index ) )
        if image is not None:
            return image
            
        return -1
        
    def OnGetItemText ( self, index, column ):
        """ Returns the text to use for the specified list item.
        """
        editor = self._editor
                                    
        return editor.adapter.get_text( editor.object, editor.name, index )

#-------------------------------------------------------------------------------
#  '_ListStrEditor' class:
#-------------------------------------------------------------------------------
                               
class _ListStrEditor ( Editor ):
    """ Traits UI editor for editing lists of strings.
    """
    
    #-- Trait Definitions ------------------------------------------------------
    
    # The title of the editor:
    title = Str
    
    # The current set of selected items (which one is used depends upon the 
    # initial state of the editor factory 'multi_select' trait):
    selected       = Any
    multi_selected = List
    
    # The current set of selected item indices (which one is used depends upon 
    # the initial state of the editor factory 'multi_select' trait):
    selected_index         = Int
    multi_selected_indices = List( Int )
    
    # The most recently actived item and its index:
    activated       = Any
    activated_index = Int
    
    # The most recently right_clicked item and its index:
    right_clicked       = Event
    right_clicked_index = Event

    # Is the table editor is scrollable? This value overrides the default.
    scrollable = True
    
    # Index of item to select after rebuilding editor list:
    index = Any
    
    # Should the selected item be edited after rebuilding the editor list:
    edit = Bool( False )
           
    # The adapter from list items to editor values:                       
    adapter = Instance( ListStrAdapter )
    
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
            
        if not factory.multi_select:
            style |= wx.LC_SINGLE_SEL
            
        if (factory.title == '') and (factory.title_name == ''):
            style |= wx.LC_NO_HEADER
            
        # Create the list control and link it back to us:
        self.control = control = wxListCtrl( parent, -1, style = style )
        control._editor = self
        
        # Create the list control column:
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
        wx.EVT_SIZE(                  control, self._size_modified )

        # Set up the drag and drop target:
        if PythonDropTarget is not None:
            control.SetDropTarget( PythonDropTarget( self ) )
        
        # Initialize the editor title:
        self.title = factory.title
        self.sync_value( factory.title_name, 'title', 'from' )
        
        # Set up the selection listener (if necessary):
        if factory.multi_select:
            self.sync_value( factory.selected, 'multi_selected', 'both',
                             is_list = True )
            self.sync_value( factory.selected_index, 'multi_selected_indices', 
                             'both', is_list = True )
        else:
            self.sync_value( factory.selected, 'selected', 'both' )
            self.sync_value( factory.selected_index, 'selected_index', 'both' )
            
        # Synchronize other interesting traits as necessary:
        self.sync_value( factory.activated, 'activated', 'to' )
        self.sync_value( factory.activated_index, 'activated_index', 'to' )
            
        self.sync_value( factory.right_clicked, 'right_clicked', 'to' )
        self.sync_value( factory.right_clicked_index, 'right_clicked_index', 
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
        
        # Set the list control's tooltip:
        self.set_tooltip()

    def dispose ( self ):
        """ Disposes of the contents of an editor.
        """
        super( _ListStrEditor, self ).dispose()
        
        self.context_object.on_trait_change( self.update_editor,
                                  self.extended_name + '_items', remove = True )
        self.on_trait_change( self._refresh, 'adapter.+update', remove = True ) 
                        
    def update_editor ( self ):
        """ Updates the editor when the object trait changes externally to the
            editor.
        """
        control = self.control
        n       = len( self.value )
        top     = control.GetTopItem()
        pn      = control.GetCountPerPage()
        
        control.DeleteAllItems()
        control.SetItemCount( n )
        control.RefreshItems( 0, n - 1 )
        control.SetColumnWidth( 0, control.GetClientSizeTuple()[0]  )
        
        edit,  self.edit  = self.edit,  False
        index, self.index = self.index, None
        
        if index is not None:
            if index >= n:
                index -= 1
                if index < 0:
                    index = None
        
        if index is None:
            control.EnsureVisible( top + pn - 2 )
            return
         
        if 0 <= (index - top) < pn:
            control.EnsureVisible( top + pn - 2 )
        elif index < top:
            control.EnsureVisible( index + pn - 1 )
        else:
            control.EnsureVisible( index )

        control.SetItemState( index, 
            wx.LIST_STATE_SELECTED | wx.LIST_STATE_FOCUSED,
            wx.LIST_STATE_SELECTED | wx.LIST_STATE_FOCUSED  )
                                         
        if edit:
            control.EditLabel( index )
        
    #-- Trait Event Handlers ---------------------------------------------------
    
    def _title_changed ( self, title ):
        """ Handles the editor title being changed.
        """
        list_item = wx.ListItem()
        list_item.SetText( title )
        self.control.SetColumn( 0, list_item ) 
        
    def _selected_changed ( self, selected ):
        """ Handles the editor's 'selected' trait being changed.
        """
        if not self._no_update:
            try:
                self.control.SetItemState( self.value.index( selected ), 
                                wx.LIST_STATE_SELECTED, wx.LIST_STATE_SELECTED )
            except:
                pass
        
    def _selected_index_changed ( self, selected_index ):
        """ Handles the editor's 'selected_index' trait being changed.
        """
        if not self._no_update:
            self.control.SetItemState( selected_index, wx.LIST_STATE_SELECTED, 
                                                       wx.LIST_STATE_SELECTED ) 
        
    def _multi_selected_changed ( self, selected ):
        """ Handles the editor's 'multi_selected' trait being changed.
        """
        if not self._no_update:
            values = self.value
            try:
                self._multi_selected_indices_changed( [ values.index( item )
                                                        for item in selected ] )
            except:
                pass
        
    def _multi_selected_items_changed ( self, event ):
        """ Handles the editor's 'multi_selected' trait being modified.
        """
        values = self.values
        try:
            self._multi_selected_indices_items_changed( TraitListEvent( 0,
                [ values.index( item ) for item in event.removed ],
                [ values.index( item ) for item in event.added   ] ) )
        except:
            pass
        
    def _multi_selected_indices_changed ( self, selected_indices ):
        """ Handles the editor's 'multi_selected_indices' trait being changed.
        """
        if not self._no_update:
            control  = self.control
            selected = self._get_selected()
            
            # Select any new items that aren't already selected:
            for index in selected_indices:
                if index in selected:
                    selected.remove( index )
                else:
                    control.SetItemState( index, wx.LIST_STATE_SELECTED, 
                                                 wx.LIST_STATE_SELECTED )
                              
            # Unselect all remaining selected items that aren't selected now:
            for index in selected:
                control.SetItemState( index, 0, wx.LIST_STATE_SELECTED ) 
        
    def _multi_selected_indices_items_changed ( self, event ):
        """ Handles the editor's 'multi_selected_indices' trait being modified.
        """
        control = self.control
        
        # Remove all items that are no longer selected:
        for index in event.removed:
            control.SetItemState( index, 0, wx.LIST_STATE_SELECTED ) 
            
        # Select all newly added items:
        for index in event.added:
            control.SetItemState( index, wx.LIST_STATE_SELECTED, 
                                         wx.LIST_STATE_SELECTED ) 
        
    #-- List Control Event Handlers --------------------------------------------
    
    def _begin_drag ( self, event ):
        """ Handles the user beginning a drag operation with the left mouse
            button.
        """
        if PythonDropSource is not None:
            adapter      = self.adapter
            object, name = self.object, self.name
            index        = event.GetIndex()
            selected     = self._get_selected()
            drag_items   = []
            
            # Collect all of the selected items to drag:
            for index in selected:
                drag = adapter.get_drag( object, name, index )
                if drag is None:
                    return
                    
                drag_items.append( drag )
                
            # Save the drag item indices, so that we can later handle a 
            # completed 'move' operation:
            self._drag_indices = selected
            
            try:
                # If only one item is being dragged, drag it as an item, not a
                # list:
                if len( drag_items ) == 1:
                    drag_items = drag_items[0]
                
                # Perform the drag and drop operation:
                ds = PythonDropSource( self.control, drag_items )
                
                # If the result was a drag move:
                if ds.result == wx.DragMove:
                    # Then delete all of the original items (in reverse order
                    # from highest to lowest, so the indices don't need to be
                    # adjusted):
                    indices = self._drag_indices
                    indices.reverse()
                    for index in indices:
                        adapter.delete( object, name, index )
            finally:
                self._drag_indices = None
        
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
        self.index = event.GetIndex() + 1
       
    def _item_selected ( self, event ):
        """ Handles an item being selected.
        """
        self._no_update = True
        try:
            get_item         = self.adapter.get_item
            object, name     = self.object, self.name
            selected_indices = self._get_selected()
            if self.factory.multi_select:
                self.multi_selected_indices = selected_indices
                self.multi_selected = [ get_item( object, name, index ) 
                                        for index in selected_indices]
            elif len( selected_indices ) == 0:
                self.selected_index = -1
                self.selected       = None
            else:
                self.selected_index = selected_indices[0]
                self.selected       = get_item( object, name, 
                                                selected_indices[0] )
        finally:
            self._no_update = False
            
    def _item_activated ( self, event ):
        """ Handles an item being activated (double-clicked or enter pressed).
        """
        self.activated_index = event.GetIndex()
        self.activated       = self.adapter.get_item( self.object, self.name,
                                                      self.activated_index )
            
    def _right_clicked ( self, event ):
        """ Handles an item being right clicked.
        """
        self.right_clicked_index = index = event.GetIndex()
        self.right_clicked = self.adapter.get_item( self.object, self.name,
                                                    index )
            
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

    def _size_modified ( self, size ):
        """ Handles the size of the list control being changed.
        """
        dx, dy = self.control.GetClientSizeTuple()
        self.control.SetColumnWidth( 0, dx - 1 )

    #-- Drag and Drop Event Handlers -------------------------------------------

    def wx_dropped_on ( self, x, y, data, drag_result ):
        """ Handles a Python object being dropped on the list control.
        """
        index, flags = self.control.HitTest( wx.Point( x, y ) )
        
        # If the user dropped it below the bottom of the list, set the target
        # as 1 past the end of the list:
        if (index == -1) and ((flags & wx.LIST_HITTEST_NOWHERE) != 0):
            index = len( self.value )
            
        # If we have a valid drop target index, proceed:
        if index != -1:
            if not isinstance( data, list ):
                # Handle the case of just a single item being dropped:
                self._wx_dropped_on( index, data )
            else:
                # Handles the case of a list of items being dropped, being 
                # careful to preserve the original order of the source items if
                # possible:
                data.reverse()
                for item in data:
                    self._wx_dropped_on( index, item )
                    
            # Return a successful drop result:
            return drag_result
            
        # Indicate we could not process the drop:
        return wx.DragNone

    def _wx_dropped_on ( self, index, item ):
        """ Helper method for handling a single item dropped on the list 
            control.
        """
        adapter      = self.adapter
        object, name = self.object, self.name
        
        # Obtain the destination of the dropped item relative to the target: 
        destination = adapter.get_dropped( object, name, index, item )
        
        # Adjust the target index accordingly:
        if destination == 'after':
            index += 1
            
        # Insert the dropped item at the requested position:
        adapter.insert( object, name, index, item )
        
        # If the source for the drag was also this list control, we need to
        # adjust the original source indices to account for their new position
        # after the drag operation:
        indices = self._drag_indices
        if indices is not None:
            for i in range( len( indices ) - 1, -1, -1 ):
                if indices[i] < index:
                    break
                    
                indices[i] += 1
        
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
            
        index, flags = self.control.HitTest( wx.Point( x, y ) )
        
        # If the user dropped it below the bottom of the list, set the target
        # as 1 past the end of the list:
        if (index == -1) and ((flags & wx.LIST_HITTEST_NOWHERE) != 0):
            index = len( self.value )
           
        # If the drag target index is valid and the adapter says it is OK to
        # drop the data here, then indicate the data can be dropped:
        if ((index != -1) and 
            self.adapter.get_can_drop( self.object, self.name, index, data )):
            return drag_result
            
        # Else indicate that we will not accept the data:
        return wx.DragNone
        
    #-- Private Methods --------------------------------------------------------
    
    def _refresh ( self ):
        """ Refreshes the contents of the editor's list control.
        """
        self.control.RefreshItems( 0, len( self.value ) - 1 )
    
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
        self.images[ image_resource.name ]   = index = image_list.Add( bitmap )
        
        return index
        
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
        """ Returns a list of the indices of all currently selected list items.
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
            adapter    = self.adapter
            self.index = self.control.GetItemCount()
            self.edit  = True
            adapter.insert( self.object, self.name, self.index,
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
                self.index = selected[0]
                self.edit  = True
        
    def _delete_current ( self ):
        """ Deletes the currently selected items from the list control.
        """
        if 'delete' in self.factory.operations:
            selected = self._get_selected()
            if len( selected ) == 0:
                return
                
            delete = self.adapter.delete
            selected.reverse()
            for index in selected:
                delete( self.object, self.name, index )
                    
            self.index = index
        
    def _move_up_current ( self ):
        """ Moves the currently selected item up one line in the list control.
        """
        if 'move' in self.factory.operations:
            selected = self._get_selected()
            if len( selected ) == 1:
                index = selected[0]
                if index > 0:
                    adapter      = self.adapter
                    object, name = self.object, self.name
                    item         = adapter.get_item( object, name, index )
                    adapter.delete( object, name, index )
                    adapter.insert( object, name, index - 1, item )
                    self.index = index - 1
        
    def _move_down_current ( self ):
        """ Moves the currently selected item down one line in the list control.
        """
        if 'move' in self.factory.operations:
            selected = self._get_selected()
            if len( selected ) == 1:
                index = selected[0]
                if index < (self.control.GetItemCount() - 1):
                    adapter      = self.adapter
                    object, name = self.object, self.name
                    item         = adapter.get_item( object, name, index )
                    adapter.delete( object, name, index )
                    adapter.insert( object, name, index + 1, item )
                    self.index = index + 1
                    
    def _edit_current ( self ):
        """ Allows the user to edit the current item in the list control.
        """
        if 'edit' in self.factory.operations:
            selected = self._get_selected()
            if len( selected ) == 1:
                self.control.EditLabel( selected[0] )
                    
#-------------------------------------------------------------------------------
#  'ListStrEditor' editor factory class:
#-------------------------------------------------------------------------------

class ListStrEditor ( BasicEditorFactory ):
    """ wxPython editor factory for list of string editors.
    """
  
    #-- Trait Definitions ------------------------------------------------------
    
    # The editor class to be created:
    klass = _ListStrEditor
    
    # The optional extended name of the trait to synchronize the selection 
    # values with:
    selected = Str
    
    # The optional extended name of the trait to synchronize the selection 
    # indices with:
    selected_index = Str
    
    # The optional extended name of the trait to synchronize the activated value
    # with:
    activated = Str
    
    # The optional extended name of the trait to synchronize the activated 
    # value's index with:
    activated_index = Str
    
    # The optional extended name of the trait to synchronize the right clicked
    # value with:
    right_clicked = Str
    
    # The optional extended name of the trait to synchronize the right clicked
    # value's index with:
    right_clicked_index = Str
    
    # Can the user edit the values?
    editable = Bool( True )
                 
    # Are multiple selected items allowed?
    multi_select = Bool( False )
    
    # Should horizontal lines be drawn between items?
    horizontal_lines = Bool( False )
    
    # The title for the editor:
    title = Str
    
    # The optional extended name of the trait containing the editor title:
    title_name = Str
           
    # The adapter from list items to editor values:                       
    adapter = Instance( ListStrAdapter, () )
    
    # The optional extended name of the trait containing the adapter:
    adapter_name = Str
    
    # What type of operations are allowed on the list:
    operations = List( Enum( 'delete', 'insert', 'append', 'edit', 'move' ),
                       [ 'delete', 'insert', 'append', 'edit', 'move' ] )
                       
    # The set of images that can be used:                       
    images = List( ImageResource )  
    
