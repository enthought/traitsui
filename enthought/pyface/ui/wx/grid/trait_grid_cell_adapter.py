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
""" Adapter class to make trait editor controls work inside of a grid. """

# Major package imports
import wx
from wx.grid import PyGridCellEditor
from wx import SIZE_ALLOW_MINUS_ONE

# Enthought library imports
from enthought.traits.ui.api import UI, default_handler

# Local imports:
from combobox_focus_handler import ComboboxFocusHandler

wx_28 = (float( wx.__version__[:3] ) >= 2.8)

def get_control(control):
    if isinstance(control, wx.Control):
        return control

    for control in control.GetChildren():
        result = get_control(control)
        if result is not None:
            return result

    return None

def push_control(control, grid):
    control.PushEventHandler(ComboboxFocusHandler(grid))
    for child_control in control.GetChildren():
        push_control(child_control, grid)

class TraitGridCellAdapter(PyGridCellEditor):
    """ Wrap a trait editor as a GridCellEditor object. """

    def __init__(self, trait_editor_factory, obj, name, description,
                 handler = None, context = None, style = 'simple',
                 width = -1.0, height = -1.0):
        """ Build a new TraitGridCellAdapter object. """

        PyGridCellEditor.__init__(self)
        self._factory     = trait_editor_factory
        self._style       = style
        self._width       = width
        self._height      = height
        self._editor      = None
        self._obj         = obj
        self._name        = name
        self._description = description
        self._handler     = handler
        self._context     = context

    def Create(self, parent, id, evtHandler):
        """ Called to create the control, which must derive from wxControl. """
        # If the editor has already been created, ignore the request:
        if hasattr( self, '_control' ):
            return

        handler = self._handler
        if handler is None:
            handler = default_handler()

        if self._context is None:
            ui = UI(handler = handler)
        else:
            context = self._context.copy()
            context['table_editor_object'] = context['object']
            context['object'] = self._obj
            ui = UI(handler = handler, context = context)

        # Link the editor's undo history in to the main ui undo history if the
        # UI object is available:
        factory = self._factory
        if factory._ui is not None:
            ui.history = factory._ui.history

        # make sure the factory knows this is a grid_cell editor
        factory.is_grid_cell = True
        factory_method = getattr(factory, self._style + '_editor')
        self._editor   = factory_method(ui,
                                        self._obj,
                                        self._name,
                                        self._description,
                                        parent)

        # Tell the editor to actually build the editing widget:
        self._editor.prepare(parent)

        # Find the control to use as the editor:
        self._control = control = self._editor.control

        # Calculate and save the required editor height:
        grid, row, col = getattr(self, '_grid_info', (None, None, None))
        width, height  = control.GetBestSize()

        self_height    = self._height
        if self_height > 1.0:
            height = int( self_height )
        elif (self_height >= 0.0) and (grid is not None):
            height = int( self_height * grid.GetSize()[1] )

        self_width = self._width
        if self_width > 1.0:
            width = int( self_width )
        elif (self_width >= 0.0) and (grid is not None):
            width = int( self_width * grid.GetSize()[0] )

        self._edit_width, self._edit_height = width, height

        # Set up the event handler for each window in the cell editor:
        push_control(control, grid)

        # Set up the first control found within the cell editor as the cell
        # editor control:
        control = get_control(control)
        if control is not None:
            self.SetControl(control)

    def SetSize(self, rect):
        """ Called to position/size the edit control within the cell rectangle.
            If you don't fill the cell (the rect) then be sure to override
            PaintBackground and do something meaningful there.
        """
        changed = False
        edit_width, edit_height = rect.width, rect.height
        grid, row, col = getattr(self, '_grid_info', (None, None, None))
        if (grid is not None) and self._editor.scrollable:
            edit_width, cur_width = self._edit_width, grid.GetColSize(col)

            restore_width = getattr( grid, '_restore_width', None )
            if restore_width is not None:
                cur_width = restore_width

            if (edit_width > cur_width) or (restore_width is not None):
                edit_width = max( edit_width, cur_width )
                grid._restore_width = cur_width
                grid.SetColSize(col, edit_width + 1 + (col == 0))
                changed = True
            else:
                edit_width = cur_width

            edit_height, cur_height = self._edit_height, grid.GetRowSize(row)

            restore_height = getattr( grid, '_restore_height', None )
            if restore_height is not None:
                cur_height = restore_height

            if (edit_height > cur_height) or (restore_height is not None):
                edit_height = max( edit_height, cur_height )
                grid._restore_height = cur_height
                grid.SetRowSize(row, edit_height + 1 + (row == 0))
                changed = True
            else:
                edit_height = cur_height

            if changed:
                grid.ForceRefresh()

        self._control.SetDimensions(rect.x + 1, rect.y + 1,
                                    edit_width, edit_height,
                                    SIZE_ALLOW_MINUS_ONE)

        if changed:
            grid.MakeCellVisible(grid.GetGridCursorRow(),
                                 grid.GetGridCursorCol())

    def Show(self, show, attr):
        """ Show or hide the edit control.  You can use the attr (if not None)
            to set colours or fonts for the control.
        """
        if self.IsCreated():
            if wx_28:
                super(TraitGridCellAdapter, self).Show(show, attr)
            else:
                self.base_Show(show, attr)

        return

    def PaintBackground(self, rect, attr):
        """ Draws the part of the cell not occupied by the edit control.  The
            base  class version just fills it with background colour from the
            attribute.  In this class the edit control fills the whole cell so
            don't do anything at all in order to reduce flicker.
        """
        return

    def BeginEdit(self, row, col, grid):
        """ Make sure the control is ready to edit. """
        # We have to manually set the focus to the control
        self._editor.update_editor()
        control = self._control
        control.Show(True)
        control.SetFocus()
        if isinstance(control, wx.TextCtrl):
            control.SetSelection(-1, -1)

    def EndEdit(self, row, col, grid):
        """ Do anything necessary to complete the editing. """
        self._control.Show(False)

        changed        = False
        grid, row, col = self._grid_info

        if grid._no_reset_col:
            grid._no_reset_col = False
        else:
            width = getattr(grid, '_restore_width', None)
            if width is not None:
                del grid._restore_width
                grid.SetColSize(col, width)
                changed = True

        if grid._no_reset_row:
            grid._no_reset_row = False
        else:
            height = getattr(grid, '_restore_height', None)
            if height is not None:
                del grid._restore_height
                grid.SetRowSize(row, height)
                changed = True

        if changed:
            grid.ForceRefresh()

    def Reset(self):
        """ Reset the value in the control back to its starting value. """

        # fixme: should we be using the undo history here?
        return

    def StartingKey(self, evt):
        """ If the editor is enabled by pressing keys on the grid, this will be
            called to let the editor do something about that first key
            if desired.
        """
        return

    def StartingClick(self):
        """ If the editor is enabled by clicking on the cell, this method
            will be called to allow the editor to simulate the click on the
            control if needed.
        """
        return

    def Destroy(self):
        """ Final cleanup. """
        self._editor.dispose()
        return

    def Clone(self):
        """ Create a new object which is the copy of this one. """
        return TraitGridCellAdapter(self._factory, self._obj, self._name,
                                    self._description, style=self._style)

    def dispose(self):
        if self._editor is not None:
            self._editor.dispose()

        self.DecRef()

#### EOF ######################################################################

