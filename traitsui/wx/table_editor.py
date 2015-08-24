#------------------------------------------------------------------------------
#
#  Copyright (c) 2005, Enthought, Inc.
#  All rights reserved.
#
#  This software is provided without warranty under the terms of the BSD
#  license included in enthought/LICENSE.txt and may be redistributed only
#  under the conditions described in the aforementioned license.  The license
#  is also available online at http://www.enthought.com/licenses/BSD.txt
#
#  Thanks for using Enthought open source!
#
#  Author: David C. Morrill
#  Date:   07/01/2005
#
#------------------------------------------------------------------------------

""" Defines the table editor for the wxPython user interface toolkit.
"""

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from operator import itemgetter

import wx

from traits.api \
    import Int, List, Instance, Str, Any, Button, Tuple, \
           HasPrivateTraits, Bool, Event, Property

from traitsui.api \
    import View, Item, UI, InstanceEditor, EnumEditor, Handler, SetEditor, \
           ListUndoItem

from traitsui.editors.table_editor \
    import BaseTableEditor, customize_filter

from traitsui.menu \
    import Action, ToolBar

from traitsui.table_column \
    import TableColumn, ObjectColumn

from traitsui.table_filter \
    import TableFilter

from traitsui.ui_traits \
    import SequenceTypes

from pyface.ui.wx.grid.api \
    import Grid

from pyface.dock.api \
    import DockWindow, DockSizer, DockSection, DockRegion, DockControl

from pyface.image_resource \
    import ImageResource

from pyface.timer.api \
    import do_later

from editor \
    import Editor

from table_model \
    import TableModel, TraitGridSelection

from helper import TraitsUIPanel

#-------------------------------------------------------------------------------
#  Constants:
#-------------------------------------------------------------------------------

# Mapping from TableEditor selection modes to Grid selection modes:
GridModes = {
    'row':     'rows',
    'rows':    'rows',
    'column':  'cols',
    'columns': 'cols',
    'cell':    'cell',
    'cells':   'cell'
}

#-------------------------------------------------------------------------------
#  'TableEditor' class:
#-------------------------------------------------------------------------------

class TableEditor ( Editor, BaseTableEditor ):
    """ Editor that presents data in a table. Optionally, tables can have
        a set of filters that reduce the set of data displayed, according to
        their criteria.
    """

    #---------------------------------------------------------------------------
    #  Trait definitions:
    #---------------------------------------------------------------------------

    # The set of columns currently defined on the editor:
    columns = List( TableColumn )

    # Index of currently edited (i.e., selected) table item(s):
    selected_row_index      = Int( -1 )
    selected_row_indices    = List( Int )
    selected_indices        = Property

    selected_column_index   = Int( -1 )
    selected_column_indices = List( Int )

    selected_cell_index     = Tuple( Int, Int )
    selected_cell_indices   = List( Tuple( Int, Int ) )

    # The currently selected table item(s):
    selected_row     = Any
    selected_rows    = List
    selected_items   = Property

    selected_column  = Any
    selected_columns = List

    selected_cell    = Tuple( Any, Str )
    selected_cells   = List( Tuple( Any, Str ) )

    selected_values  = Property

    # The indices of the table items currently passing the table filter:
    filtered_indices = List( Int )

    # The event fired when a cell is clicked on:
    click = Event

    # The event fired when a cell is double-clicked on:
    dclick = Event

    # Is the editor in row mode (i.e. not column or cell mode)?
    in_row_mode = Property

    # Is the editor in column mode (i.e. not row or cell mode)?
    in_column_mode = Property

    # Current filter object (should be a TableFilter or callable or None):
    filter = Any

    # The grid widget associated with the editor:
    grid = Instance( Grid )

    # The table model associated with the editor:
    model = Instance( TableModel )

    # TableEditorToolbar associated with the editor:
    toolbar = Any

    # The Traits UI associated with the table editor toolbar:
    toolbar_ui = Instance( UI )

    # Is the table editor scrollable? This value overrides the default.
    scrollable = True

    # Is 'auto_add' mode in effect? (I.e., new rows are automatically added to
    # the end of the table when the user modifies current last row.)
    auto_add = Bool( False )

    #---------------------------------------------------------------------------
    #  Finishes initializing the editor by creating the underlying toolkit
    #  widget:
    #---------------------------------------------------------------------------

    def init ( self, parent ):
        """ Finishes initializing the editor by creating the underlying toolkit
            widget.
        """

        factory       = self.factory
        self.filter   = factory.filter
        self.auto_add = (factory.auto_add and (factory.row_factory is not None))

        columns = factory.columns[:]
        if (len( columns ) == 0) and (len( self.value ) > 0):
            columns = [ ObjectColumn( name = name )
                        for name in self.value[0].editable_traits() ]
        self.columns = columns

        self.model = model = TableModel(
                                editor         = self,
                                reverse        = factory.reverse )
        model.on_trait_change( self._model_sorted, 'sorted', dispatch = 'ui' )
        mode     = factory.selection_mode
        row_mode = mode in ( 'row', 'rows' )
        selected = None
        items    = model.get_filtered_items()
        if factory.editable and (len( items ) > 0):
            selected = items[0]
        if (factory.edit_view == ' ') or (not row_mode):
            self.control = panel = TraitsUIPanel( parent, -1 )
            sizer        = wx.BoxSizer( wx.VERTICAL )
            self._create_toolbar( panel, sizer )

            # Create the table (i.e. grid) control:
            hsizer = wx.BoxSizer( wx.HORIZONTAL )
            self._create_grid( panel, hsizer )
            sizer.Add( hsizer, 1, wx.EXPAND )
        else:
            item         = self.item
            name         = item.get_label( self.ui )
            theme        = factory.dock_theme or item.container.dock_theme
            self.control = dw = DockWindow( parent, theme = theme ).control
            panel        = TraitsUIPanel( dw, -1, size = ( 300, 300 ) )
            sizer        = wx.BoxSizer( wx.VERTICAL )
            dc           = DockControl( name    = name + ' Table',
                                        id      = 'table',
                                        control = panel,
                                        style   = 'fixed' )
            contents     = [ DockRegion( contents = [ dc ] ) ]
            self._create_toolbar( panel, sizer )
            selected = None
            items    = model.get_filtered_items()
            if factory.editable and (len( items ) > 0):
                selected = items[0]

            # Create the table (i.e. grid) control:
            hsizer = wx.BoxSizer( wx.HORIZONTAL )
            self._create_grid( panel, hsizer )
            sizer.Add( hsizer, 1, wx.EXPAND )

            # Assign the initial object here, so a valid editor will be built
            # when the 'edit_traits' call is made:
            self.selected_row = selected
            self._ui = ui = self.edit_traits(
                     parent = dw,
                     kind   = 'subpanel',
                     view   = View( [ Item( 'selected_row',
                                          style  = 'custom',
                                          editor = InstanceEditor(
                                                       view = factory.edit_view,
                                                       kind = 'subpanel' ),
                                          resizable = True,
                                          width  = factory.edit_view_width,
                                          height = factory.edit_view_height ),
                                      '|<>' ],
                                    resizable = True,
                                    handler   = factory.edit_view_handler ) )

            # Set the parent UI of the new UI to our own UI:
            ui.parent = self.ui

            # Reset the object so that the sub-sub-view will pick up the
            # correct history also:
            self.selected_row = None
            self.selected_row = selected

            dc.style = item.dock
            contents.append( DockRegion( contents = [
                                 DockControl( name    = name + ' Editor',
                                              id      = 'editor',
                                              control = ui.control,
                                              style   = item.dock ) ] ) )

            # Finish setting up the DockWindow:
            dw.SetSizer( DockSizer( contents = DockSection(
                          contents = contents,
                          is_row   = (factory.orientation == 'horizontal') ) ) )

        # Set up the required externally synchronized traits (if any):
        sv      = self.sync_value
        is_list = (mode[-1] == 's')
        sv( factory.click,  'click',  'to' )
        sv( factory.dclick, 'dclick', 'to' )
        sv( factory.filter_name,  'filter',  'from' )
        sv( factory.columns_name, 'columns', is_list = True )
        sv( factory.filtered_indices, 'filtered_indices', 'to' )
        sv( factory.selected, 'selected_%s' % mode, is_list = is_list )
        if is_list:
            sv( factory.selected_indices, 'selected_%s_indices' % mode[:-1],
                is_list = True )
        else:
            sv( factory.selected_indices, 'selected_%s_index' % mode )

        # Listen for the selection changing on the grid:
        self.grid.on_trait_change(
            getattr( self, '_selection_%s_updated' % mode ),
            'selection_changed', dispatch = 'ui' )

        # Make sure the selection is initialized:
        if row_mode:
            self.set_selection( items[0:1] )
        else:
            self.set_selection()


        # Set the min height of the grid panel to 0, this will provide
        # a scrollbar if the window is resized such that only the first row
        # is visible
        panel.SetMinSize((-1, 0))

        # Finish the panel layout setup:
        panel.SetSizer( sizer )


    #---------------------------------------------------------------------------
    #  Creates the associated grid control used to implement the table:
    #---------------------------------------------------------------------------

    def _create_grid ( self, parent, sizer ):
        """ Creates the associated grid control used to implement the table.
        """
        factory        = self.factory
        selection_mode = GridModes[ factory.selection_mode ]
        if factory.selection_bg_color is None:
            selection_mode = ''

        self.grid = grid = Grid( parent,
            model                        = self.model,
            enable_lines                 = factory.show_lines,
            grid_line_color              = factory.line_color,
            show_row_headers             = factory.show_row_labels,
            show_column_headers          = factory.show_column_labels,
            default_cell_font            = factory.cell_font,
            default_cell_text_color      = factory.cell_color,
            default_cell_bg_color        = factory.cell_bg_color,
            default_cell_read_only_color = factory.cell_read_only_bg_color,
            default_label_font           = factory.label_font,
            default_label_text_color     = factory.label_color,
            default_label_bg_color       = factory.label_bg_color,
            selection_bg_color           = factory.selection_bg_color,
            selection_text_color         = factory.selection_color,
            autosize                     = factory.auto_size,
            read_only                    = not factory.editable,
            edit_on_first_click          = factory.edit_on_first_click,
            selection_mode               = selection_mode,
            allow_column_sort            = factory.sortable,
            allow_row_sort               = False,
            column_label_height          = factory.column_label_height,
            row_label_width              = factory.row_label_width
        )
        _grid = grid._grid
        _grid.SetScrollLineY( factory.scroll_dy )

        # Set the default size for each table row:
        height = factory.row_height
        if height <= 0:
            height = _grid.GetTextExtent( 'My' )[1] + 9
        _grid.SetDefaultRowSize( height )

        # Allow the table to be resizable if the user did not explicitly
        # specify a number of rows to display:
        self.scrollable = (factory.rows == 0)

        # Calculate a reasonable default size for the table:
        if len( self.model.get_filtered_items() ) > 0:
            height = _grid.GetRowSize( 0 )

        max_rows = factory.rows or 15

        min_width = max( 150, 80 * len( self.columns ) )

        if factory.show_column_labels:
            min_height = _grid.GetColLabelSize() + (max_rows * height)
        else:
            min_height = (max_rows * height)

        _grid.SetMinSize(wx.Size(min_width, min_height))

        # On Linux, there is what appears to be a bug in wx in which the
        # vertical scrollbar will not be sized properly if the TableEditor is
        # sized to be shorter than the minimum height specified above. Since
        # this height is only set to ensure that the TableEditor is sized
        # correctly during the initial UI layout, we un-set it after this takes
        # place (addresses ticket 1810)
        def clear_minimum_height ( info ):
            min_size = _grid.GetMinSize()
            min_size.height = 0
            _grid.SetMinSize ( min_size )
        self.ui.add_defined ( clear_minimum_height )

        sizer.Add( grid.control, 1, wx.EXPAND )

        return grid.control

    #---------------------------------------------------------------------------
    #  Creates the table editing tool bar:
    #---------------------------------------------------------------------------

    def _create_toolbar ( self, parent, sizer ):
        """ Creates the table editing toolbar.
        """

        factory = self.factory
        if not factory.show_toolbar:
            return

        toolbar = TableEditorToolbar( parent = parent, editor = self )
        if (toolbar.control is not None) or (len( factory.filters ) > 0):
            tb_sizer = wx.BoxSizer( wx.HORIZONTAL )

            if len( factory.filters ) > 0:
                view = View( [ Item( 'filter<250>{View}',
                                     editor = factory._filter_editor ), '_',
                               Item( 'filter_summary<100>{Results}~',
                                     object = 'model', resizable = False ), '_',
                               '-' ],
                             resizable = True )
                self.toolbar_ui = ui = view.ui(
                              context = { 'object': self, 'model': self.model },
                              parent  = parent,
                              kind    = 'subpanel' ).set(
                              parent  = self.ui )
                tb_sizer.Add( ui.control, 0 )

            if toolbar.control is not None:
                self.toolbar = toolbar
                # add padding so the toolbar is right aligned
                tb_sizer.Add( ( 1, 1 ), 1, wx.EXPAND )
                tb_sizer.Add( toolbar.control, 0 )

            sizer.Add( tb_sizer, 0, wx.ALIGN_RIGHT | wx.EXPAND )

    #---------------------------------------------------------------------------
    #  Disposes of the contents of an editor:
    #---------------------------------------------------------------------------

    def dispose ( self ):
        """ Disposes of the contents of an editor.
        """
        if self.toolbar_ui is not None:
            self.toolbar_ui.dispose()

        if self._ui is not None:
            self._ui.dispose()

        self.grid.on_trait_change( getattr( self,
            '_selection_%s_updated' % self.factory.selection_mode ),
            'selection_changed', remove = True )

        self.model.on_trait_change( self._model_sorted, 'sorted',
                                    remove = True )

        self.grid.dispose()
        self.model.dispose()

        # Break any links needed to allow garbage collection:
        self.grid = self.model = self.toolbar = None

        super( TableEditor, self ).dispose()

    #---------------------------------------------------------------------------
    #  Updates the editor when the object trait changes external to the editor:
    #---------------------------------------------------------------------------

    def update_editor ( self ):
        """ Updates the editor when the object trait changes externally to the
            editor.
        """
        # fixme: Do we need to override this method?
        pass

    #---------------------------------------------------------------------------
    #  Refreshes the editor control:
    #---------------------------------------------------------------------------

    def refresh ( self ):
        """ Refreshes the editor control.
        """
        self.grid._grid.Refresh()

    #---------------------------------------------------------------------------
    #  Sets the current selection to a set of specified objects:
    #---------------------------------------------------------------------------

    def set_selection ( self, objects = [], notify = True ):
        """ Sets the current selection to a set of specified objects.
        """
        if not isinstance( objects, SequenceTypes ):
            objects = [ objects ]

        self.grid.set_selection( [ TraitGridSelection( obj = object )
                                   for object in objects ], notify = notify )

    #---------------------------------------------------------------------------
    #  Sets the current selection to a set of specified object/column pairs:
    #---------------------------------------------------------------------------

    def set_extended_selection ( self, *pairs ):
        """ Sets the current selection to a set of specified object/column
            pairs.
        """
        if (len( pairs ) == 1) and isinstance( pairs[0], list ):
            pairs = pairs[0]

        grid_selections = [TraitGridSelection(obj = object, name = name)
                           for object, name in pairs]

        self.grid.set_selection(grid_selections)

    #---------------------------------------------------------------------------
    #  Creates a new row object using the provided factory:
    #---------------------------------------------------------------------------

    def create_new_row ( self ):
        """ Creates a new row object using the provided factory.
        """
        factory = self.factory
        kw      = factory.row_factory_kw.copy()
        if '__table_editor__' in kw:
            kw[ '__table_editor__' ] = self

        return self.ui.evaluate( factory.row_factory,
                                 *factory.row_factory_args, **kw  )

    #---------------------------------------------------------------------------
    #  Adds a new object as a new row after the currently selected indices:
    #---------------------------------------------------------------------------

    def add_row ( self, object = None, index = None ):
        """ Adds a specified object as a new row after the specified index.
        """
        filtered_items = self.model.get_filtered_items

        if index is None:
            indices = self.selected_indices
            if len( indices ) == 0:
                indices = [ len( filtered_items() ) - 1 ]
            indices.reverse()
        else:
            indices = [ index ]

        if object is None:
            objects = []
            for index in indices:
                object = self.create_new_row()
                if object is None:
                    if self.in_row_mode:
                        self.set_selection()
                    return

                objects.append( object )
        else:
            objects = [ object ]

        items             = []
        insert_item_after = self.model.insert_filtered_item_after
        in_row_mode       = self.in_row_mode
        for i, index in enumerate( indices ):
            object = objects[i]
            index, extend = insert_item_after( index, object )

            if in_row_mode and (object in filtered_items()):
                items.append( object )

            self._add_undo( ListUndoItem( object = self.object,
                                          name   = self.name,
                                          index  = index,
                                          added  = [ object ] ), extend )

        if in_row_mode:
            self.set_selection( items )

    #---------------------------------------------------------------------------
    #  Moves a column from one place to another:
    #---------------------------------------------------------------------------

    def move_column ( self, from_column, to_column ):
        """ Moves the specified **from_column** from its current position to
            just preceding the specified **to_column**.
        """
        columns = self.columns
        frm     = columns.index( from_column )
        if to_column is None:
            to = len( columns )
        else:
            to = columns.index( to_column )
        del columns[ frm ]
        columns.insert( to - (frm < to), from_column )

        return True

    #-- Property Implementations -----------------------------------------------

    def _get_selected_indices ( self ):
        sm = self.factory.selection_mode
        if sm == 'rows':
            return self.selected_row_indices

        elif sm == 'row':
            index = self.selected_row_index
            if index >= 0:
                return [ index ]

        elif sm == 'cells':
            return list( set( [ row_col[0] for
                                row_col in self.selected_cell_indices ] ) )

        elif sm == 'cell':
            index = self.selected_cell_index[0]
            if index >= 0:
                return [ index ]

        return []

    def _get_selected_items ( self ):
        sm = self.factory.selection_mode
        if sm == 'rows':
            return self.selected_rows

        elif sm == 'row':
            item = self.selected_row
            if item is not None:
                return [ item ]

        elif sm == 'cells':
            return list( set( [ item_name[0]
                                for item_name in self.selected_cells ] ) )

        elif sm == 'cell':
            item = self.selected_cell[0]
            if item is not None:
                return [ item ]

        return []

    def _get_selected_values ( self ):
        if self.in_row_mode:
            return [ ( item, '' ) for item in self.selected_items ]

        if self.in_column_mode:
            if self.factory.selection_mode == 'columns':
                return [ ( None, column ) for column in self.selected_columns ]

            column = self.selected_column
            if column != '':
                return [ ( None, column ) ]

            return []

        if self.factory.selection_mode == 'cells':
            return self.selected_cells

        item = self.selected_cell
        if item[0] is not None:
            return [ item ]

        return []

    def _get_in_row_mode ( self ):
        return (self.factory.selection_mode in ( 'row', 'rows' ))

    def _get_in_column_mode ( self ):
        return (self.factory.selection_mode in ( 'column', 'columns' ))

    #-- UI preference save/restore interface -----------------------------------

    #---------------------------------------------------------------------------
    #  Restores any saved user preference information associated with the
    #  editor:
    #---------------------------------------------------------------------------

    def restore_prefs ( self, prefs ):
        """ Restores any saved user preference information associated with the
            editor.
        """
        factory = self.factory
        try:
            filters = prefs.get( 'filters', None )
            if filters is not None:
                factory.filters = ([ f for f in factory.filters if f.template ]
                                 + [ f for f in filters if not f.template ])

            columns = prefs.get( 'columns' )
            if columns is not None:
                new_columns = []
                all_columns = self.columns + factory.other_columns
                for column in columns:
                    for column2 in all_columns:
                        if column == column2.get_label():
                            new_columns.append( column2 )
                            break
                self.columns = new_columns

                # Restore the column sizes if possible:
                if not factory.auto_size:
                    widths = prefs.get( 'widths' )
                    if widths is not None:
                        # fixme: Talk to Jason about a better way to do this:
                        self.grid._user_col_size = True

                        set_col_size = self.grid._grid.SetColSize
                        for i, width in enumerate( widths ):
                            if width >= 0:
                                set_col_size( i, width )

            structure = prefs.get( 'structure' )
            if (structure is not None) and (factory.edit_view != ' '):
                self.control.GetSizer().SetStructure( self.control, structure )
        except:
            pass

    #---------------------------------------------------------------------------
    #  Returns any user preference information associated with the editor:
    #---------------------------------------------------------------------------

    def save_prefs ( self ):
        """ Returns any user preference information associated with the editor.
        """
        get_col_size = self.grid._grid.GetColSize
        result = {
            'filters': [ f for f in self.factory.filters if not f.template ],
            'columns': [ c.get_label() for c in self.columns ],
            'widths':  [ get_col_size( i )
                         for i in range( len( self.columns ) ) ]
        }

        if self.factory.edit_view != ' ':
            result[ 'structure' ] = self.control.GetSizer().GetStructure()

        return result

    #-- Public Methods ---------------------------------------------------------

    def filter_modified ( self ):
        """ Handles updating the selection when some aspect of the current
            filter has changed.
        """
        values = self.selected_values
        if len( values ) > 0:
            if self.in_column_mode:
                self.set_extended_selection( values )
            else:
                items = self.model.get_filtered_items()
                self.set_extended_selection(
                         [ item for item in values if item[0] in items ] )

    #-- Event Handlers ---------------------------------------------------------

    #---------------------------------------------------------------------------
    #  Handles the user selecting items (rows, columns, cells) in the table:
    #---------------------------------------------------------------------------

    def _selection_row_updated ( self, event ):
        """ Handles the user selecting items (rows, columns, cells) in the
            table.
        """
        gfi  = self.model.get_filtered_item
        rio  = self.model.raw_index_of
        tl   = self.grid._grid.GetSelectionBlockTopLeft()
        br   = iter( self.grid._grid.GetSelectionBlockBottomRight() )
        rows = len( self.model.get_filtered_items() )
        if self.auto_add:
            rows -= 1

        # Get the row items and indices in the selection:
        values = []
        for row0, col0 in tl:
            row1, col1 = br.next()
            for row in xrange( row0, row1 + 1 ):
                if row < rows:
                    values.append( ( rio( row ), gfi( row ) ) )

        if len( values ) > 0:
            # Sort by increasing row index:
            values.sort(key=itemgetter(0))
            index, row = values[0]
        else:
            index, row = -1, None

        # Save the new selection information:
        self.set( selected_row_index  = index,
                  trait_change_notify = False )
        self.setx( selected_row = row )

        # Update the toolbar status:
        self._update_toolbar( row is not None )

        # Invoke the user 'on_select' handler:
        self.ui.evaluate( self.factory.on_select, row )

    def _selection_rows_updated ( self, event ):
        """ Handles multiple row selection changes.
        """
        gfi  = self.model.get_filtered_item
        rio  = self.model.raw_index_of
        tl   = self.grid._grid.GetSelectionBlockTopLeft()
        br   = iter( self.grid._grid.GetSelectionBlockBottomRight() )
        rows = len( self.model.get_filtered_items() )
        if self.auto_add:
            rows -= 1

        # Get the row items and indices in the selection:
        values = []
        for row0, col0 in tl:
            row1, col1 = br.next()
            for row in xrange( row0, row1 + 1 ):
                if row < rows:
                    values.append( ( rio( row ), gfi( row ) ) )

        # Sort by increasing row index:
        values.sort(key=itemgetter(0))

        # Save the new selection information:
        self.trait_set( selected_row_indices = [ v[0] for v in values ],
                        trait_change_notify  = False )
        rows = [ v[1] for v in values ]
        self.setx( selected_rows = rows )

        # Update the toolbar status:
        self._update_toolbar( len( values ) > 0 )

        # Invoke the user 'on_select' handler:
        self.ui.evaluate( self.factory.on_select, rows )

    def _selection_column_updated ( self, event ):
        """ Handles single column selection changes.
        """
        cols = self.columns
        tl   = self.grid._grid.GetSelectionBlockTopLeft()
        br   = iter( self.grid._grid.GetSelectionBlockBottomRight() )

        # Get the column items and indices in the selection:
        values = []
        for row0, col0 in tl:
            row1, col1 = br.next()
            for col in xrange( col0, col1 + 1 ):
                values.append( ( col, cols[ col ].name ) )

        if len( values ) > 0:
            # Sort by increasing column index:
            values.sort(key=itemgetter(0))
            index, column = values[0]
        else:
            index, column = -1, ''

        # Save the new selection information:
        self.set( selected_column_index = index,
                  trait_change_notify   = False )
        self.setx( selected_column = column )

        # Invoke the user 'on_select' handler:
        self.ui.evaluate( self.factory.on_select, column )

    def _selection_columns_updated ( self, event ):
        """ Handles multiple column selection changes.
        """
        cols = self.columns
        tl   = self.grid._grid.GetSelectionBlockTopLeft()
        br   = iter( self.grid._grid.GetSelectionBlockBottomRight() )

        # Get the column items and indices in the selection:
        values = []
        for row0, col0 in tl:
            row1, col1 = br.next()
            for col in xrange( col0, col1 + 1 ):
                values.append( ( col, cols[ col ].name ) )

        # Sort by increasing row index:
        values.sort(key=itemgetter(0))

        # Save the new selection information:
        self.set( selected_column_indices = [ v[0] for v in values ],
                  trait_change_notify     = False )
        columns = [ v[1] for v in values ]
        self.setx( selected_columns = columns )

        # Invoke the user 'on_select' handler:
        self.ui.evaluate( self.factory.on_select, columns )

    def _selection_cell_updated ( self, event ):
        """ Handles single cell selection changes.
        """
        tl = self.grid._grid.GetSelectionBlockTopLeft()
        if len( tl ) == 0:
            return

        gfi  = self.model.get_filtered_item
        rio  = self.model.raw_index_of
        cols = self.columns
        br   = iter( self.grid._grid.GetSelectionBlockBottomRight() )

        # Get the column items and indices in the selection:
        values = []
        for row0, col0 in tl:
            row1, col1 = br.next()
            for row in xrange( row0, row1 + 1 ):
                item = gfi( row )
                for col in xrange( col0, col1 + 1 ):
                    values.append( ( ( rio( row ), col ),
                                     ( item, cols[ col ].name ) ) )

        if len( values ) > 0:
            # Sort by increasing row, column index:
            values.sort(key=itemgetter(0))
            index, cell = values[0]
        else:
            index, cell = ( -1, -1 ), ( None, '' )

        # Save the new selection information:
        self.set( selected_cell_index = index,
                  trait_change_notify = False )
        self.setx( selected_cell = cell )

        # Update the toolbar status:
        self._update_toolbar( len( values ) > 0 )

        # Invoke the user 'on_select' handler:
        self.ui.evaluate( self.factory.on_select, cell )

    def _selection_cells_updated ( self, event ):
        """ Handles multiple cell selection changes.
        """
        gfi  = self.model.get_filtered_item
        rio  = self.model.raw_index_of
        cols = self.columns
        tl   = self.grid._grid.GetSelectionBlockTopLeft()
        br   = iter( self.grid._grid.GetSelectionBlockBottomRight() )

        # Get the column items and indices in the selection:
        values = []
        for row0, col0 in tl:
            row1, col1 = br.next()
            for row in xrange( row0, row1 + 1 ):
                item = gfi( row )
                for col in xrange( col0, col1 + 1 ):
                    values.append( ( ( rio( row ), col ),
                                     ( item, cols[ col ].name ) ) )

        # Sort by increasing row, column index:
        values.sort(key=itemgetter(0))

        # Save the new selection information:
        self.setx( selected_cell_indices = [ v[0] for v in values ])
        cells = [ v[1] for v in values ]
        self.setx( selected_cells = cells )

        # Update the toolbar status:
        self._update_toolbar( len( cells ) > 0 )

        # Invoke the user 'on_select' handler:
        self.ui.evaluate( self.factory.on_select, cells )

    def _selected_row_changed ( self, item ):
        if not self._no_notify:
            if item is None:
                self.set_selection( notify = False )
            else:
                self.set_selection( item, notify = False )

    def _selected_row_index_changed ( self, row ):
        if not self._no_notify:
            if row < 0:
                self.set_selection( notify = False )
            else:
                self.set_selection( self.value[ row ], notify = False )

    def _selected_rows_changed ( self, items ):
        if not self._no_notify:
            self.set_selection( items, notify = False )

    def _selected_row_indices_changed ( self, indices ):
        if not self._no_notify:
            value = self.value
            self.set_selection( [ value[i] for i in indices ], notify = False )

    def _selected_column_changed ( self, name ):
        if not self._no_notify:
            self.set_extended_selection( ( None, name ) )

    def _selected_column_index_changed ( self, index ):
        if not self._no_notify:
            if index < 0:
                self.set_extended_selection()
            else:
                self.set_extended_selection(
                    ( None, self.model.get_column_name[ index ] ) )

    def _selected_columns_changed ( self, names ):
        if not self._no_notify:
            self.set_extended_selection( [ ( None, name ) for name in names ] )

    def _selected_column_indices_changed ( self, indices ):
        if not self._no_notify:
            gcn = self.model.get_column_name
            self.set_extended_selection( [ ( None, gcn(i) ) for i in indices ] )

    def _selected_cell_changed ( self, cell ):
        if not self._no_notify:
            self.set_extended_selection( [ cell ] )

    def _selected_cell_index_changed ( self, pair ):
        if not self._no_notify:
            row, column = pair
            if (row < 0) or (column < 0):
                self.set_extended_selection()
            else:
                self.set_extended_selection(
                    ( self.value[ row ],
                      self.model.get_column_name[ column ] ) )

    def _selected_cells_changed ( self, cells ):
        if not self._no_notify:
            self.set_extended_selection( cells )

    def _selected_cell_indices_changed ( self, pairs ):
        if not self._no_notify:
            value = self.value
            gcn   = self.model.get_column_name
            new_selection = [(value[row], gcn(col)) for row, col in pairs]
            self.set_extended_selection(new_selection)

    def _update_toolbar ( self, has_selection ):
        """ Updates the toolbar after a selection change.
        """
        toolbar = self.toolbar
        if toolbar is not None:
            no_filter = (self.filter is None)
            if has_selection:
                indices = self.selected_indices
                start   = indices[0]
                n       = len( self.model.get_filtered_items() ) - 1
                delete  = toolbar.delete
                if self.auto_add:
                    n -= 1
                    delete.enabled = (start <= n)
                else:
                    delete.enabled = True

                deletable = self.factory.deletable
                if delete.enabled and callable( deletable ):
                    delete.enabled = reduce( lambda l, r: l and r,
                        [ deletable( item ) for item in self.selected_items ],
                        True )

                toolbar.search.enabled    = toolbar.add.enabled = True
                toolbar.move_up.enabled   = (no_filter and (start > 0))
                toolbar.move_down.enabled = (no_filter and (indices[-1] < n))
            else:
                toolbar.add.enabled     = no_filter
                toolbar.search.enabled  = toolbar.delete.enabled    = \
                toolbar.move_up.enabled = toolbar.move_down.enabled = False

    #---------------------------------------------------------------------------
    #  Handles the contents of the model being resorted:
    #---------------------------------------------------------------------------

    def _model_sorted ( self ):
        """ Handles the contents of the model being resorted.
        """
        if self.toolbar is not None:
            self.toolbar.no_sort.enabled = True

        values = self.selected_values
        if len( values ) > 0:
            do_later( self.set_extended_selection, values )

    #---------------------------------------------------------------------------
    #  Handles the current filter being changed:
    #---------------------------------------------------------------------------

    def _filter_changed ( self, old_filter, new_filter ):
        """ Handles the current filter being changed.
        """
        if new_filter is customize_filter:
            do_later( self._customize_filters, old_filter )

        elif self.model is not None:
            if ((new_filter is not None) and
                (not isinstance( new_filter, TableFilter ))):
                new_filter = TableFilter( allowed = new_filter )
            self.model.filter = new_filter
            self.filter_modified()

    #---------------------------------------------------------------------------
    #  Refresh the list of available filters:
    #---------------------------------------------------------------------------

    def _refresh_filters ( self, filters ):
        factory = self.factory
        # hack: The following line forces the 'filters' to be changed...
        factory.filters = []
        factory.filters = filters

    #---------------------------------------------------------------------------
    #  Allows the user to customize the current set of table filters:
    #---------------------------------------------------------------------------

    def _customize_filters ( self, filter ):
        """ Allows the user to customize the current set of table filters.
        """
        factory = self.factory
        filter_editor = TableFilterEditor( editor = self, filter = filter )
        enum_editor   = EnumEditor( values = factory.filters[:], mode = 'list' )
        ui = filter_editor.edit_traits( parent = self.control, view = View(
            [ [ Item( 'filter<200>@',
                      editor    = enum_editor,
                      resizable = True ),
                '|<>' ],
              [ 'edit:edit', 'new', 'apply', 'delete:delete',
                '|<>' ],
              '-' ],
            title   = 'Customize Filters',
            kind    = 'livemodal',
            height  = .25,
            buttons = [ 'OK', 'Cancel' ] ) )

        if ui.result:
            self._refresh_filters( enum_editor.values )
            self.filter = filter_editor.filter
        else:
            self.filter = filter

    #---------------------------------------------------------------------------
    #  Handles the user requesting that columns not be sorted:
    #---------------------------------------------------------------------------

    def on_no_sort ( self ):
        """ Handles the user requesting that columns not be sorted.
        """
        self.model.no_column_sort()
        self.toolbar.no_sort.enabled = False
        values = self.selected_values
        if len( values ) > 0:
            self.set_extended_selection( values )

    #---------------------------------------------------------------------------
    #  Handles the user requesting to move the current item up one row:
    #---------------------------------------------------------------------------

    def on_move_up ( self ):
        """ Handles the user requesting to move the current item up one row.
        """
        model   = self.model
        objects = []
        for index in self.selected_indices:
            objects.append( model.get_filtered_item( index ) )
            index -= 1
            object = model.get_filtered_item( index )
            model.delete_filtered_item_at( index )
            model.insert_filtered_item_after( index, object )

        if self.in_row_mode:
            self.set_selection( objects )
        else:
            self.set_extended_selection( self.selected_values )

    #---------------------------------------------------------------------------
    #  Handles the user requesting to move the current item down one row:
    #---------------------------------------------------------------------------

    def on_move_down ( self ):
        """ Handles the user requesting to move the current item down one row.
        """
        model   = self.model
        objects = []
        indices = self.selected_indices[:]
        indices.reverse()
        for index in indices:
            object = model.get_filtered_item( index )
            objects.append( object )
            model.delete_filtered_item_at( index )
            model.insert_filtered_item_after( index, object )

        if self.in_row_mode:
            self.set_selection( objects )
        else:
            self.set_extended_selection( self.selected_values )

    #---------------------------------------------------------------------------
    #  Handles the user requesting a table search:
    #---------------------------------------------------------------------------

    def on_search ( self ):
        """ Handles the user requesting a table search.
        """
        self.factory.search.edit_traits(
            parent  = self.control,
            view    = 'searchable_view',
            handler = TableSearchHandler( editor = self )
        )

    #---------------------------------------------------------------------------
    #  Handles the user requesting to add a new row to the table:
    #---------------------------------------------------------------------------

    def on_add ( self ):
        """ Handles the user requesting to add a new row to the table.
        """
        self.add_row()

    #---------------------------------------------------------------------------
    #  Handles the user requesting to delete the currently selected items of the
    #  table:
    #---------------------------------------------------------------------------

    def on_delete ( self ):
        """ Handles the user requesting to delete the currently selected items
            of the table.
        """
        # Get the selected row indices:
        indices = self.selected_indices[:]
        values  = self.selected_values[:]
        indices.reverse()

        # Make sure that we don't delete any rows while an editor is open in it
        self.grid.stop_editing_indices(indices)

        # Delete the selected rows:
        for i in indices:
            index, object = self.model.delete_filtered_item_at( i )
            self._add_undo( ListUndoItem( object  = self.object,
                                          name    = self.name,
                                          index   = index,
                                          removed = [ object ] ) )

        # Compute the new selection and set it:
        items = self.model.get_filtered_items()
        n     = len( items ) - 1
        indices.reverse()
        for i in range( len( indices ) - 1, -1, -1 ):
            if indices[i] > n:
                indices[i] = n
                if indices[i] < 0:
                    del indices[i]
                    del values[i]

        n = len( indices )
        if n > 0:
            if self.in_row_mode:
                self.set_selection(
                    list( set( [ items[i] for i in indices ] ) ) )
            else:
                self.set_extended_selection(
                    list( set( [ ( items[ indices[i] ], values[i][1] )
                                 for i in range( n ) ] ) ) )
        else:
            self._update_toolbar( False )

    #---------------------------------------------------------------------------
    #  Handles the user requesting to set the user preference items for the
    #  table:
    #---------------------------------------------------------------------------

    def on_prefs ( self ):
        """ Handles the user requesting to set the user preference items for the
            table.
        """
        columns = self.columns[:]
        columns.extend( [ c
            for c in (self.factory.columns + self.factory.other_columns)
            if c not in columns ] )
        self.edit_traits(
            parent = self.control,
            view   = View( [ Item( 'columns',
                                resizable = True,
                                editor    = SetEditor( values       = columns,
                                                       ordered      = True,
                                                       can_move_all = False ) ),
                             '|<>' ],
                         title     = 'Select and Order Columns',
                         width     = 0.3,
                         height    = 0.3,
                         resizable = True,
                         buttons   = [ 'Undo', 'OK', 'Cancel' ],
                         kind      = 'livemodal' ) )

    #---------------------------------------------------------------------------
    #  Prepares to have a context menu action called:
    #---------------------------------------------------------------------------

    def prepare_menu ( self, row, column ):
        """ Prepares to have a context menu action called.
        """
        object    = self.model.get_filtered_item( row )
        selection = [ x.obj for x in self.grid.get_selection() ]
        if object not in selection:
            self.set_selection( object )
            selection = [ object ]
        self.set_menu_context( selection, object, column )

    #---------------------------------------------------------------------------
    #  Set one or more attributes without notifying the grid model:
    #---------------------------------------------------------------------------

    def setx ( self, **keywords ):
        """ Set one or more attributes without notifying the grid model.
        """
        self._no_notify = True

        for name, value in keywords.items():
            setattr( self, name, value )

        self._no_notify = False

#-- Private Methods: -----------------------------------------------------------

    #---------------------------------------------------------------------------
    #  Adds an 'undo' item to the undo history (if any):
    #---------------------------------------------------------------------------

    def _add_undo ( self, undo_item, extend = False ):
        history = self.ui.history
        if history is not None:
            history.add( undo_item, extend )

#-------------------------------------------------------------------------------
#  'TableFilterEditor' class:
#-------------------------------------------------------------------------------

class TableFilterEditor ( Handler ):
    """ Editor that manages table filters.
    """

    #---------------------------------------------------------------------------
    #  Trait definitions:
    #---------------------------------------------------------------------------

    # TableEditor this editor is associated with
    editor = Instance( TableEditor )

    # Current filter
    filter = Instance( TableFilter, allow_none = True )

    # Edit the current filter
    edit = Button

    # Create a new filter and edit it
    new = Button

    # Apply the current filter to the editor's table
    apply = Button

    # Delete the current filter
    delete = Button

    #---------------------------------------------------------------------------
    #  'Handler' interface:
    #---------------------------------------------------------------------------

    def init ( self, info ):
        """ Initializes the controls of a user interface.
        """
        # Save both the original filter object reference and its contents:
        if self.filter is None:
            self.filter = info.filter.factory.values[0]
        self._filter = self.filter
        self._filter_copy = self.filter.clone_traits()

    def closed ( self, info, is_ok ):
        """ Handles a dialog-based user interface being closed by the user.
        """
        if not is_ok:
            # Restore the contents of the original filter:
            self._filter.copy_traits( self._filter_copy )

    #---------------------------------------------------------------------------
    #  Event handlers:
    #---------------------------------------------------------------------------

    def object_filter_changed ( self, info ):
        """ Handles a new filter being selected.
        """
        filter              = info.object.filter
        info.edit.enabled   = (not filter.template)
        info.delete.enabled = ((not filter.template) and
                               (len( info.filter.factory.values ) > 1))

    def object_edit_changed ( self, info ):
        """ Handles the user clicking the **Edit** button.
        """
        if info.initialized:
            items = self.editor.model.get_filtered_items()
            if len(items) > 0:
                item = items[0]
            else:
                item = None
            # `item` is now either the first item in the table, or None if
            # the table is empty.
            ui = self.filter.edit(item)
            if ui.result:
                self._refresh_filters( info )

    def object_new_changed ( self, info ):
        """ Handles the user clicking the **New** button.
        """
        if info.initialized:
            # Get list of available filters and find the current filter in it:
            factory = info.filter.factory
            filters = factory.values
            filter  = self.filter
            index   = filters.index( filter ) + 1
            n       = len( filters )
            while (index < n) and filters[ index ].template:
                index += 1

            # Create a new filter based on the current filter:
            new_filter          = filter.clone_traits()
            new_filter.template = False
            new_filter.name     = new_filter._name = 'New filter'

            # Add it to the list of filters:
            filters.insert( index, new_filter )
            self._refresh_filters( info )

            # Set up the new filter as the current filter and edit it:
            self.filter = new_filter
            do_later( self._delayed_edit, info )

    def object_apply_changed ( self, info ):
        """ Handles the user clicking the **Apply** button.
        """
        if info.initialized:
            self.init( info )
            self.editor._refresh_filters( info.filter.factory.values )
            self.editor.filter = self.filter

    def object_delete_changed ( self, info ):
        """ Handles the user clicking the **Delete** button.
        """
        # Get the list of available filters:
        filters = info.filter.factory.values

        if info.initialized:
            # Delete the current filter:
            index = filters.index( self.filter )
            del filters[ index ]

            # Select a new filter:
            if index >= len( filters ):
                index -= 1
            self.filter = filters[ index ]
            self._refresh_filters( info )

    #---------------------------------------------------------------------------
    #  Private methods:
    #---------------------------------------------------------------------------

    def _refresh_filters ( self, info ):
        """ Refresh the filter editor's list of filters.
        """
        factory = info.filter.factory
        values, factory.values = factory.values, []
        factory.values = values

    def _delayed_edit ( self, info ):
        """ Edits the current filter, and deletes it if the user cancels the
            edit.
        """
        ui = self.filter.edit( self.editor.model.get_filtered_item( 0 ) )
        if not ui.result:
            self.object_delete_changed( info )
        else:
            self._refresh_filters( info )

        # Allow deletion as long as there is more than 1 filter:
        if (not self.filter.template) and len( info.filter.factory.values ) > 1:
            info.delete.enabled = True

#-------------------------------------------------------------------------------
#  'TableEditorToolbar' class:
#-------------------------------------------------------------------------------

class TableEditorToolbar ( HasPrivateTraits ):
    """ Toolbar displayed in table editors.
    """

    #---------------------------------------------------------------------------
    #  Trait definitions:
    #---------------------------------------------------------------------------

    # Do not sort columns:
    no_sort = Instance( Action,
                        { 'name':    'No Sorting',
                          'tooltip': 'Do not sort columns',
                          'action':  'on_no_sort',
                          'enabled': False,
                          'image':   ImageResource( 'table_no_sort.png' ) } )

    # Move current object up one row:
    move_up = Instance( Action,
                        { 'name':    'Move Up',
                          'tooltip': 'Move current item up one row',
                          'action':  'on_move_up',
                          'enabled': False,
                          'image':   ImageResource( 'table_move_up.png' ) } )

    # Move current object down one row:
    move_down = Instance( Action,
                          { 'name':    'Move Down',
                            'tooltip': 'Move current item down one row',
                            'action':  'on_move_down',
                            'enabled': False,
                            'image':   ImageResource( 'table_move_down.png' ) })

    # Search the table:
    search = Instance( Action,
                       { 'name':    'Search',
                         'tooltip': 'Search table',
                         'action':  'on_search',
                         'image':   ImageResource( 'table_search.png' ) } )

    # Add a row:
    add = Instance( Action,
                    { 'name':    'Add',
                      'tooltip': 'Insert new item',
                      'action':  'on_add',
                      'image':   ImageResource( 'table_add.png' ) } )

    # Delete selected row:
    delete = Instance( Action,
                       { 'name':    'Delete',
                         'tooltip': 'Delete current item',
                         'action':  'on_delete',
                         'enabled': False,
                         'image':   ImageResource( 'table_delete.png' ) } )

    # Edit the user preferences:
    prefs = Instance( Action,
                      { 'name':    'Preferences',
                        'tooltip': 'Set user preferences for table',
                        'action':  'on_prefs',
                        'image':   ImageResource( 'table_prefs.png' ) } )

    # The table editor that this is the toolbar for:
    editor = Instance( TableEditor )

    # The toolbar control:
    control = Any

    #---------------------------------------------------------------------------
    #  Initializes the toolbar for a specified window:
    #---------------------------------------------------------------------------

    def __init__ ( self, parent = None, **traits ):
        super( TableEditorToolbar, self ).__init__( **traits )
        editor  = self.editor
        factory = editor.factory
        actions = []

        if factory.sortable and (not factory.sort_model):
            actions.append( self.no_sort )

        if (not editor.in_column_mode) and factory.reorderable:
            actions.append( self.move_up )
            actions.append( self.move_down )

        if editor.in_row_mode and (factory.search is not None):
            actions.append( self.search )

        if factory.editable:
            if (factory.row_factory is not None) and (not factory.auto_add):
                actions.append( self.add )

            if (factory.deletable != False) and (not editor.in_column_mode):
                actions.append( self.delete )

        if factory.configurable:
            actions.append( self.prefs )

        if len( actions ) > 0:
            toolbar = ToolBar( image_size      = ( 16, 16 ),
                               show_tool_names = False,
                               show_divider    = False,
                               *actions )
            self.control = toolbar.create_tool_bar( parent, self )
            self.control.SetBackgroundColour( parent.GetBackgroundColour() )

            # fixme: Why do we have to explictly set the size of the toolbar?
            #        Is there some method that needs to be called to do the
            #        layout?
            self.control.SetSize( wx.Size( 23 * len( actions ), 16 ) )

    #---------------------------------------------------------------------------
    #  PyFace/Traits menu/toolbar controller interface:
    #---------------------------------------------------------------------------

    def add_to_menu ( self, menu_item ):
        """ Adds a menu item to the menu bar being constructed.
        """
        pass

    def add_to_toolbar ( self, toolbar_item ):
        """ Adds a toolbar item to the too bar being constructed.
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

    def perform ( self, action, action_event = None ):
        """ Performs the action described by a specified Action object.
        """
        getattr( self.editor, action.action )()

#-------------------------------------------------------------------------------
#  'TableSearchHandler' class:
#-------------------------------------------------------------------------------

class TableSearchHandler ( Handler ):
    """ Handler for saerching a table.
    """

    #---------------------------------------------------------------------------
    #  Trait definitions:
    #---------------------------------------------------------------------------

    # The editor that this handler is associated with
    editor = Instance( TableEditor )

    # Find next matching item
    find_next = Button( 'Find Next' )

    # Find previous matching item
    find_previous = Button( 'Find Previous' )

    # Select all matching items
    select = Button

    # The user is finished searching
    OK = Button( 'Close' )

    # Search status message:
    status = Str

    #---------------------------------------------------------------------------
    #  Handles the user clicking the 'Find next' button:
    #---------------------------------------------------------------------------

    def handler_find_next_changed ( self, info ):
        """ Handles the user clicking the **Find** button.
        """
        if info.initialized:
            editor = self.editor
            items  = editor.model.get_filtered_items()

            for i in range( editor.selected_row_index + 1, len( items ) ):
                if info.object.filter( items[i] ):
                    self.status = 'Item %d matches' % ( i + 1 )
                    editor.set_selection( items[i] )
                    editor.selected_row_index = i
                    break
            else:
                self.status = 'No more matches found'

    #---------------------------------------------------------------------------
    #  Handles the user clicking the 'Find previous' button:
    #---------------------------------------------------------------------------

    def handler_find_previous_changed ( self, info ):
        """ Handles the user clicking the **Find previous** button.
        """
        if info.initialized:
            editor = self.editor
            items  = editor.model.get_filtered_items()

            for i in range( editor.selected_row_index - 1, -1, -1 ):
                if info.object.filter( items[i] ):
                    self.status = 'Item %d matches' % ( i + 1 )
                    editor.set_selection( items[i] )
                    editor.selected_row_index = i
                    break
            else:
                self.status = 'No more matches found'

    #---------------------------------------------------------------------------
    #  Handles the user clicking the 'Select' button:
    #---------------------------------------------------------------------------

    def handler_select_changed ( self, info ):
        """ Handles the user clicking the **Select** button.
        """
        if info.initialized:
            editor = self.editor
            filter = info.object.filter
            items  = [ item for item in editor.model.get_filtered_items()
                       if filter( item ) ]
            editor.set_selection( items )

            if len( items ) == 1:
                self.status = '1 item selected'
            else:
                self.status = '%d items selected' % len( items )

    #---------------------------------------------------------------------------
    #  Handles the user clicking 'OK' button:
    #---------------------------------------------------------------------------

    def handler_OK_changed ( self, info ):
        """ Handles the user clicking the OK button.
        """
        if info.initialized:
            info.ui.dispose()

# Define the SimpleEditor class.
SimpleEditor = TableEditor

# Define the ReadonlyEditor class.
ReadonlyEditor = TableEditor
