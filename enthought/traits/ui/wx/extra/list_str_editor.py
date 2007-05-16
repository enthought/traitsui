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
           Dict, TraitListEvent
    
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
#  'ListStrAdapter' class:
#-------------------------------------------------------------------------------

class ListStrAdapter ( HasPrivateTraits ):
    """ The base class for adapting list items to values that can be edited 
        by a ListStrEditor.
    """
    
    #-- Trait Definitions ------------------------------------------------------
    
    # The default background color for list items:
    bg_color = Color( None )
    
    # The default text color for list items:
    text_color = Color( None )
    
    # The name of the default image to use for list items:
    image = Str
    
    # Specifies where a dropped item should be placed in the list relative to
    # the item it is dropped on:
    drop = Enum( 'after', 'before', 'replace' )
    
    # Specifies the default value for a new list item:
    default_value = Any( '' )
    
    #-- Adapter Methods --------------------------------------------------------
    
    def can_edit ( self, object, trait, index ):
        """ Returns whether the user can edit a specified *object.trait[index]*
            list item. A True result indicates the value can be edited, while
            a False result indicates that it cannot be edited.
        """
        return True
    
    def drag ( self, object, trait, index ):
        """ Returns the 'drag' value for a specified *object.trait[index]*
            list item. A result of *None* means that the item cannot be dragged.
        """
        return self.get_text( object, trait, index )
        
    def can_drop ( self, object, trait, index, value ):
        """ Returns whether the specified *value* can be dropped on the
            specified *object.trait[index]* list item. A value of **True** means
            the *value* can be dropped; and a value of **False** indicates that
            it cannot be dropped.
        """
        return isinstance( value, basestring )
        
    def dropped ( self, object, trait, index, value ):
        """ Returns how to handle a specified *value* being dropped on a
            specified *object.trait[index]* list item. The possible return
            values are:
                
            'replace'
                Replace the item dropped on with the specified *value*.
            'before'
                Insert the specified *value* before the dropped on item.
            'after'
                Insert the specified *value* after the dropped on item.
        """
        return self.drop
        
    def get_item ( self, object, trait, index ):
        """ Returns the value of the *object.trait[index]* list item.
        """
        return getattr( object, trait )[ index ]
     
    def get_text ( self, object, trait, index ):
        """ Returns the text to display for a specified *object.trait[index]*
            list item. 
        """
        return str( self.get_item( object, trait, index ) )
        
    def set_item ( self, object, trait, index, value ):
        """ Sets the value of the *object.trait[index]* list item.
        """
        getattr( object, trait )[ index ] = value
     
    def set_text ( self, object, trait, index, text ):
        """ Sets the text for a specified *object.trait[index]* list item to
            *text*.
        """
        self.set_item( object, trait, index, text )
        
    def get_default_value ( self, object, trait ):
        """ Returns a new default value for the specified *object.trait* list.
        """
        return self.default_value
        
    def delete ( self, object, trait, index ):
        """ Deletes the specified *object.trait[index]* list item.
        """
        del getattr( object, trait )[ index ]
        
    def insert ( self, object, trait, index, value ):
        """ Inserts a new value at the specified *object.trait[index]* list 
            index.
        """
        getattr( object, trait ) [ index: index ] = [ value ]
     
    def get_bg_color ( self, object, trait, index ):
        """ Returns the background color for a specified *object.trait[index]*
            list item. A result of None means use the default list item 
            background color.
        """
        if self.bg_color is None:
            return None
            
        return self.bg_color_
        
    def get_text_color ( self, object, trait, index ):
        """ Returns the text color for a specified *object.trait[index]* list
            item. A result of None means use the default list item text color. 
        """
        if self.text_color is None:
            return None
            
        return self.text_color_
        
    def get_image ( self, object, trait, index ):
        """ Returns the name of the image to use for a specified 
            *object.trait[index]* list item. A result of None means no image
            should be used. Otherwise, the result should either be the name of
            the image, or an ImageResource item specifying the image to use.
        """
        if self.image == '':
            return None
        
        return self.image

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

    # Is the table editor is scrollable? This value overrides the default.
    scrollable = True
    
    # Index of item to select after rebuilding editor list:
    index = Any
    
    # Should the selected item be edited after rebuilding the editor list:
    edit = Bool( False )
        
    #---------------------------------------------------------------------------
    #  Finishes initializing the editor by creating the underlying toolkit
    #  widget:
    #---------------------------------------------------------------------------
        
    def init ( self, parent ):
        """ Finishes initializing the editor by creating the underlying toolkit
            widget.
        """
        # Determine the style to use for the list control:
        factory = self.factory
        style   = wx.LC_REPORT
        
        if factory.editable:
            style |= wx.LC_EDIT_LABELS 
        
        if factory.horizontal_lines:
            style |= wx.LC_HRULES
            
        if not factory.multi_select:
            style |= wx.LC_SINGLE_SEL
            
        if (factory.title == '') and (factory.title_name == ''):
            style |= wx.LC_NO_HEADER
            
        # Create the list control:
        self.control = control = wx.ListCtrl( parent, -1, style = style )
        
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
            
        # Make sure we listen for 'items' changes as well as complete list
        # replacements:
        self.context_object.on_trait_change( self.update_editor,
                                self.extended_name + '_items', dispatch = 'ui' )
        
        # Set the list control's tooltip:
        self.set_tooltip()

    def dispose ( self ):
        """ Disposes of the contents of an editor.
        """
        super( _ListStrEditor, self ).dispose()
        
        self.context_object.on_trait_change( self.update_editor,
                                  self.extended_name + '_items', remove = True )
                        
    def update_editor ( self ):
        """ Updates the editor when the object trait changes externally to the
            editor.
        """
        adapter = self.factory.adapter
        control, object, name = self.control, self.object, self.name
        control.DeleteAllItems()
        for i in range( len( self.value ) ):
            list_item = wx.ListItem()
            
            list_item.SetId( i )
            
            color = adapter.get_bg_color( object, name, i ) 
            if color is not None:
                list_item.SetBackgroundColour( color )
                
            color = adapter.get_text_color( object, name, i ) 
            if color is not None:
                list_item.SetTextColour( color )
                                    
            list_item.SetText( adapter.get_text( object, name, i ) )
            
            image = self._get_image( adapter.get_image( object, name, i ) )
            if image is not None:
                list_item.SetImage( image )
                
            control.InsertItem( list_item )
           
        index, self.index = self.index, None
        edit,  self.edit  = self.edit,  False
        if index is not None:
            if index >= control.GetItemCount():
                index -= 1
                if index < 0:
                    return
            
            control.SetItemState( index, wx.LIST_STATE_SELECTED,
                                         wx.LIST_STATE_SELECTED )
                                         
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
            adapter      = self.factory.adapter
            object, name = self.object, self.name
            index        = event.GetIndex()
            selected     = self._get_selected()
            drag_items   = []
            for index in selected:
                drag = adapter.drag( object, name, index )
                if drag is None:
                    return
                    
                drag_items.append( drag )
                
            self._drag_indices = selected
            try:
                if len( drag_items ) == 1:
                    drag_items = drag_items[0]
                    
                PythonDropSource( self.control, drag_items )
            finally:
                self._drag_indices = None
        
    def _begin_label_edit ( self, event ):
        """ Handles the user starting to edit an item label.
        """
        if not self.factory.adapter.can_edit( self.object, self.name, 
                                              event.GetIndex() ):
            event.Veto()
        
    def _end_label_edit ( self, event ):
        """ Handles the user finishing editing an item label.
        """
        self.factory.adapter.set_text( self.object, self.name, event.GetIndex(),
                                       event.GetText() )
        self.index = event.GetIndex() + 1
       
    def _item_selected ( self, event ):
        """ Handles an item being selected.
        """
        self._no_update = True
        try:
            values           = self.value
            selected_indices = self._get_selected()
            if self.factory.multi_select:
                self.multi_selected_indices = selected_indices
                self.multi_selected = [ values[ index ] 
                                        for index in selected_indices]
            elif len( selected_indices ) == 0:
                self.selected_index = -1
                self.selected       = None
            else:
                self.selected_index = selected_indices[0]
                self.selected       = values[ selected_indices[0] ]
        finally:
            self._no_update = False
            
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
        elif key == wx.WXK_UP:
            self._move_up_current()
        elif key == wx.WXK_DOWN:
            self._move_down_current()
        elif key in ( wx.WXK_LEFT, wx.WXK_RIGHT ):
            self._edit_current()
        else:
            event.Skip()

    #-- Drag and drop Event Handlers -------------------------------------------

    def wx_dropped_on ( self, x, y, data, drag_result ):
        """ Handles a Python object being dropped on the list control.
        """
        index, flags = self.control.HitTest( wx.Point( x, y ) )
        if index != -1:
            self._drop_index = index
            
            if not isinstance( data, list ):
                return self._wx_dropped_on( data, drag_result )
                
            data.reverse()
            for item in data:
                rc = self._wx_dropped_on( item, drag_result )
                    
            return rc
            
        return wx.DragNone

    def _wx_dropped_on ( self, data, drag_result ):
        adapter      = self.factory.adapter
        object, name = self.object, self.name
        index        = self._drop_index
        destination  = adapter.dropped( object, name, index, data )
        indices      = self._drag_indices
        if (indices is not None) and (drag_result == wx.DragMove):
            indices.reverse()
            for an_index in indices:
                if an_index < index:
                    index -= 1
                elif (an_index == index) and (destination == 'replace'):
                    continue
                    
                adapter.delete( object, name, an_index )
                
            self._drag_indices = None
            self._drop_index   = index
            
        if destination == 'replace':
            adapter.set_item( object, name, index, data )
        else:
            if destination == 'after':
                index += 1
            adapter.insert( object, name, index, data )
            
        return drag_result
        
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
        if ((index != -1) and 
            self.factory.adapter.can_drop( self.object, self.name, index, 
                                           data )):
            return drag_result
            
        return wx.DragNone

    #---------------------------------------------------------------------------
    #  Makes sure that the target is not the same as or a child of the source
    #  object:
    #---------------------------------------------------------------------------

    def _is_drag_ok ( self, snid, source, target ):
        if (snid is None) or (target is source):
            return False
        for cnid in self._nodes( snid ):
            if not self._is_drag_ok( cnid, self._get_node_data( cnid )[2],
                                     target ):
                return False
        return True
        
    #-- Private Methods --------------------------------------------------------
    
    def _get_image ( self, image ):
        """ Converts a user specified image to a wx.ListCtrl image index.
        """
        # fixme: NOT IMPLEMENTED YET
        return None
        
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
            adapter    = self.factory.adapter
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
                adapter = self.factory.adapter
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
                
            delete = self.factory.adapter.delete
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
                    adapter      = self.factory.adapter
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
                    adapter      = self.factory.adapter
                    object, name = self.object, self.name
                    item         = adapter.get_item( object, name, index )
                    adapter.delete( object, name, index )
                    adapter.insert( object, name, index + 1, item )
                    self.index = index + 1
                    
    def _edit_current ( self ):
        """ Allows the user to edit the current item in the list control.
        """
        if 'replace' in self.factory.operations:
            selected = self._get_selected()
            if len( selected ) == 1:
                self.control.EditLabel( selected[0] )
                    
#-------------------------------------------------------------------------------
#  Create the editor factory object:
#-------------------------------------------------------------------------------

# wxPython editor factory for list of string editors:
class ListStrEditor ( BasicEditorFactory ):
  
    #-- Trait Definitions ------------------------------------------------------
    
    # The editor class to be created:
    klass = _ListStrEditor
    
    # The optional extended name of the trait to synchronize the selection 
    # values with:
    selected = Str
    
    # The optional extended name of the trait to synchronize the selection 
    # indices with:
    selected_index = Str
    
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
    
    # What type of operations are allowed on the list:
    operations = List( Enum( 'delete', 'insert', 'append', 'replace', 'move' ),
                       [ 'delete', 'insert', 'append', 'replace', 'move' ] )
           
    # The adapter from list items to editor values:                       
    adapter = Instance( ListStrAdapter, () )
                       
    # The set of images that can be used:                       
    images = Dict( Str, Instance( ImageResource ) )  
    
