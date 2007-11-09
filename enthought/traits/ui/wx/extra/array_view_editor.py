#-------------------------------------------------------------------------------
#  
#  Defines an ArrayViewEditor for displaying 1-d or 2-d arrays of values.
#  
#  Written by: David C. Morrill
#  
#  Date: 08/29/2007
#  
#  (c) Copyright 2007 by Enthought, Inc.

#-------------------------------------------------------------------------------

""" Defines an ArrayViewEditor for displaying 1-d or 2-d arrays of values.
"""

#-- Imports --------------------------------------------------------------------

from enthought.traits.api \
    import HasTraits, Instance, Property, List, Str, Bool
    
from enthought.traits.ui.api \
    import View, Item
    
from enthought.traits.ui.wx.extra.tabular_editor \
    import TabularEditor, TabularAdapter
 
from enthought.traits.ui.wx.ui_editor \
    import UIEditor
    
from enthought.traits.ui.wx.basic_editor_factory \
    import BasicEditorFactory
    
#-- Tabular Adapter Definition -------------------------------------------------

class ArrayViewAdapter ( TabularAdapter ):
    
    # Is the array 1D or 2D?
    is_2d = Bool( True )
    
    # Should array rows and columns be transposed:
    transpose  = Bool( False )
    
    font       = 'Courier 10'
    alignment  = 'right'
    index_text = Property
    
    def _get_index_text ( self ):
        return str( self.row )
     
    def _get_content ( self ):
        if self.is_2d:
            return self.item[ self.column_id ]
            
        return self.item
        
    def get_item ( self, object, trait, row ):
        """ Returns the value of the *object.trait[row]* item.
        """
        if self.is_2d:
            if self.transpose:
                return getattr( object, trait )[:,row]
                
            return super( ArrayViewAdapter, self ).get_item( object, trait, row )
            
        return getattr( object, trait )[ row ]
    
    def len ( self, object, trait ):
        """ Returns the number of items in the specified *object.trait" list.
        """
        if self.transpose:
            return getattr( object, trait ).shape[1]
            
        return super( ArrayViewAdapter, self ).len( object, trait )

# Define the actual Traits UI string list editor:        
class _ArrayViewEditor ( UIEditor ):
    
    # Indicate that the editor is scrollable/resizable:
    scrollable = True
    
    # Should column titles be displayed:
    show_titles = Bool( False )
    
    # The tabular adapter being used for the editor view:
    adapter = Instance( ArrayViewAdapter )
    
    #-- Private Methods --------------------------------------------------------
    
    def _array_view ( self ):
        """ Return the view used by the editor.
        """
        return View(
            Item( 'object.object.' + self.name,
                  id         = 'tabular_editor',
                  show_label = False,
                  editor     = TabularEditor( show_titles = self.show_titles,
                                              editable    = False,
                                              adapter     = self.adapter )
        ),
        id        = 'array_view_editor',
        resizable = True
    )
    
    def init_ui ( self, parent ):
        """ Creates the Traits UI for displaying the array.
        """
        # Make sure that the value is an array of the correct shape:
        shape = self.value.shape
        len_shape = len( shape )
        if (len_shape == 0) or (len_shape > 2): 
            raise ValueError( "ArrayViewEditor can only display 1D or 2D "
                              "arrays" )
                              
        factory = self.factory
        cols    = 1
        titles  = [ 'Data' ]
        is_2d   = (len_shape == 2)
        if is_2d:
            index = 1
            if factory.transpose:
                index = 0
            cols             = shape[ index ]
            titles           = factory.titles
            n                = len( titles )
            self.show_titles = (n > 0)
            if self.show_titles:
                if n > cols:
                    titles = titles[:cols]
                elif n < cols:
                    if (cols % n) == 0:
                        titles, old_titles, i = [], titles, 0
                        while len( titles ) < cols:
                            titles.extend( '%s%d' % ( title, i ) 
                                           for title in old_titles )
                            i += 1
                    else:
                        titles.extend( [ '' ] * (cols - n) )
            else:
                titles = [ 'Data %d' % i for i in range( cols ) ]
            
        columns = [ ( title, i ) for i, title in enumerate( titles ) ]
        
        if factory.show_index:
            columns.insert( 0, ( 'Index', 'index' ) )
            
        self.adapter = ArrayViewAdapter( is_2d     = is_2d,
                                         columns   = columns,
                                         transpose = factory.transpose,
                                         format    = factory.format )
            
        return self.edit_traits( view   = '_array_view', 
                                 parent = parent, 
                                 kind   = 'subpanel' )

# Define the ArrayViewEditor class used by client code:        
class ArrayViewEditor ( BasicEditorFactory ):

    # The editor implementation class:
    klass = _ArrayViewEditor
    
    # Should an index column be displayed:
    show_index = Bool( True )
    
    # List of (optional) column titles:
    titles = List( Str )
    
    # Should the array be logically transposed:
    transpose = Bool( False )
    
    # The format used to display each array element:
    format = Str( '%s' )

