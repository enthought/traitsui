#------------------------------------------------------------------------------
# Copyright (c) 2005, Enthought, Inc.
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in enthought/LICENSE.txt and may be redistributed only
# under the conditions described in the aforementioned license.  The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
# Thanks for using Enthought open source!
#
# Author: Enthought, Inc.
# Description: <Enthought pyface package component>
#------------------------------------------------------------------------------
""" A grid control with a model/ui architecture. """

# Major package imports
import sys
import wx
import wx.lib.gridmovers as grid_movers
from os.path import abspath, exists
from wx.grid import Grid as wxGrid
from wx.grid import GridCellAttr, GridCellBoolRenderer, PyGridTableBase
from wx.grid import GridTableMessage, \
     GRIDTABLE_NOTIFY_ROWS_APPENDED, GRIDTABLE_NOTIFY_ROWS_DELETED,  \
     GRIDTABLE_NOTIFY_ROWS_INSERTED, GRIDTABLE_NOTIFY_COLS_APPENDED, \
     GRIDTABLE_NOTIFY_COLS_DELETED,  GRIDTABLE_NOTIFY_COLS_INSERTED, \
     GRIDTABLE_REQUEST_VIEW_GET_VALUES, GRID_VALUE_STRING
from wx import TheClipboard

# Enthought library imports
from enthought.pyface.api import Sorter, Widget
from enthought.pyface.timer.api import do_later
from enthought.traits.api import Bool, Color, Enum, Event, Font, Instance, Int, \
     List, Trait
from enthought.util.wx.drag_and_drop import PythonDropSource, \
     PythonDropTarget, PythonObject
from enthought.util.wx.drag_and_drop import clipboard as enClipboard
from enthought.traits.ui.wx.dnd_editor import FileDropSource

# local imports
from grid_model import GridModel
from combobox_focus_handler import ComboboxFocusHandler

# Is this code running on MS Windows?
is_win32 = (sys.platform == 'win32')

ASCII_C = 67

class Grid(Widget):
    """ A grid control with a model/ui architecture. """

    #### 'Grid' interface #####################################################

    # The model that provides the data for the grid.
    model = Instance(GridModel, ())

    # Should grid lines be shown on the table?
    enable_lines = Bool(True)

    # The color to show gridlines in
    grid_line_color = Color("blue")

    # Show row headers?
    show_row_headers = Bool(True)

    # Show column headers?
    show_column_headers = Bool(True)

    # The default font to use for text in labels
    default_label_font = Font(None)

    # The default background color for labels
    default_label_bg_color = Color(wx.Colour(236, 233, 216))

    # The default text color for labels
    default_label_text_color = Color("black")

    # The color to use for a selection background
    selection_bg_color = Trait(wx.Colour(49, 106, 197), None, Color)

    # The color to use for a selection foreground/text
    selection_text_color = Trait(wx.Colour(255, 255, 255), None, Color)

    # The default font to use for text in cells
    default_cell_font = Font(None)

    # The default text color to use for text in cells
    default_cell_text_color = Color("black")

    # The default background color to use for editable cells
    default_cell_bg_color = Color("white")

    # The default background color to use for read-only cells
    #default_cell_read_only_color = Trait(Color("linen"), None, Color)
    default_cell_read_only_color = Color(wx.Colour(248, 247, 241))

    # Should the grid be read-only? If this is set to false, individual
    # cells can still declare themselves read-only.
    read_only = Bool(False)

    # Selection mode.
    selection_mode = Enum('cell', 'rows', 'cols', '')

    # Sort data when a column header is clicked?
    allow_column_sort = Bool(True)

    # Sort data when a row header is clicked?
    allow_row_sort = Bool(False)

    # pixel height of column labels
    column_label_height = Int(32)

    # pixel width of row labels
    row_label_width = Int(82)

    # auto-size columns and rows?
    autosize = Bool(False)

    # Allow single-click access to cell-editors?
    edit_on_first_click = Bool(True)

    #### Events ####

    # A cell has been activated (ie. double-clicked).
    cell_activated = Event

    # The current selection has changed.
    selection_changed = Event

    # A drag operation was started on a cell.
    cell_begin_drag = Event

    # A left-click occurred on a cell.
    cell_left_clicked = Event

    # A left-click occurred on a cell at specific location
    # Useful if the cell contains multiple controls though the hit test
    # is left to the consumer of the event
    cell_left_clicked_location = Event

    # A right-click occurred on a cell.
    cell_right_clicked = Event

    # protected variables to store the location of the clicked event
    _x_clicked = Int
    _y_clicked = Int

    ###########################################################################
    # 'object' interface.
    ###########################################################################
    def __init__(self, parent, **traits):
        """ Creates a new grid.

        'parent' is the toolkit-specific control that is the grid's parent.

        """

        # Base class constructors.
        super(Grid, self).__init__(**traits)

        # Flag set when columns are resizing:
        self._user_col_size = False

        # Create the toolkit-specific control.
        self.control = self._grid = grid = wxGrid(parent, -1)
        grid.grid    = self

        # Set when moving edit cursor:
        grid._no_reset_col = False
        grid._no_reset_row = False

        # initialize the current selection
        self.__current_selection = ()

        self.__initialize_counts(self.model)
        self.__initialize_sort_state()

        # Don't display any extra space around the rows and columns.
        grid.SetMargins(0, 0)

        # Provides more accurate scrolling behavior without creating large
        # margins on the bottom and right. The down side is that it makes
        # scrolling using the scroll bar buttons painfully slow:
        grid.SetScrollLineX(1)
        grid.SetScrollLineY(1)

        # Tell the grid to get its data from the model.
        #
        # N.B The terminology used in the wxPython API is a little confusing!
        # --- The 'SetTable' method is actually setting the model used by
        #     the grid (which is the view)!
        #
        # The second parameter to 'SetTable' tells the grid to take ownership
        # of the model and to destroy it when it is done.  Otherwise you would
        # need to keep a reference to the model and manually destroy it later
        # (by calling it's Destroy method).
        #
        # fixme: We should create a default model if one is not supplied.

        # The wx virtual table hook.

        self._grid_table_base = _GridTableBase(self.model, self)

        grid.SetTable(self._grid_table_base, True)

        # Enable column and row moving:
        grid_movers.GridColMover(grid)
        grid_movers.GridRowMover(grid)
        grid.Bind(grid_movers.EVT_GRID_COL_MOVE, self._on_col_move, grid)
        grid.Bind(grid_movers.EVT_GRID_ROW_MOVE, self._on_row_move, grid)

        smotc = self.model.on_trait_change
        otc   = self.on_trait_change
        smotc(self._on_model_content_changed, 'content_changed')
        smotc(self._on_model_structure_changed, 'structure_changed')
        smotc(self._on_row_sort, 'row_sorted')
        smotc(self._on_column_sort, 'column_sorted')
        otc(self._on_new_model, 'model')

        # hook up style trait handlers - note that we have to use
        # dynamic notification hook-ups because these handlers should
        # not be called until after the control object is initialized.
        # static trait notifiers get called when the object inits.
        otc(self._on_enable_lines_changed, 'enable_lines')
        otc(self._on_grid_line_color_changed, 'grid_line_color')
        otc(self._on_default_label_font_changed, 'default_label_font')
        otc(self._on_default_label_bg_color_changed, 'default_label_bg_color')
        otc(self._on_default_label_text_color_changed,
            'default_label_text_color')
        otc(self._on_selection_bg_color_changed, 'selection_bg_color')
        otc(self._on_selection_text_color_changed, 'selection_text_color')
        otc(self._on_default_cell_font_changed, 'default_cell_font')
        otc(self._on_default_cell_text_color_changed, 'default_cell_text_color')
        otc(self._on_default_cell_bg_color_changed, 'default_cell_bg_color')
        otc(self._on_read_only_changed, 'read_only_changed')
        otc(self._on_selection_mode_changed, 'selection_mode')
        otc(self._on_column_label_height_changed, 'column_label_height')
        otc(self._on_row_label_width_changed, 'row_label_width')
        otc(self._on_show_column_headers_changed, 'show_column_headers')
        otc(self._on_show_row_headers_changed, 'show_row_headers')

        # Initialize wx handlers:
        self._notify_select = True
        wx.grid.EVT_GRID_SELECT_CELL(grid, self._on_select_cell)
        wx.grid.EVT_GRID_RANGE_SELECT(grid, self._on_range_select)
        wx.grid.EVT_GRID_COL_SIZE(grid, self._on_col_size)
        wx.grid.EVT_GRID_ROW_SIZE(grid, self._on_row_size)

        # This starts the cell editor on a double-click as well as on a second
        # click:
        wx.grid.EVT_GRID_CELL_LEFT_DCLICK(grid, self._on_cell_left_dclick)

        # Notify when cells are clicked on:
        wx.grid.EVT_GRID_CELL_RIGHT_CLICK(grid, self._on_cell_right_click)
        wx.grid.EVT_GRID_CELL_RIGHT_DCLICK(grid, self._on_cell_right_dclick)

        wx.grid.EVT_GRID_LABEL_RIGHT_CLICK(grid, self._on_label_right_click)
        wx.grid.EVT_GRID_LABEL_LEFT_CLICK(grid, self._on_label_left_click)

        #wx.grid.EVT_GRID_EDITOR_CREATED(grid, self._on_editor_created)
        if is_win32:
            wx.grid.EVT_GRID_EDITOR_HIDDEN(grid, self._on_editor_hidden)

        # We handle key presses to change the behavior of the <Enter> and
        # <Tab> keys to make manual data entry smoother.
        wx.EVT_KEY_DOWN(grid, self._on_key_down)

        # We handle control resize events to adjust column widths
        wx.EVT_SIZE(grid, self._on_size)

        # Handle drags:
        self._corner_window = grid.GetGridCornerLabelWindow()
        self._grid_window   = gw = grid.GetGridWindow()
        self._row_window    = rw = grid.GetGridRowLabelWindow()
        self._col_window    = cw = grid.GetGridColLabelWindow()

        # Handle mouse button state changes:
        self._ignore = False
        for window in ( gw, rw, cw ):
            wx.EVT_MOTION(    window, self._on_grid_motion )
            wx.EVT_LEFT_DOWN( window, self._on_left_down )
            wx.EVT_LEFT_UP(   window, self._on_left_up )

        wx.EVT_PAINT(self._grid_window, self._on_grid_window_paint)

        # Initialize the row and column models:
        self.__initialize_rows(self.model)
        self.__initialize_columns(self.model)
        self.__initialize_fonts()

        # Handle trait style settings:
        self.__initialize_style_settings()

        # Enable the grid as a drag and drop target:
        self._grid.SetDropTarget(PythonDropTarget(self))

        self.__autosize()

        self._edit = False
        wx.EVT_IDLE(grid, self._on_idle)

    def dispose(self):
        # Remove all wx handlers:
        grid = self._grid
        wx.grid.EVT_GRID_SELECT_CELL(       grid, None )
        wx.grid.EVT_GRID_RANGE_SELECT(      grid, None )
        wx.grid.EVT_GRID_COL_SIZE(          grid, None )
        wx.grid.EVT_GRID_ROW_SIZE(          grid, None )
        wx.grid.EVT_GRID_CELL_LEFT_DCLICK(  grid, None )
        wx.grid.EVT_GRID_CELL_RIGHT_CLICK(  grid, None )
        wx.grid.EVT_GRID_CELL_RIGHT_DCLICK( grid, None )
        wx.grid.EVT_GRID_LABEL_RIGHT_CLICK( grid, None )
        wx.grid.EVT_GRID_LABEL_LEFT_CLICK(  grid, None )
        wx.grid.EVT_GRID_EDITOR_CREATED(    grid, None )
        if is_win32:
            wx.grid.EVT_GRID_EDITOR_HIDDEN( grid, None )
        wx.EVT_KEY_DOWN(                    grid, None )
        wx.EVT_SIZE(                        grid, None )
        wx.EVT_PAINT( self._grid_window, None )

        for window in ( self._grid_window , self._row_window ,
                        self._col_window ):
            wx.EVT_MOTION(    window, None )
            wx.EVT_LEFT_DOWN( window, None )
            wx.EVT_LEFT_UP(   window, None )

        otc = self.on_trait_change
        otc(self._on_enable_lines_changed, 'enable_lines',
            remove = True)
        otc(self._on_grid_line_color_changed, 'grid_line_color',
            remove = True)
        otc(self._on_default_label_font_changed, 'default_label_font',
            remove = True)
        otc(self._on_default_label_bg_color_changed, 'default_label_bg_color',
            remove = True)
        otc(self._on_default_label_text_color_changed,
            'default_label_text_color',
            remove = True)
        otc(self._on_selection_bg_color_changed, 'selection_bg_color',
            remove = True)
        otc(self._on_selection_text_color_changed, 'selection_text_color',
            remove = True)
        otc(self._on_default_cell_font_changed, 'default_cell_font',
            remove = True)
        otc(self._on_default_cell_text_color_changed, 'default_cell_text_color',
            remove = True)
        otc(self._on_default_cell_bg_color_changed, 'default_cell_bg_color',
            remove = True)
        otc(self._on_read_only_changed, 'read_only_changed',
            remove = True)
        otc(self._on_selection_mode_changed, 'selection_mode',
            remove = True)
        otc(self._on_column_label_height_changed, 'column_label_height',
            remove = True)
        otc(self._on_row_label_width_changed, 'row_label_width',
            remove = True)
        otc(self._on_show_column_headers_changed, 'show_column_headers',
            remove = True)
        otc(self._on_show_row_headers_changed, 'show_row_headers',
            remove = True)

        self._grid_table_base.dispose()

    ###########################################################################
    # Trait event handlers.
    ###########################################################################

    def _on_new_model(self):
        """ When we get a new model reinitialize grid match to that model. """

        self._grid_table_base.model = self.model

        self.__initialize_counts(self.model)

        self._on_model_changed()

        if self.autosize:
            # Note that we don't call AutoSize() here, because autosizing
            # the rows looks like crap.
            self._grid.AutoSizeColumns(False)

        return

    def _on_model_content_changed(self):
        """ A notification method called when the data in the underlying
            model changes. """

        # Note: We're seeing some wx 2.6 weirdness in the traits TableEditor
        #       because of what's going on here. TextEditors and ComboEditors
        #       update the trait value for every character typed. The
        #       TableEditor catches these changes and fires the
        #       model_content_changed event. In this routine we then update
        #       the values in the table by sending the
        #       wxGRIDTABLE_REQUEST_VIEW_GET_VALUES message, which at the
        #       c++ grid level forces the editor to close. So those editors
        #       don't allow you to type more than one character before closing.
        #       For now, we are fixing this in those specific editors, but
        #       we may need a more general solution at some point.

        # make sure we update for any new values in the table
        #msg = GridTableMessage(self._grid_table_base,
        #                       GRIDTABLE_REQUEST_VIEW_GET_VALUES)
        #self._grid.ProcessTableMessage(msg)

        self._grid.ForceRefresh()

    def _on_model_structure_changed(self, *arg, **kw):
        """ A notification method called when the underlying model has
        changed. Responsible for making sure the view object updates
        correctly. """

        # Disable any active editors in order to prevent a wx crash bug:
        self._edit = False
        grid       = self._grid

        # Make sure any current active editor has been disabled:
        grid.DisableCellEditControl()

        # More wacky fun with wx. We have to manufacture the appropriate
        # grid messages and send them off to make sure the grid updates
        # correctly:
        should_autosize = False

        # First check to see if rows have been added or deleted:
        row_count       = self.model.get_row_count()
        delta           = row_count - self._row_count
        self._row_count = row_count

        if delta > 0:
            # Rows were added:
            msg = GridTableMessage(self._grid_table_base,
                                   GRIDTABLE_NOTIFY_ROWS_APPENDED, delta)
            grid.ProcessTableMessage(msg)
            should_autosize = True
        elif delta < 0:
            # Rows were deleted:
            msg = GridTableMessage(self._grid_table_base,
                                   GRIDTABLE_NOTIFY_ROWS_DELETED,
                                   row_count, -delta)
            grid.ProcessTableMessage(msg)
            should_autosize = True

        # Now check for column changes:
        col_count       = self.model.get_column_count()
        delta           = col_count - self._col_count
        self._col_count = col_count

        if delta > 0:
            # Columns were added:
            msg = GridTableMessage(self._grid_table_base,
                                   GRIDTABLE_NOTIFY_COLS_APPENDED, delta)
            grid.ProcessTableMessage(msg)
            should_autosize = True
        elif delta < 0:
            # Columns were deleted:
            msg = GridTableMessage(self._grid_table_base,
                                   GRIDTABLE_NOTIFY_COLS_DELETED,
                                   col_count, -delta)
            grid.ProcessTableMessage(msg)
            should_autosize = True

        # Finally make sure we update for any new values in the table:
        msg = GridTableMessage(self._grid_table_base,
                               GRIDTABLE_REQUEST_VIEW_GET_VALUES)
        grid.ProcessTableMessage(msg)

        if should_autosize:
            self.__autosize()

        # We have to make sure the editor/renderer cache in the GridTableBase
        # object is cleaned out:
        self._grid_table_base._clear_cache()

        grid.AdjustScrollbars()
        self._refresh()

    def _on_row_sort(self, evt):
        """ Handles a row_sorted event from the underlying model. """

        # First grab the new data out of the event:
        if evt.index < 0:
            self._current_sorted_row = None
        else:
            self._current_sorted_row = evt.index

        self._row_sort_reversed = evt.reversed

        # Since the label may have changed we may need to autosize again:
        # fixme: when we change how we represent the sorted column
        #        this should go away.
        self.__autosize()

        # Make sure everything updates to reflect the changes:
        self._on_model_structure_changed()

    def _on_column_sort(self, evt):
        """ Handles a column_sorted event from the underlying model. """

        # first grab the new data out of the event
        if evt.index < 0:
            self._current_sorted_col = None
        else:
            self._current_sorted_col = evt.index

        self._col_sort_reversed = evt.reversed

        # since the label may have changed we may need to autosize again
        # fixme: when we change how we represent the sorted column
        #        this should go away.
        self.__autosize()

        # make sure everything updates to reflect the changes
        self._on_model_structure_changed()

    def _on_enable_lines_changed(self):
        """ Handle a change to the enable_lines trait. """
        self._grid.EnableGridLines(self.enable_lines)

    def _on_grid_line_color_changed(self):
        """ Handle a change to the enable_lines trait. """
        self._grid.SetGridLineColour(self.grid_line_color)

    def _on_default_label_font_changed(self):
        """ Handle a change to the default_label_font trait. """

        font = self.default_label_font
        if font is None:
            font = wx.SystemSettings_GetFont(wx.SYS_DEFAULT_GUI_FONT)
            font.SetWeight(wx.BOLD)

        self._grid.SetLabelFont(font)

    def _on_default_label_text_color_changed(self):
        """ Handle a change to the default_cell_text_color trait. """

        if self.default_label_text_color is not None:
            color = self.default_label_text_color
            self._grid.SetLabelTextColour(color)
            self._grid.ForceRefresh()

    def _on_default_label_bg_color_changed(self):
        """ Handle a change to the default_cell_text_color trait. """

        if self.default_label_bg_color is not None:
            color = self.default_label_bg_color
            self._grid.SetLabelBackgroundColour(color)
            self._grid.ForceRefresh()

    def _on_selection_bg_color_changed(self):
        """ Handle a change to the selection_bg_color trait. """
        if self.selection_bg_color is not None:
            self._grid.SetSelectionBackground(self.selection_bg_color)

    def _on_selection_text_color_changed(self):
        """ Handle a change to the selection_text_color trait. """
        if self.selection_text_color is not None:
            self._grid.SetSelectionForeground(self.selection_text_color)

    def _on_default_cell_font_changed(self):
        """ Handle a change to the default_cell_font trait. """

        if self.default_cell_font is not None:
            self._grid.SetDefaultCellFont(self.default_cell_font)
            self._grid.ForceRefresh()

    def _on_default_cell_text_color_changed(self):
        """ Handle a change to the default_cell_text_color trait. """

        if self.default_cell_text_color is not None:
            color = self.default_cell_text_color
            self._grid.SetDefaultCellTextColour(color)
            self._grid.ForceRefresh()

    def _on_default_cell_bg_color_changed(self):
        """ Handle a change to the default_cell_bg_color trait. """

        if self.default_cell_bg_color is not None:
            color = self.default_cell_bg_color
            self._grid.SetDefaultCellBackgroundColour(color)
            self._grid.ForceRefresh()

    def _on_read_only_changed(self):
        """ Handle a change to the read_only trait. """

        # should the whole grid be read-only?
        if self.read_only:
            self._grid.EnableEditing(False)
        else:
            self._grid.EnableEditing(True)

    def _on_selection_mode_changed(self):
        """ Handle a change to the selection_mode trait. """

        # should we allow individual cells to be selected or only rows
        # or only columns
        if self.selection_mode == 'cell':
            self._grid.SetSelectionMode(wxGrid.wxGridSelectCells)
        elif self.selection_mode == 'rows':
            self._grid.SetSelectionMode(wxGrid.wxGridSelectRows)
        elif self.selection_mode == 'cols':
            self._grid.SetSelectionMode(wxGrid.wxGridSelectColumns)

    def _on_column_label_height_changed(self):
        """ Handle a change to the column_label_height trait. """

        # handle setting for height of column labels
        if self.column_label_height is not None:
            self._grid.SetColLabelSize(self.column_label_height)

    def _on_row_label_width_changed(self):
        """ Handle a change to the row_label_width trait. """
        # handle setting for width of row labels
        if self.row_label_width is not None:
            self._grid.SetRowLabelSize(self.row_label_width)

    def _on_show_column_headers_changed(self):
        """ Handle a change to the show_column_headers trait. """

        if not self.show_column_headers:
            self._grid.SetColLabelSize(0)
        else:
            self._grid.SetColLabelSize(self.column_label_height)

    def _on_show_row_headers_changed(self):
        """ Handle a change to the show_row_headers trait. """

        if not self.show_row_headers:
            self._grid.SetRowLabelSize(0)
        else:
            self._grid.SetRowLabelSize(self.row_label_width)

    ###########################################################################
    # 'Grid' interface.
    ###########################################################################

    def get_selection(self):
        """ Return a list of the currently selected objects. """

        return self.__get_selection()

    def set_selection(self, selection_list, notify=True):
        """ Set the current selection to the objects listed in selection_list.
        Note that these objects are model-specific, as the grid depends on the
        underlying model to translate these objects into grid coordinates.
        A ValueError will be raised if the objects are not in the proper format
        for the underlying model. """

        # Set the 'should we notify the model of the selection change' flag:
        self._notify_select = notify

        # First use the model to resolve the object list into a set of
        # grid coordinates
        cells = self.model.resolve_selection(selection_list)

        # Now make sure all those grid coordinates get set properly:
        grid = self._grid
        grid.BeginBatch()

        grid.ClearSelection()

        mode = self.selection_mode
        if mode == 'rows':
            self._select_rows(cells)
        elif mode != '':
            for selection in cells:
                row, col = max( 0, selection[0] ), max( 0, selection[1] )
                grid.SelectBlock(row, col, row, col, True)

        grid.EndBatch()

        # Indicate that the selection has been changed:
        if notify:
            self.__fire_selection_changed()

        self._notify_select = True

    def stop_editing_indices(self, indices):
        """ If editing is occuring in a row in 'indices', stop editing. """

        if self._grid.GetGridCursorRow() in indices:
            self._grid.DisableCellEditControl()

    ###########################################################################
    # wx event handlers.
    ###########################################################################

    def _on_size(self, evt):
        """ Called when the grid is resized. """
        self.__autosize()

    # needed to handle problem in wx 2.6 with combobox cell editors
    def _on_editor_created(self, evt):

        editor = evt.GetControl()
        if editor is not None:
            editor.PushEventHandler(ComboboxFocusHandler(self._grid))

        evt.Skip()

    def _on_editor_hidden(self, evt):
        # This is a hack to make clicking on a window button while a grid
        # editor is active work correctly under Windows. Normally, when the
        # user clicks on the button to exit grid cell editing and perform the
        # button function, only the grid cell editing is terminated under
        # Windows. A second click on the button is required to actually
        # trigger the button functionality. We circumvent this problem by
        # generating a 'fake' button click event. Technically this solution
        # is not correct since the button click should be generated on mouse
        # up, but I'm not sure if we will get the mouse up event, so we do it
        # here instead. Note that this handler is only set-up when the OS is
        # Windows.
        control = wx.FindWindowAtPointer()
        if isinstance(control, wx.Button):
            do_later(wx.PostEvent, control,
                     wx.CommandEvent(wx.wxEVT_COMMAND_BUTTON_CLICKED,
                                     control.GetId()))

    def _on_grid_window_paint(self, evt):

        # fixme: this is a total h*ck to get rid of the scrollbars that appear
        # on a grid under wx2.6 when it starts up. these appear whether or
        # not needed, and disappear as soon as the grid is resized. hopefully
        # we will be able to remove this egregious code on some future version
        # of wx.
        self._grid.SetColSize(0, self._grid.GetColSize(0) + 1)
        self._grid.SetColSize(0, self._grid.GetColSize(0) - 1)

        evt.Skip()

    def _on_left_down ( self, evt ):
        """ Called when the left mouse button is pressed.
        """
        grid            = self._grid
        self._x_clicked = evt.GetX()
        self._y_clicked = evt.GetY()
        self._ignore = ((grid.XToEdgeOfCol(evt.GetX()) != wx.NOT_FOUND) or
                        (grid.YToEdgeOfRow(evt.GetY()) != wx.NOT_FOUND))
        evt.Skip()

    def _on_left_up ( self, evt ):
        """ Called when the left mouse button is released.
        """
        self._ignore = False
        evt.Skip()

    def _on_motion(self, evt):
        """ Called when the mouse moves. """

        evt.Skip()
        if evt.Dragging() and not evt.ControlDown():
            data = self.__get_drag_value()
            if isinstance(data, basestring):
                file = abspath(data)
                if exists(file):
                    FileDropSource(self._grid, file)
                    return

            PythonDropSource(self._grid, data)

    def _on_grid_motion(self, evt):
        if evt.GetEventObject() is self._grid_window:
            x, y = self._grid.CalcUnscrolledPosition(evt.GetPosition())
            row  = self._grid.YToRow(y)
            col  = self._grid.XToCol(x)

            # Notify the model that the mouse has moved into the cell at row,col,
            # only if the row and col are valid.
            if (row >= 0) and (col >= 0):
                self.model.mouse_cell = (row, col)

            # If we are not ignoring mouse events, call _on_motion.
            if not self._ignore:
                self._on_motion(evt)

        evt.Skip()

    def _on_select_cell(self, evt):
        """ Called when the user has moved to another cell. """
        row, col = evt.GetRow(), evt.GetCol()
        self.cell_left_clicked = self.model.click = (row, col)

        # Try to find a renderer for this cell:
        renderer = self.model.get_cell_renderer(row, col)

        # If the renderer has defined a handler then call it:
        result = False
        if renderer is not None:
            result = renderer.on_left_click(self, row, col)

        # if the handler didn't tell us to stop further handling then skip
        if not result:
            if (self.selection_mode != '') or (not self.edit_on_first_click):
                self._grid.SelectBlock(row, col, row, col, evt.ControlDown())

            self._edit = True
            evt.Skip()

    def _on_range_select(self, evt):
        if evt.Selecting():
            if (self.selection_mode == 'cell') and evt.ControlDown():
                self._grid.SelectBlock(evt.GetTopRow(), evt.GetLeftCol(),
                                    evt.GetBottomRow(), evt.GetRightCol(), True)

        if self._notify_select:
            self.__fire_selection_changed()

    def _on_col_size(self, evt):
        """ Called when the user changes a column's width. """
        self.__autosize()

        evt.Skip()

    def _on_row_size(self, evt):
        """ Called when the user changes a row's height. """
        self._grid.AdjustScrollbars()

        evt.Skip()

    def _on_idle(self, evt):
        """ Immediately jumps into editing mode, bypassing the
            usual select mode of a spreadsheet. See also self.OnSelectCell().
        """
        if self._edit == True and self.edit_on_first_click:
            if self._grid.CanEnableCellControl():
                self._grid.EnableCellEditControl()
            self._edit = False

        evt.Skip()

    def _on_cell_left_dclick(self, evt):
        """ Called when the left mouse button was double-clicked.

        From the wxPython demo code:-

        'I do this because I don't like the default behaviour of not starting
        the cell editor on double clicks, but only a second click.'

        Fair enuff!

        """
        row, col = evt.GetRow(), evt.GetCol()
        data     = self.model.get_value(row, col)
        self.cell_activated = data

        # Tell the model that a cell was double-clicked on:
        self.model.dclick = (row, col)

        # Try to find a renderer for this cell
        renderer = self.model.get_cell_renderer(row, col)

        # If the renderer has defined a handler then call it
        if renderer is not None:
            renderer.on_left_dclick(self, row, col)

    def _on_cell_right_dclick(self, evt):
        """ Called when the right mouse button was double-clicked.

        From the wxPython demo code:-

        'I do this because I don't like the default behaviour of not starting
        the cell editor on double clicks, but only a second click.'

        Fair enuff!

        """
        row, col = evt.GetRow(), evt.GetCol()

        # try to find a renderer for this cell
        renderer = self.model.get_cell_renderer(row, col)

        # if the renderer has defined a handler then call it
        if renderer is not None:
            renderer.on_right_dclick(self, row, col)

    def _on_cell_right_click(self, evt):
        """ Called when a right click occurred in a cell. """
        row, col = evt.GetRow(), evt.GetCol()

        # try to find a renderer for this cell
        renderer = self.model.get_cell_renderer(row, col)

        # if the renderer has defined a handler then call it
        result = False
        if renderer is not None:
            result = renderer.on_right_click(self, row, col)

        # if the handler didn't tell us to stop further handling then skip
        if not result:
            # ask model for the appropriate context menu
            menu_manager = self.model.get_cell_context_menu(row, col)
            # get the underlying menu object
            if menu_manager is not None:
                controller = None
                if type( menu_manager ) is tuple:
                    menu_manager, controller = menu_manager
                menu = menu_manager.create_menu(self._grid, controller)
                # if it has anything in it pop it up
                if menu.GetMenuItemCount() > 0:
                    # Popup the menu (if an action is selected it will be
                    # performed before before 'PopupMenu' returns).
                    x, y = evt.GetPosition()
                    self._grid.PopupMenuXY(menu, x - 10, y - 10 )

            self.cell_right_clicked = (row, col)

            evt.Skip()

        return

    def _on_label_right_click(self, evt):
        """ Called when a right click occurred on a label. """

        row, col = evt.GetRow(), evt.GetCol()

        # a row value of -1 means this click happened on a column.
        # vice versa, a col value of -1 means a row click.
        menu_manager = None
        if row == -1:
            menu_manager = self.model.get_column_context_menu(col)
        else:
            menu_manager = self.model.get_row_context_menu(row)

        if menu_manager is not None:
            # get the underlying menu object
            menu = menu_manager.create_menu(self._grid)
            # if it has anything in it pop it up
            if menu.GetMenuItemCount() > 0:
                # Popup the menu (if an action is selected it will be performed
                # before before 'PopupMenu' returns).
                self._grid.PopupMenu(menu, evt.GetPosition())
        elif col >= 0:
            cws = getattr( self, '_cached_widths', None )
            if (cws is not None) and (0 <= col < len( cws )):
                cws[ col ] = None
                self.__autosize()

        evt.Skip()

    def _on_label_left_click(self, evt):
        """ Called when a left click occurred on a label. """

        row, col = evt.GetRow(), evt.GetCol()

        # A row value of -1 means this click happened on a column.
        # vice versa, a col value of -1 means a row click.
        if (row == -1) and self.allow_column_sort and evt.ControlDown():
            self._column_sort( col )

        elif (col == -1) and self.allow_row_sort and evt.ControlDown():
            self._row_sort( row )

        evt.Skip()

    def _column_sort(self, col):
        """ Sorts the data on the specified column **col**.
        """
        self._grid.Freeze()

        if (col == self._current_sorted_col) and (not self._col_sort_reversed):
            # If this column is currently sorted on then reverse it:
            self.model.sort_by_column(col, True)
        elif (col == self._current_sorted_col) and self._col_sort_reversed:
            # If this column is currently reverse-sorted then unsort it:
            try:
                self.model.no_column_sort()
            except NotImplementedError:
                # If an unsort function is not implemented then just
                # reverse the sort:
                self.model.sort_by_column(col, False)
        else:
            # Sort the data:
            self.model.sort_by_column(col, False)

        self._grid.Thaw()

    def _row_sort(self, row):
        self._grid.Freeze()

        if (row == self._current_sorted_row) and (not self._row_sort_reversed):
            # If this row is currently sorted on then reverse it:
            self.model.sort_by_row(row, True)
        elif row == self._current_sorted_row and self._row_sort_reversed:
            # If this row is currently reverse-sorted then unsort it:
            try:
                self.model.no_row_sort()
            except NotImplementedError:
                # If an unsort function is not implemented then just
                # reverse the sort:
                self.model.sort_by_row(row, False)
        else:
            # Sort the data:
            self.model.sort_by_row(row, False)

        self._grid.Thaw()

    def _on_key_down(self, evt):
        """ Called when a key is pressed. """
        # This changes the behaviour of the <Enter> and <Tab> keys to make
        # manual data entry smoother!
        #
        # Don't change the behavior if the <Control> key is pressed as this
        # has meaning to the edit control.
        key_code = evt.GetKeyCode()

        if (key_code == wx.WXK_RETURN) and not evt.ControlDown():
            self._move_to_next_cell(evt.ShiftDown())

        elif (key_code == wx.WXK_TAB) and not evt.ControlDown():
            if evt.ShiftDown():
                # fixme: in a split window the shift tab is being eaten
                # by tabbing between the splits
                self._move_to_previous_cell()

            else:
                self._move_to_next_cell()

        elif key_code == ASCII_C:
            data = self.__get_drag_value()
            # deposit the data in our singleton clipboard
            enClipboard.data = data

            # build a wxCustomDataObject to notify the system clipboard
            # that some in-process data is available
            data_object = wx.CustomDataObject(PythonObject)
            data_object.SetData('dummy')
            if TheClipboard.Open():
                TheClipboard.SetData(data_object)
                TheClipboard.Close()

        evt.Skip()

    def _move_to_next_cell(self, expandSelection=False):
        """ Move to the 'next' cell. """

        # Complete the edit on the current cell.
        self._grid.DisableCellEditControl()

        # Try to move to the next column.
        success = self._grid.MoveCursorRight(expandSelection)

        # If the move failed then we must be at the end of a row.
        if not success:
            # Move to the first column in the next row.
            newRow = self._grid.GetGridCursorRow() + 1
            if newRow < self._grid.GetNumberRows():
                self._grid.SetGridCursor(newRow, 0)
                self._grid.MakeCellVisible(newRow, 0)

            else:
                # This would be a good place to add a new row if your app
                # needs to do that.
                pass

        return success

    def _move_to_previous_cell(self, expandSelection=False):
        """ Move to the 'previous' cell. """

        # Complete the edit on the current cell.
        self._grid.DisableCellEditControl()

        # Try to move to the previous column (without expanding the current
        # selection).
        success = self._grid.MoveCursorLeft(expandSelection)

        # If the move failed then we must be at the start of a row.
        if not success:
            # Move to the last column in the previous row.
            newRow = self._grid.GetGridCursorRow() - 1
            if newRow >= 0:
                self._grid.SetGridCursor(newRow,
                                           self._grid.GetNumberCols() - 1)
                self._grid.MakeCellVisible(newRow,
                                             self._grid.GetNumberCols() - 1)

    def _refresh(self):
        self._grid.GetParent().Layout()

    def _on_col_move(self, evt):
        """ Called when a column move is taking place.
        """
        self._ignore = True

        # Get the column being moved:
        frm = evt.GetMoveColumn()

        # Get the column to insert it before:
        to = evt.GetBeforeColumn()

        # Tell the model to update its columns:
        if self.model._move_column(frm, to):

            # Modify the grid:
            grid   = self._grid
            cols   = grid.GetNumberCols()
            widths = [ grid.GetColSize(i) for i in range( cols ) ]
            width  = widths[frm]
            del widths[frm]
            to -= (frm < to)
            widths.insert( to, width )

            grid.BeginBatch()

            grid.ProcessTableMessage( GridTableMessage( self._grid_table_base,
                GRIDTABLE_NOTIFY_COLS_DELETED, frm, 1 ) )

            grid.ProcessTableMessage( GridTableMessage( self._grid_table_base,
                GRIDTABLE_NOTIFY_COLS_INSERTED, to, 1 ) )

            [ grid.SetColSize(i, widths[i]) for i in range(min(frm, to), cols) ]

            grid.EndBatch()

    def _on_row_move(self, evt):
        """ Called when a row move is taking place.
        """
        self._ignore = True

        # Get the column being moved:
        frm = evt.GetMoveRow()

        # Get the column to insert it before:
        to = evt.GetBeforeRow()

        # Tell the model to update its rows:
        if self.model._move_row(frm, to):

            # Notify the grid:
            grid    = self._grid
            rows    = grid.GetNumberRows()
            heights = [ grid.GetRowSize(i) for i in range( rows ) ]
            height  = heights[frm]
            del heights[frm]
            to -= (frm < to)
            heights.insert( to, height )

            grid.BeginBatch()

            grid.ProcessTableMessage( GridTableMessage( self._grid_table_base,
                GRIDTABLE_NOTIFY_ROWS_DELETED, frm, 1 ) )

            grid.ProcessTableMessage( GridTableMessage( self._grid_table_base,
                GRIDTABLE_NOTIFY_ROWS_INSERTED, to, 1 ) )

            [ grid.SetRowSize(i, heights[i]) for i in range(min(frm, to), rows)]

            grid.EndBatch()

    ###########################################################################
    # PythonDropTarget interface.
    ###########################################################################
    def wx_dropped_on ( self, x, y, drag_object, drag_result ):

        # first resolve the x/y coords into a grid row/col
        row, col = self.__resolve_grid_coords(x, y)

        result = wx.DragNone
        if row != -1 and col != -1:
            # now ask the model if the target cell can accept this object
            valid_target = self.model.is_valid_cell_value(row, col,
                                                          drag_object)
            # if this is a valid target then attempt to set the value
            if valid_target:
                # find the data
                data = drag_object
                # sometimes a 'node' attribute on the clipboard gets set
                # to a binding. if this happens we want to use it, otherwise
                # we want to just use the drag_object passed to us
                if hasattr(enClipboard, 'node') and \
                   enClipboard.node is not None:
                    data = enClipboard.node

                # now make sure the value gets set in the model
                self.model.set_value(row, col, data)
                result = drag_result

        return result

    def wx_drag_over ( self, x, y, drag_object, drag_result ):

        # first resolve the x/y coords into a grid row/col
        row, col = self.__resolve_grid_coords(x, y)

        result = wx.DragNone
        if row != -1 and col != -1:
            # now ask the model if the target cell can accept this object
            valid_target = self.model.is_valid_cell_value(row, col,
                                                          drag_object)
            if valid_target:
                result = drag_result

        return result

    ###########################################################################
    # private interface.
    ###########################################################################

    def __initialize_fonts(self):
        """ Initialize the label fonts. """

        self._on_default_label_font_changed()
        self._on_default_cell_font_changed()
        self._on_default_cell_text_color_changed()
        self._on_grid_line_color_changed()

        self._grid.SetColLabelAlignment(wx.ALIGN_CENTRE, wx.ALIGN_CENTRE)
        self._grid.SetRowLabelAlignment(wx.ALIGN_RIGHT, wx.ALIGN_CENTRE)

    def __initialize_rows(self, model):
        """ Initialize the row headers. """

        # should we really be doing this?
        for row in range(model.get_row_count()):
            if model.is_row_read_only(row):
                attr = wx.grid.GridCellAttr()
                attr.SetReadOnly()
                #attr.SetRenderer(None)
                #attr.SetBackgroundColour('linen')
                self._grid.SetRowAttr(row, attr)

    def __initialize_columns(self, model):
        """ Initialize the column headers. """

        # should we really be doing this?
        for column in range(model.get_column_count()):
            if model.is_column_read_only(column):
                attr = wx.grid.GridCellAttr()
                attr.SetReadOnly()
                #attr.SetRenderer(None)
                #attr.SetBackgroundColour('linen')
                self._grid.SetColAttr(column, attr)

    def __initialize_counts(self, model):
        """ Initializes the row and column counts. """

        if model is not None:
            self._row_count = model.get_row_count()
        else:
            self._row_count = 0

        if model is not None:
            self._col_count = model.get_column_count()
        else:
            self._col_count = 0

    def __initialize_sort_state(self):
        """ Initializes the row and column counts. """

        self._current_sorted_col = None
        self._current_sorted_row = None
        self._col_sort_reversed  = False
        self._row_sort_reversed  = False

    def __initialize_style_settings(self, event=None):

        # make sure all the handlers for traits defining styles get called
        self._on_enable_lines_changed()
        self._on_read_only_changed()
        self._on_selection_mode_changed()
        self._on_column_label_height_changed()
        self._on_row_label_width_changed()
        self._on_show_column_headers_changed()
        self._on_show_row_headers_changed()
        self._on_default_cell_bg_color_changed()
        self._on_default_label_bg_color_changed()
        self._on_default_label_text_color_changed()
        self._on_selection_bg_color_changed()
        self._on_selection_text_color_changed()

    def __get_drag_value(self):
        """ Calculates the drag value based on the current selection. """
        # fixme: The following line seems like a more useful implementation than
        # the previous commented out version below, but I am leaving the old
        # version in the code for now just in case. If anyone sees this comment
        # after 1/1/2009, it should be safe to delete this comment and the
        # commented out code below...
        return self.model.get_cell_drag_value(self._grid.GetGridCursorRow(),
                                              self._grid.GetGridCursorCol())

        ###rows, cols = self.__get_selected_rows_and_cols()
        ###
        ###if len(rows) > 0:
        ###    rows.sort()
        ###    value = self.model.get_rows_drag_value(rows)
        ###    if len(rows) == 1 and len(value) == 1:
        ###        value = value[0]
        ###elif len(cols) > 0:
        ###    cols.sort()
        ###    value = self.model.get_cols_drag_value(cols)
        ###    if len(cols) == 1 and len(value) == 1:
        ###        value = value[0]
        ###else:
        ###    # our final option -- grab the cell that the cursor is currently in
        ###    row = self._grid.GetGridCursorRow()
        ###    col = self._grid.GetGridCursorCol()
        ###    value = self.model.get_cell_drag_value(row, col)
        ###
        ###return value

    def __get_selection(self):
        """ Returns a list of values for the current selection. """

        rows, cols = self.__get_selected_rows_and_cols()

        if len(rows) > 0:
            rows.sort()
            value = self.model.get_rows_selection_value(rows)
        elif len(cols) > 0:
            cols.sort()
            value = self.model.get_cols_selection_value(cols)
        else:
            # our final option -- grab the cell that the cursor is currently in
            row = self._grid.GetGridCursorRow()
            col = self._grid.GetGridCursorCol()
            value = self.model.get_cell_selection_value(row, col)
            if value is not None:
                value = [value]

        if value is None:
            value = []

        return value

    def __get_selected_rows_and_cols(self):
        """ Return lists of the selected rows and the selected columns. """

        # note: because the wx grid control is so screwy, we have limited
        # the selection behavior. we only allow single cells to be selected,
        # or whole row, or whole columns.

        rows = self._grid.GetSelectedRows()
        cols = self._grid.GetSelectedCols()

        # because wx is retarded we have to check this as well -- why
        # the blazes can't they come up with one Q#$%@$#% API to manage
        # selections??? makes me want to put the smack on somebody.
        # note that all this malarkey is working on the assumption that
        # only entire rows or entire columns or single cells are selected.
        top_left = self._grid.GetSelectionBlockTopLeft()
        bottom_right = self._grid.GetSelectionBlockBottomRight()
        selection_mode = self._grid.GetSelectionMode()

        if selection_mode == wxGrid.wxGridSelectRows:
            # handle rows differently. figure out which rows were
            # selected. turns out that in this case, wx adds a "block"
            # per row, so we have to cycle over the list returned by
            # the GetSelectionBlock routines
            for i in range(len(top_left)):
                top_point = top_left[i]
                bottom_point = bottom_right[i]
                for row_index in range(top_point[0], bottom_point[0] + 1):
                    rows.append(row_index)
        elif selection_mode == wxGrid.wxGridSelectColumns:
            # again, in this case we know that only whole columns can be
            # selected
            for i in range(len(top_left)):
                top_point = top_left[i]
                bottom_point = bottom_right[i]
                for col_index in range(top_point[1], bottom_point[1] + 1):
                    cols.append(col_index)
        elif selection_mode == wxGrid.wxGridSelectCells:
            # this is the case where the selection_mode is cell, which also
            # allows complete columns or complete rows to be selected.

            # first find the size of the grid
            row_size = self.model.get_row_count()
            col_size = self.model.get_column_count()

            for i in range(len(top_left)):
                top_point = top_left[i]
                bottom_point = bottom_right[i]
                # precalculate whether this is a row or column select
                row_select = top_point[1] == 0 and \
                             bottom_point[1] == col_size - 1
                col_select = top_point[0] == 0 and \
                             bottom_point[0] == row_size - 1

                if row_select:
                    for row_index in range(top_point[0], bottom_point[0] + 1):
                        rows.append(row_index)
                if col_select:
                    for col_index in range(top_point[1], bottom_point[1] + 1):
                        cols.append(top_point[0])

        return ( rows, cols )


    def __fire_selection_changed(self):
        self.selection_changed = True

    def __autosize(self):
        """ Autosize the grid with appropriate flags. """

        model = self.model
        grid  = self._grid
        if grid is not None and self.autosize:
            grid.AutoSizeColumns(False)
            grid.AutoSizeRows(False)

        # Whenever we size the grid we need to take in to account any
        # explicitly set column sizes:

        grid.BeginBatch()

        dx, dy  = grid.GetClientSize()
        n       = model.get_column_count()
        pdx     = 0
        wdx     = 0.0
        widths  = []
        cached  = getattr( self, '_cached_widths', None )
        current = [ grid.GetColSize( i ) for i in xrange( n ) ]
        if (cached is None) or (len( cached ) != n):
            self._cached_widths = cached = [ None ] * n

        for i in xrange( n ):
            cw = cached[i]
            if ((cw is None) or (-cw == current[i]) or
                # hack: For some reason wx always seems to adjust column 0 by
                # 1 pixel from what we set it to (at least on Windows), so we
                # need to add a little fudge factor just for this column:
                ((i == 0) and (abs( current[i] + cw ) <= 1))):
                width = model.get_column_size( i )
                if width <= 0.0:
                    width = 0.1
                if width <= 1.0:
                    wdx += width
                    cached[i] = -1
                else:
                    width = int( width )
                    pdx  += width
                    if cw is None:
                        cached[i] = width
            else:
                cached[i] = width = current[i]
                pdx += width

            widths.append( width )

        # The '-1' below adjusts for an off by 1 error in the way the wx.Grid
        # control determines whether or not it needs a horizontal scroll bar:
        adx = max( 0, dx - pdx - 1 )

        for i in range( n ):
            width = cached[i]
            if width < 0:
                width = widths[i]
                if width <= 1.0:
                    w         = max( 30, int( round( (adx * width) / wdx ) ) )
                    wdx      -= width
                    width     = w
                    adx      -= width
                    cached[i] = -w

            grid.SetColSize( i, width )

        grid.AdjustScrollbars()
        grid.EndBatch()
        grid.ForceRefresh()

    def __resolve_grid_coords(self, x, y):
        """ Resolve the specified x and y coordinates into row/col
            coordinates. Returns row, col. """

        # the x,y coordinates here are Unscrolled coordinates.
        # They must be changed to scrolled coordinates.
        x, y = self._grid.CalcUnscrolledPosition(x, y)

        # now we need to get the row and column from the grid
        # but we need to first remove the RowLabel and ColumnLabel
        # bounding boxes
        if self.show_row_headers:
            x = x - self._grid.GetGridRowLabelWindow().GetRect().width

        if self.show_column_headers:
            y = y - self._grid.GetGridColLabelWindow().GetRect().height

        return ( self._grid.YToRow(y), self._grid.XToCol(x) )

    def _select_rows(self, cells):
        """ Selects all of the rows specified by a list of (row,column) pairs.
        """
        # For a large set of rows, simply calling 'SelectBlock' on the Grid
        # object for each row is very inefficient, so we first make a pass over
        # all of the cells to merge them into contiguous ranges as much as
        # possible:
        sb = self._grid.SelectBlock

        # Extract the rows and sort them:
        rows = [ row for row, column in cells ]
        rows.sort()

        # Now find contiguous ranges of rows, and select the current range
        # whenever a break in the sequence is found:
        first = last = -999
        for row in rows:
            if row == (last + 1):
                last = row
            else:
                if first >= 0:
                    sb(first, 0, last, 0, True)
                first = last = row

        # Handle the last pending range of lines to be selected:
        if first >= 0:
            sb(first, 0, last, 0, True)

class _GridTableBase(PyGridTableBase):
    """ A private adapter for the underlying wx grid implementation. """

    ###########################################################################
    # 'object' interface.
    ###########################################################################

    def __init__(self, model, grid):
        """ Creates a new table base. """

        # Base class constructor.
        PyGridTableBase.__init__(self)

        # The Pyface model that provides the data.
        self.model = model
        self._grid = grid

        # hacky state variables so we can identify when rows have been
        # added or deleted.
        self._row_count = -1
        self._col_count = -1

        # caches for editors and renderers
        self._editor_cache   = {}
        self._renderer_cache = {}

    def dispose(self):

        # Make sure dispose gets called on all traits editors:
        for editor in self._editor_cache.values():
            editor.dispose()
        self._editor_cache = {}

        for renderer in self._renderer_cache.values():
            renderer.dispose()
        self._renderer_cache = {}

    ###########################################################################
    # 'wxPyGridTableBase' interface.
    ###########################################################################

    def GetNumberRows(self):
        """ Return the number of rows in the model. """

        # because wx is such a wack job we have to store away the row
        # and column counts so we can figure out when rows or cols have
        # been appended or deleted. lacking a better place to do this
        # we just set the local variable every time GetNumberRows is called.
        self._row_count = self.model.get_row_count()
        return self._row_count

    def GetNumberCols(self):
        """ Return the number of columns in the model. """

        # see comment in GetNumberRows for logic here
        self._col_count = self.model.get_column_count()
        return self._col_count

    def IsEmptyCell(self, row, col):
        """ Is the specified cell empty? """

        return self.model.is_cell_empty(row, col)

    def GetValue(self, row, col):
        """ Get the value at the specified row and column. """

        return self.model.get_value(row, col)

    def SetValue(self, row, col, value):
        """ Set the value at the specified row and column. """
        return self.model.set_value(row, col, value)

    def GetRowLabelValue(self, row):
        """ Called when the grid needs to display a row label. """

        label = self.model.get_row_name(row)

        if row == self._grid._current_sorted_row:
            if self._grid._row_sort_reversed:
                if is_win32:
                    ulabel = unicode(label, 'ascii') + u'  \u00ab'
                    label  = ulabel.encode('latin-1')
                else:
                    label += '  <<'
            elif is_win32:
                ulabel = unicode(label, 'ascii') + u'  \u00bb'
                label  = ulabel.encode('latin-1')
            else:
                label += '  >>'

        return label

    def GetColLabelValue(self, col):
        """ Called when the grid needs to display a column label. """

        label = self.model.get_column_name(col)

        if col == self._grid._current_sorted_col:
            if self._grid._col_sort_reversed:
                if is_win32:
                    ulabel = unicode(label, 'ascii') + u'  \u00ab'
                    label  = ulabel.encode('latin-1')
                else:
                    label += '  <<'
            elif is_win32:
                ulabel = unicode(label, 'ascii') + u'  \u00bb'
                label  = ulabel.encode('latin-1')
            else:
                label += '  >>'

        return label

    def GetTypeName(self, row, col):
        """ Called to determine the kind of editor/renderer to use.

        This doesn't necessarily have to be the same type used natively by the
        editor/renderer if they know how to convert.

        """
        typename = None
        try:
            typename = self.model.get_type(row, col)
        except NotImplementedError:
            pass

        if typename == None:
            typename = GRID_VALUE_STRING

        return typename

    def DeleteRows(self, pos, num_rows):
        """ Called when the view is deleting rows. """

        # clear the cache
        self._clear_cache()
        return self.model.delete_rows(pos, num_rows)

    def InsertRows(self, pos, num_rows):
        """ Called when the view is inserting rows. """
        # clear the cache
        self._clear_cache()
        return self.model.insert_rows(pos, num_rows)

    def AppendRows(self, num_rows):
        """ Called when the view is inserting rows. """
        # clear the cache
        self._clear_cache()
        pos = self.model.get_row_count()
        return self.model.insert_rows(pos, num_rows)

    def DeleteCols(self, pos, num_cols):
        """ Called when the view is deleting columns. """

        # clear the cache
        self._clear_cache()
        return self.model.delete_columns(pos, num_cols)

    def InsertCols(self, pos, num_cols):
        """ Called when the view is inserting columns. """
        # clear the cache
        self._clear_cache()
        return self.model.insert_columns(pos, num_cols)

    def AppendCols(self, num_cols):
        """ Called when the view is inserting columns. """
        # clear the cache
        self._clear_cache()
        pos = self.model.get_column_count()
        return self.model.insert_columns(pos, num_cols)

    def GetAttr(self, row, col, kind):
        """ Retrieve the cell attribute object for the specified cell. """

        result = GridCellAttr()
        # we only handle cell requests, for other delegate to the supa
        if kind != GridCellAttr.Cell and kind != GridCellAttr.Any:
            return result

        rows = self.model.get_row_count()
        cols = self.model.get_column_count()

        # First look in the cache for the editor:
        editor = self._editor_cache.get((row, col))
        if editor is None:
            if (row >= rows) or (col >= cols):
                editor = DummyGridCellEditor()
            else:
                # Ask the underlying model for an editor for this cell:
                editor = self.model.get_cell_editor(row, col)
                if editor is not None:
                    self._editor_cache[(row, col)] = editor
                    editor._grid_info = (self._grid._grid, row, col)

        if editor is not None:
            # Note: We have to increment the reference to keep the
            #       underlying code from destroying our object.
            editor.IncRef()
            result.SetEditor(editor)

        # try to find a renderer for this cell
        renderer = None
        if row < rows and col < cols:
            renderer = self.model.get_cell_renderer(row, col)

        if renderer is not None and renderer.renderer is not None:
            renderer.renderer.IncRef()
            result.SetRenderer(renderer.renderer)

        # look to see if this cell is editable
        read_only = False
        if row < rows and col < cols:
            read_only = self.model.is_cell_read_only(row, col) or \
                        self.model.is_row_read_only(row) or \
                        self.model.is_column_read_only(col)

        result.SetReadOnly(read_only)
        read_only_color = self._grid.default_cell_read_only_color
        if read_only and read_only_color is not None:
            result.SetBackgroundColour(read_only_color)

        # check to see if colors or fonts are specified for this cell
        bgcolor = None
        if row < rows and col < cols:
            bgcolor = self.model.get_cell_bg_color(row, col)
        else:
            bgcolor = self._grid.default_cell_bg_color

        if bgcolor is not None:
            result.SetBackgroundColour(bgcolor)

        text_color = None
        if row < rows and col < cols:
            text_color = self.model.get_cell_text_color(row, col)
        else:
            text_color = self._grid.default_cell_text_color
        if text_color is not None:
            result.SetTextColour(text_color)

        cell_font = None
        if row < rows and col < cols:
            cell_font = self.model.get_cell_font(row, col)
        else:
            cell_font = self._grid.default_cell_font
        if cell_font is not None:
            result.SetFont(cell_font)

        # check for alignment definition for this cell
        halignment = valignment = None
        if row < rows and col < cols:
            halignment = self.model.get_cell_halignment(row, col)
            valignment = self.model.get_cell_valignment(row, col)
        if halignment is not None and valignment is not None:
            if halignment == 'center':
                h = wx.ALIGN_CENTRE
            elif halignment == 'right':
                h = wx.ALIGN_RIGHT
            else:
                h = wx.ALIGN_LEFT

            if valignment == 'top':
                v = wx.ALIGN_TOP
            elif valignment == 'bottom':
                v = wx.ALIGN_BOTTOM
            else:
                v = wx.ALIGN_CENTRE

            result.SetAlignment(h, v)

        return result

    ###########################################################################
    # private interface.
    ###########################################################################
    def _clear_cache(self):
        """ Clean out the editor/renderer cache. """

        # Dispose of the editors in the cache after a brief delay, so as
        # to allow completion of the current event:
        do_later( self._editor_dispose, self._editor_cache.values() )

        self._editor_cache   = {}
        self._renderer_cache = {}
        return

    def _editor_dispose(self, editors):
        for editor in editors:
            editor.dispose()

from wx.grid import PyGridCellEditor
class DummyGridCellEditor(PyGridCellEditor):

    def Show(self, show, attr):
        return

#### EOF ######################################################################
