#-------------------------------------------------------------------------
#
#  Copyright (c) 2007, Enthought, Inc.
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
#  Date:   05/20/2007
#
#-------------------------------------------------------------------------

""" A traits UI editor for editing tabular data (arrays, list of tuples, lists
    of objects, etc).
"""

#-------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------

from __future__ import absolute_import
import wx
import wx.lib.mixins.listctrl as listmix

from traits.api \
    import HasStrictTraits, Int, \
    List, Bool, Instance, Any, Event, \
    Property, TraitListEvent

# FIXME: TabularEditor (the editor factory for tabular editors) is a proxy class
# defined here just for backward compatibility. The class has been moved to the
# traitsui.editors.tabular_editor file.
from traitsui.editors.tabular_editor \
    import TabularEditor

from traitsui.ui_traits \
    import Image

from traitsui.tabular_adapter \
    import TabularAdapter

from traitsui.wx.editor \
    import Editor

from pyface.image_resource \
    import ImageResource

from pyface.timer.api \
    import do_later

from .constants \
    import is_mac, scrollbar_dx
import six
from six.moves import range

try:
    from pyface.wx.drag_and_drop \
        import PythonDropSource, PythonDropTarget
except:
    PythonDropSource = PythonDropTarget = None

#-------------------------------------------------------------------------
#  Constants:
#-------------------------------------------------------------------------

# Mapping for trait alignment values to wx alignment values:
alignment_map = {
    'left': wx.LIST_FORMAT_LEFT,
    'center': wx.LIST_FORMAT_CENTRE,
    'right': wx.LIST_FORMAT_RIGHT
}


class TextEditMixin(listmix.TextEditMixin):

    def __init__(self, edit_labels):
        """ edit_labels controls whether the first column is editable
        """
        self.edit_labels = edit_labels
        listmix.TextEditMixin.__init__(self)

    def OpenEditor(self, col, row):
        if col == 0 and not self.edit_labels:
            return
        else:
            return listmix.TextEditMixin.OpenEditor(self, col, row)

#-------------------------------------------------------------------------
#  'wxListCtrl' class:
#-------------------------------------------------------------------------


class wxListCtrl(wx.ListCtrl, TextEditMixin):
    """ Subclass of wx.ListCtrl to provide correct virtual list behavior.
    """

    def __init__(self, parent, ID, pos=wx.DefaultPosition, size=wx.DefaultSize,
                 style=0, can_edit=False, edit_labels=False):

        wx.ListCtrl.__init__(self, parent, ID, pos, size, style)

        # if the selected is editable, then we have to init the mixin
        if can_edit:
            TextEditMixin.__init__(self, edit_labels)

    def SetVirtualData(self, row, col, text):
        # this method is called but the job is already done by
        # the _end_label_edit method. Commmented code is availabed
        # if needed
        pass
        #edit = self._editor
        #return editor.adapter.set_text( editor.object, editor.name,
        #                                row, col, text )

    def OnGetItemAttr(self, row):
        """ Returns the display attributes to use for the specified list item.
        """
        # fixme: There appears to be a bug in wx in that they do not correctly
        # manage the reference count for the returned object, and it seems to be
        # gc'ed before they finish using it. So we store an object reference to
        # it to prevent it from going away too soon...
        self._attr = attr = wx.ListItemAttr()
        editor = self._editor
        object, name = editor.object, editor.name

        color = editor.adapter.get_bg_color(object, name, row)
        if color is not None:
            attr.SetBackgroundColour(color)

        color = editor.adapter.get_text_color(object, name, row)
        if color is not None:
            attr.SetTextColour(color)

        font = editor.adapter.get_font(object, name, row)
        if font is not None:
            attr.SetFont(font)

        return attr

    def OnGetItemImage(self, row):
        """ Returns the image index to use for the specified list item.
        """
        editor = self._editor
        image = editor._get_image(
            editor.adapter.get_image(
                editor.object, editor.name, row, 0))
        if image is not None:
            return image

        return -1

    def OnGetItemColumnImage(self, row, column):
        """ Returns the image index to use for the specified list item.
        """
        editor = self._editor
        image = editor._get_image(
            editor.adapter.get_image(
                editor.object, editor.name, row, column))
        if image is not None:
            return image

        return -1

    def OnGetItemText(self, row, column):
        """ Returns the text to use for the specified list item.
        """
        editor = self._editor
        return editor.adapter.get_text(editor.object, editor.name,
                                       row, column)

#-------------------------------------------------------------------------
#  'TabularEditor' class:
#-------------------------------------------------------------------------


class TabularEditor(Editor):
    """ A traits UI editor for editing tabular data (arrays, list of tuples,
        lists of objects, etc).
    """

    #-- Trait Definitions ----------------------------------------------------

    # The event fired when a table update is needed:
    update = Event

    # The event fired when a simple repaint is needed:
    refresh = Event

    # The current set of selected items (which one is used depends upon the
    # initial state of the editor factory 'multi_select' trait):
    selected = Any
    multi_selected = List

    # The current set of selected item indices (which one is used depends upon
    # the initial state of the editor factory 'multi_select' trait):
    selected_row = Int(-1)
    multi_selected_rows = List(Int)

    # The most recently actived item and its index:
    activated = Any
    activated_row = Int

    # The most recent left click data:
    clicked = Instance('TabularEditorEvent')

    # The most recent left double click data:
    dclicked = Instance('TabularEditorEvent')

    # The most recent right click data:
    right_clicked = Instance('TabularEditorEvent')

    # The most recent right double click data:
    right_dclicked = Instance('TabularEditorEvent')

    # The most recent column click data:
    column_clicked = Instance('TabularEditorEvent')

    # Is the tabular editor scrollable? This value overrides the default.
    scrollable = True

    # Row index of item to select after rebuilding editor list:
    row = Any

    # Should the selected item be edited after rebuilding the editor list:
    edit = Bool(False)

    # The adapter from trait values to editor values:
    adapter = Instance(TabularAdapter)

    # Dictionary mapping image names to wx.ImageList indices:
    images = Any({})

    # Dictionary mapping ImageResource objects to wx.ImageList indices:
    image_resources = Any({})

    # An image being converted:
    image = Image

    # Flag for marking whether the update was within the visible area
    _update_visible = Bool(False)

    #-------------------------------------------------------------------------
    #  Finishes initializing the editor by creating the underlying toolkit
    #  widget:
    #-------------------------------------------------------------------------

    def init(self, parent):
        """ Finishes initializing the editor by creating the underlying toolkit
            widget.
        """
        factory = self.factory

        # Set up the adapter to use:
        self.adapter = factory.adapter

        # Determine the style to use for the list control:
        style = wx.LC_REPORT | wx.LC_VIRTUAL | wx.BORDER_NONE

        if factory.editable_labels:
            style |= wx.LC_EDIT_LABELS

        if factory.horizontal_lines:
            style |= wx.LC_HRULES

        if factory.vertical_lines:
            style |= wx.LC_VRULES

        if not factory.multi_select:
            style |= wx.LC_SINGLE_SEL

        if not factory.show_titles:
            style |= wx.LC_NO_HEADER

        # Create the list control and link it back to us:
        self.control = control = wxListCtrl(parent, -1, style=style,
                                            can_edit=factory.editable,
                                            edit_labels=factory.editable_labels)
        control._editor = self

        # Create the list control column:
        #fixme: what do we do here?
        #control.InsertColumn( 0, '' )

        # Set up the list control's event handlers:
        id = control.GetId()
        wx.EVT_LIST_BEGIN_DRAG(parent, id, self._begin_drag)
        wx.EVT_LIST_BEGIN_LABEL_EDIT(parent, id, self._begin_label_edit)
        wx.EVT_LIST_END_LABEL_EDIT(parent, id, self._end_label_edit)
        wx.EVT_LIST_ITEM_SELECTED(parent, id, self._item_selected)
        wx.EVT_LIST_ITEM_DESELECTED(parent, id, self._item_selected)
        wx.EVT_LIST_KEY_DOWN(parent, id, self._key_down)
        wx.EVT_LIST_ITEM_ACTIVATED(parent, id, self._item_activated)
        wx.EVT_LIST_COL_END_DRAG(parent, id, self._size_modified)
        wx.EVT_LIST_COL_RIGHT_CLICK(parent, id, self._column_right_clicked)
        wx.EVT_LIST_COL_CLICK(parent, id, self._column_clicked)
        wx.EVT_LEFT_DOWN(control, self._left_down)
        wx.EVT_LEFT_DCLICK(control, self._left_dclick)
        wx.EVT_RIGHT_DOWN(control, self._right_down)
        wx.EVT_RIGHT_DCLICK(control, self._right_dclick)
        wx.EVT_MOTION(control, self._motion)
        wx.EVT_SIZE(control, self._size_modified)

        # Set up the drag and drop target:
        if PythonDropTarget is not None:
            control.SetDropTarget(PythonDropTarget(self))

        # Set up the selection listener (if necessary):
        if factory.multi_select:
            self.sync_value(factory.selected, 'multi_selected', 'both',
                            is_list=True)
            self.sync_value(factory.selected_row, 'multi_selected_rows',
                            'both', is_list=True)
        else:
            self.sync_value(factory.selected, 'selected', 'both')
            self.sync_value(factory.selected_row, 'selected_row', 'both')

        # Synchronize other interesting traits as necessary:
        self.sync_value(factory.update, 'update', 'from', is_event=True)
        self.sync_value(factory.refresh, 'refresh', 'from', is_event=True)

        self.sync_value(factory.activated, 'activated', 'to')
        self.sync_value(factory.activated_row, 'activated_row', 'to')

        self.sync_value(factory.clicked, 'clicked', 'to')
        self.sync_value(factory.dclicked, 'dclicked', 'to')

        self.sync_value(factory.right_clicked, 'right_clicked', 'to')
        self.sync_value(factory.right_dclicked, 'right_dclicked', 'to')

        self.sync_value(factory.column_clicked, 'column_clicked', 'to')

        # Make sure we listen for 'items' changes as well as complete list
        # replacements:
        try:
            self.context_object.on_trait_change(
                self.update_editor, self.extended_name + '_items', dispatch='ui')
        except:
            pass

        # If the user has requested automatic update, attempt to set up the
        # appropriate listeners:
        if factory.auto_update:
            self.context_object.on_trait_change(
                self.refresh_editor, self.extended_name + '.-', dispatch='ui')

        # Create the mapping from user supplied images to wx.ImageList indices:
        for image_resource in factory.images:
            self._add_image(image_resource)

        # Refresh the editor whenever the adapter changes:
        self.on_trait_change(self._refresh, 'adapter.+update',
                             dispatch='ui')

        # Rebuild the editor columns and headers whenever the adapter's
        # 'columns' changes:
        self.on_trait_change(self._rebuild_all, 'adapter.columns',
                             dispatch='ui')

        # Make sure the tabular view gets initialized:
        self._rebuild()

        # Set the list control's tooltip:
        self.set_tooltip()

    def dispose(self):
        """ Disposes of the contents of an editor.
        """
        # Remove all of the wx event handlers:
        control = self.control
        parent = control.GetParent()
        id = control.GetId()
        wx.EVT_LIST_BEGIN_DRAG(parent, id, None)
        wx.EVT_LIST_BEGIN_LABEL_EDIT(parent, id, None)
        wx.EVT_LIST_END_LABEL_EDIT(parent, id, None)
        wx.EVT_LIST_ITEM_SELECTED(parent, id, None)
        wx.EVT_LIST_ITEM_DESELECTED(parent, id, None)
        wx.EVT_LIST_KEY_DOWN(parent, id, None)
        wx.EVT_LIST_ITEM_ACTIVATED(parent, id, None)
        wx.EVT_LIST_COL_END_DRAG(parent, id, None)
        wx.EVT_LIST_COL_RIGHT_CLICK(parent, id, None)
        wx.EVT_LIST_COL_CLICK(parent, id, None)
        wx.EVT_LEFT_DOWN(control, None)
        wx.EVT_LEFT_DCLICK(control, None)
        wx.EVT_RIGHT_DOWN(control, None)
        wx.EVT_RIGHT_DCLICK(control, None)
        wx.EVT_MOTION(control, None)
        wx.EVT_SIZE(control, None)

        self.context_object.on_trait_change(
            self.update_editor,
            self.extended_name + '_items',
            remove=True)

        if self.factory.auto_update:
            self.context_object.on_trait_change(
                self.refresh_editor, self.extended_name + '.-', remove=True)

        self.on_trait_change(self._refresh, 'adapter.+update', remove=True)
        self.on_trait_change(self._rebuild_all, 'adapter.columns',
                             remove=True)

        super(TabularEditor, self).dispose()

    def _update_changed(self, event):
        """ Handles the 'update' event being fired.
        """
        if event is True:
            self.update_editor()
        elif isinstance(event, int):
            self._refresh_row(event)
        else:
            self._refresh_editor(event)

    def refresh_editor(self, item, name, old, new):
        """ Handles a table item attribute being changed.
        """
        self._refresh_editor(item)

    def _refresh_editor(self, item):
        """ Handles a table item being changed.
        """
        adapter = self.adapter
        object, name = self.object, self.name
        agi = adapter.get_item
        for row in range(adapter.len(object, name)):
            if item is agi(object, name, row):
                self._refresh_row(row)
                return

        self.update_editor()

    def _refresh_row(self, row):
        """ Updates the editor control when a specified table row changes.
        """
        self.control.RefreshRect(
            self.control.GetItemRect(row, wx.LIST_RECT_BOUNDS))

    def _update_editor(self, object, name, old_value, new_value):
        """ Performs updates when the object trait changes.
            Overloads traitsui.editor.UIEditor
        """
        self._update_visible = True

        super(TabularEditor, self)._update_editor(object, name,
                                                  old_value, new_value)

    def update_editor(self):
        """ Updates the editor when the object trait changes externally to the
            editor.
        """
        control = self.control
        n = self.adapter.len(self.object, self.name)
        top = control.GetTopItem()
        pn = control.GetCountPerPage()
        bottom = min(top + pn - 1, n)

        control.SetItemCount(n)

        if self._update_visible:
            control.RefreshItems(0, n - 1)
            self._update_visible = False

        if len(self.multi_selected_rows) > 0:
            self._multi_selected_rows_changed(self.multi_selected_rows)
        if len(self.multi_selected) > 0:
            self._multi_selected_changed(self.multi_selected)

        edit, self.edit = self.edit, False
        row, self.row = self.row, None

        if row is not None:
            if row >= n:
                row -= 1
                if row < 0:
                    row = None

        if row is None:
            visible = bottom
            if visible >= 0 and visible < control.GetItemCount():
                control.EnsureVisible(visible)
            return

        if 0 <= (row - top) < pn:
            control.EnsureVisible(top + pn - 2)
        elif row < top:
            control.EnsureVisible(row + pn - 1)
        else:
            control.EnsureVisible(row)

        control.SetItemState(row,
                             wx.LIST_STATE_SELECTED | wx.LIST_STATE_FOCUSED,
                             wx.LIST_STATE_SELECTED | wx.LIST_STATE_FOCUSED)

        if edit:
            control.EditLabel(row)

    #-- Trait Event Handlers -------------------------------------------------

    def _selected_changed(self, selected):
        """ Handles the editor's 'selected' trait being changed.
        """
        if not self._no_update:
            if selected is None:
                for row in self._get_selected():
                    self.control.SetItemState(row, 0, wx.LIST_STATE_SELECTED)
            else:
                try:
                    self.control.SetItemState(
                        self.value.index(selected),
                        wx.LIST_STATE_SELECTED,
                        wx.LIST_STATE_SELECTED)
                except:
                    pass

    def _selected_row_changed(self, old, new):
        """ Handles the editor's 'selected_index' trait being changed.
        """
        if not self._no_update:
            if new < 0:
                if old >= 0:
                    self.control.SetItemState(old, 0, wx.LIST_STATE_SELECTED)
            else:
                self.control.SetItemState(new, wx.LIST_STATE_SELECTED,
                                          wx.LIST_STATE_SELECTED)

    def _multi_selected_changed(self, selected):
        """ Handles the editor's 'multi_selected' trait being changed.
        """
        if not self._no_update:
            values = self.value
            try:
                self._multi_selected_rows_changed([values.index(item)
                                                   for item in selected])
            except:
                pass

    def _multi_selected_items_changed(self, event):
        """ Handles the editor's 'multi_selected' trait being modified.
        """
        values = self.values
        try:
            self._multi_selected_rows_items_changed(TraitListEvent(0, [values.index(
                item) for item in event.removed], [values.index(item) for item in event.added]))
        except:
            pass

    def _multi_selected_rows_changed(self, selected_rows):
        """ Handles the editor's 'multi_selected_rows' trait being changed.
        """
        if not self._no_update:
            control = self.control
            selected = self._get_selected()

            # Select any new items that aren't already selected:
            for row in selected_rows:
                if row in selected:
                    selected.remove(row)
                else:
                    control.SetItemState(row, wx.LIST_STATE_SELECTED,
                                         wx.LIST_STATE_SELECTED)

            # Unselect all remaining selected items that aren't selected now:
            for row in selected:
                control.SetItemState(row, 0, wx.LIST_STATE_SELECTED)

    def _multi_selected_rows_items_changed(self, event):
        """ Handles the editor's 'multi_selected_rows' trait being modified.
        """
        control = self.control

        # Remove all items that are no longer selected:
        for row in event.removed:
            control.SetItemState(row, 0, wx.LIST_STATE_SELECTED)

        # Select all newly added items:
        for row in event.added:
            control.SetItemState(row, wx.LIST_STATE_SELECTED,
                                 wx.LIST_STATE_SELECTED)

    def _refresh_changed(self):
        self.update_editor()

    #-- List Control Event Handlers ------------------------------------------

    def _left_down(self, event):
        """ Handles the left mouse button being pressed.
        """
        self._mouse_click(event, 'clicked')

    def _left_dclick(self, event):
        """ Handles the left mouse button being double clicked.
        """
        self._mouse_click(event, 'dclicked')

    def _right_down(self, event):
        """ Handles the right mouse button being pressed.
        """
        self._mouse_click(event, 'right_clicked')

    def _right_dclick(self, event):
        """ Handles the right mouse button being double clicked.
        """
        self._mouse_click(event, 'right_dclicked')

    def _begin_drag(self, event):
        """ Handles the user beginning a drag operation with the left mouse
            button.
        """
        if PythonDropSource is not None:
            adapter = self.adapter
            object, name = self.object, self.name
            selected = self._get_selected()
            drag_items = []

            # Collect all of the selected items to drag:
            for row in selected:
                drag = adapter.get_drag(object, name, row)
                if drag is None:
                    return

                drag_items.append(drag)

            # Save the drag item indices, so that we can later handle a
            # completed 'move' operation:
            self._drag_rows = selected

            try:
                # If only one item is being dragged, drag it as an item, not a
                # list:
                if len(drag_items) == 1:
                    drag_items = drag_items[0]

                # Perform the drag and drop operation:
                ds = PythonDropSource(self.control, drag_items)

                # If moves are allowed and the result was a drag move:
                if ((ds.result == wx.DragMove) and
                        (self._drag_local or self.factory.drag_move)):
                    # Then delete all of the original items (in reverse order
                    # from highest to lowest, so the indices don't need to be
                    # adjusted):
                    rows = self._drag_rows
                    rows.reverse()
                    for row in rows:
                        adapter.delete(object, name, row)
            finally:
                self._drag_rows = None
                self._drag_local = False

    def _begin_label_edit(self, event):
        """ Handles the user starting to edit an item label.
        """
        if not self.adapter.get_can_edit(self.object, self.name,
                                         event.GetIndex()):
            event.Veto()

    def _end_label_edit(self, event):
        """ Handles the user finishing editing an item label.
        """
        self.adapter.set_text(self.object, self.name, event.GetIndex(),
                              event.GetColumn(), event.GetText())
        self.row = event.GetIndex() + 1

    def _item_selected(self, event):
        """ Handles an item being selected.
        """
        self._no_update = True
        try:
            get_item = self.adapter.get_item
            object, name = self.object, self.name
            selected_rows = self._get_selected()
            if self.factory.multi_select:
                self.multi_selected_rows = selected_rows
                self.multi_selected = [get_item(object, name, row)
                                       for row in selected_rows]
            elif len(selected_rows) == 0:
                self.selected_row = -1
                self.selected = None
            else:
                self.selected_row = selected_rows[0]
                self.selected = get_item(object, name, selected_rows[0])
        finally:
            self._no_update = False

    def _item_activated(self, event):
        """ Handles an item being activated (double-clicked or enter pressed).
        """
        self.activated_row = event.GetIndex()
        self.activated = self.adapter.get_item(self.object, self.name,
                                               self.activated_row)

    def _key_down(self, event):
        """ Handles the user pressing a key in the list control.
        """
        key = event.GetKeyCode()
        if key == wx.WXK_NEXT:
            self._append_new()
        elif key in (wx.WXK_BACK, wx.WXK_DELETE):
            self._delete_current()
        elif key == wx.WXK_INSERT:
            self._insert_current()
        elif key == wx.WXK_LEFT:
            self._move_up_current()
        elif key == wx.WXK_RIGHT:
            self._move_down_current()
        elif key in (wx.WXK_RETURN, wx.WXK_ESCAPE):
            self._edit_current()
        else:
            event.Skip()

    def _column_right_clicked(self, event):
        """ Handles the user right-clicking a column header.
        """
        column = event.GetColumn()
        if ((self._cached_widths is not None) and
                (0 <= column < len(self._cached_widths))):
            self._cached_widths[column] = None
            self._size_modified(event)

    def _column_clicked(self, event):
        """ Handles the right mouse button being double clicked.
        """
        editor_event = TabularEditorEvent(
            editor=self,
            row=0,
            column=event.GetColumn()
        )

        setattr(self, 'column_clicked', editor_event)
        event.Skip()

    def _size_modified(self, event):
        """ Handles the size of the list control being changed.
        """
        control = self.control
        n = control.GetColumnCount()
        if n == 1:
            dx, dy = control.GetClientSizeTuple()
            control.SetColumnWidth(0, dx - 1)
        elif n > 1:
            do_later(self._set_column_widths)

        event.Skip()

    def _motion(self, event):
        """ Handles the user moving the mouse.
        """
        x = event.GetX()
        column = self._get_column(x)
        row, flags = self.control.HitTest(wx.Point(x, event.GetY()))
        if (row != self._last_row) or (column != self._last_column):
            self._last_row, self._last_column = row, column
            if (row == -1) or (column is None):
                tooltip = ''
            else:
                tooltip = self.adapter.get_tooltip(self.object, self.name,
                                                   row, column)
            if tooltip != self._last_tooltip:
                self._last_tooltip = tooltip
                wx.ToolTip.Enable(False)
                wx.ToolTip.Enable(True)
                self.control.SetToolTip(wx.ToolTip(tooltip))

    #-- Drag and Drop Event Handlers -----------------------------------------

    def wx_dropped_on(self, x, y, data, drag_result):
        """ Handles a Python object being dropped on the list control.
        """
        row, flags = self.control.HitTest(wx.Point(x, y))

        # If the user dropped it on an empty list, set the target as past the
        # end of the list:
        if ((row == -1) and
            ((flags & wx.LIST_HITTEST_NOWHERE) != 0) and
                (self.control.GetItemCount() == 0)):
            row = 0

        # If we have a valid drop target row, proceed:
        if row != -1:
            if not isinstance(data, list):
                # Handle the case of just a single item being dropped:
                self._wx_dropped_on(row, data)
            else:
                # Handles the case of a list of items being dropped, being
                # careful to preserve the original order of the source items if
                # possible:
                data.reverse()
                for item in data:
                    self._wx_dropped_on(row, item)

            # If this was an inter-list drag, mark it as 'local':
            if self._drag_indices is not None:
                self._drag_local = True

            # Return a successful drop result:
            return drag_result

        # Indicate we could not process the drop:
        return wx.DragNone

    def _wx_dropped_on(self, row, item):
        """ Helper method for handling a single item dropped on the list
            control.
        """
        adapter = self.adapter
        object, name = self.object, self.name

        # Obtain the destination of the dropped item relative to the target:
        destination = adapter.get_dropped(object, name, row, item)

        # Adjust the target index accordingly:
        if destination == 'after':
            row += 1

        # Insert the dropped item at the requested position:
        adapter.insert(object, name, row, item)

        # If the source for the drag was also this list control, we need to
        # adjust the original source indices to account for their new position
        # after the drag operation:
        rows = self._drag_rows
        if rows is not None:
            for i in range(len(rows) - 1, -1, -1):
                if rows[i] < row:
                    break

                rows[i] += 1

    def wx_drag_over(self, x, y, data, drag_result):
        """ Handles a Python object being dragged over the tree.
        """
        if isinstance(data, list):
            rc = wx.DragNone
            for item in data:
                rc = self.wx_drag_over(x, y, item, drag_result)
                if rc == wx.DragNone:
                    break

            return rc

        row, flags = self.control.HitTest(wx.Point(x, y))

        # If the user is dragging over an empty list, set the target to the end
        # of the list:
        if ((row == -1) and
            ((flags & wx.LIST_HITTEST_NOWHERE) != 0) and
                (self.control.GetItemCount() == 0)):
            row = 0

        # If the drag target index is valid and the adapter says it is OK to
        # drop the data here, then indicate the data can be dropped:
        if ((row != -1) and
                self.adapter.get_can_drop(self.object, self.name, row, data)):
            return drag_result

        # Else indicate that we will not accept the data:
        return wx.DragNone

    #-- UI preference save/restore interface ---------------------------------

    def restore_prefs(self, prefs):
        """ Restores any saved user preference information associated with the
            editor.
        """
        self._cached_widths = cws = prefs.get('cached_widths')
        if cws is not None:
            set_column_width = self.control.SetColumnWidth
            for i, width in enumerate(cws):
                if width is not None:
                    set_column_width(i, width)

    def save_prefs(self):
        """ Returns any user preference information associated with the editor.
        """
        cws = self._cached_widths
        if cws is not None:
            cws = [(None, cw)[cw >= 0] for cw in cws]

        return {'cached_widths': cws}

    #-- Private Methods ------------------------------------------------------

    def _refresh(self):
        """ Refreshes the contents of the editor's list control.
        """
        n = self.adapter.len(self.object, self.name)
        if n > 0:
            self.control.RefreshItems(0, n - 1)

    def _rebuild(self):
        """ Rebuilds the contents of the editor's list control.
        """
        control = self.control
        control.ClearAll()
        adapter, object, name = self.adapter, self.object, self.name
        adapter.object, adapter.name = object, name
        get_alignment = adapter.get_alignment
        get_width = adapter.get_width
        for i, label in enumerate(adapter.label_map):
            control.InsertColumn(
                i, label, alignment_map.get(
                    get_alignment(
                        object, name, i), wx.LIST_FORMAT_LEFT))
        self._set_column_widths()

    def _rebuild_all(self):
        """ Rebuilds the structure of the list control, then refreshes its
            contents.
        """
        self._rebuild()
        self.update_editor()

    def _set_column_widths(self):
        """ Set the column widths for the current set of columns.
        """
        control = self.control
        if control is None:
            return

        object, name = self.object, self.name
        dx, dy = control.GetClientSize()
        if is_mac:
            dx -= scrollbar_dx
        n = control.GetColumnCount()
        get_width = self.adapter.get_width
        pdx = 0
        wdx = 0.0
        widths = []
        cached = self._cached_widths
        current = [control.GetColumnWidth(i) for i in range(n)]
        if (cached is None) or (len(cached) != n):
            self._cached_widths = cached = [None] * n

        for i in range(n):
            cw = cached[i]
            if (cw is None) or (-cw == current[i]):
                width = float(get_width(object, name, i))
                if width <= 0.0:
                    width = 0.1
                if width <= 1.0:
                    wdx += width
                    cached[i] = -1
                else:
                    width = int(width)
                    pdx += width
                    if cw is None:
                        cached[i] = width
            else:
                cached[i] = width = current[i]
                pdx += width

            widths.append(width)

        adx = max(0, dx - pdx)

        control.Freeze()
        for i in range(n):
            width = cached[i]
            if width < 0:
                width = widths[i]
                if width <= 1.0:
                    widths[i] = w = max(30, int(round((adx * width) / wdx)))
                    wdx -= width
                    width = w
                    adx -= width
                    cached[i] = -w

            control.SetColumnWidth(i, width)

        control.Thaw()

    def _add_image(self, image_resource):
        """ Adds a new image to the wx.ImageList and its associated mapping.
        """
        bitmap = image_resource.create_image().ConvertToBitmap()

        image_list = self._image_list
        if image_list is None:
            self._image_list = image_list = wx.ImageList(bitmap.GetWidth(),
                                                         bitmap.GetHeight())
            self.control.AssignImageList(image_list, wx.IMAGE_LIST_SMALL)

        self.image_resources[image_resource] = \
            self.images[image_resource.name] = row = image_list.Add(bitmap)

        return row

    def _get_image(self, image):
        """ Converts a user specified image to a wx.ListCtrl image index.
        """
        if isinstance(image, six.string_types):
            self.image = image
            image = self.image

        if isinstance(image, ImageResource):
            result = self.image_resources.get(image)
            if result is not None:
                return result

            return self._add_image(image)

        return self.images.get(image)

    def _get_selected(self):
        """ Returns a list of the rows of all currently selected list items.
        """
        selected = []
        item = -1
        control = self.control

        # Handle case where the list is cleared
        if len(self.value) == 0:
            return selected

        while True:
            item = control.GetNextItem(item, wx.LIST_NEXT_ALL,
                                       wx.LIST_STATE_SELECTED)
            if item == -1:
                break

            selected.append(item)

        return selected

    def _append_new(self):
        """ Append a new item to the end of the list control.
        """
        if 'append' in self.factory.operations:
            adapter = self.adapter
            self.row = self.control.GetItemCount()
            self.edit = True
            adapter.insert(self.object, self.name, self.row,
                           adapter.get_default_value(self.object, self.name))

    def _insert_current(self):
        """ Inserts a new item after the currently selected list control item.
        """
        if 'insert' in self.factory.operations:
            selected = self._get_selected()
            if len(selected) == 1:
                adapter = self.adapter
                adapter.insert(
                    self.object,
                    self.name,
                    selected[0],
                    adapter.get_default_value(
                        self.object,
                        self.name))
                self.row = selected[0]
                self.edit = True

    def _delete_current(self):
        """ Deletes the currently selected items from the list control.
        """
        if 'delete' in self.factory.operations:
            selected = self._get_selected()
            if len(selected) == 0:
                return

            delete = self.adapter.delete
            selected.reverse()
            for row in selected:
                delete(self.object, self.name, row)

            n = self.adapter.len(self.object, self.name)
            if not self.factory.multi_select:
                self.selected_row = self.row = n - 1 if row >= n else row
            else:
                #FIXME: What should the selection be?
                self.multi_selected = []
                self.multi_selected_rows = []

    def _move_up_current(self):
        """ Moves the currently selected item up one line in the list control.
        """
        if 'move' in self.factory.operations:
            selected = self._get_selected()
            if len(selected) == 1:
                row = selected[0]
                if row > 0:
                    adapter = self.adapter
                    object, name = self.object, self.name
                    item = adapter.get_item(object, name, row)
                    adapter.delete(object, name, row)
                    adapter.insert(object, name, row - 1, item)
                    self.row = row - 1

    def _move_down_current(self):
        """ Moves the currently selected item down one line in the list control.
        """
        if 'move' in self.factory.operations:
            selected = self._get_selected()
            if len(selected) == 1:
                row = selected[0]
                if row < (self.control.GetItemCount() - 1):
                    adapter = self.adapter
                    object, name = self.object, self.name
                    item = adapter.get_item(object, name, row)
                    adapter.delete(object, name, row)
                    adapter.insert(object, name, row + 1, item)
                    self.row = row + 1

    def _edit_current(self):
        """ Allows the user to edit the current item in the list control.
        """
        if 'edit' in self.factory.operations and self.factory.editable_labels:
            selected = self._get_selected()
            if len(selected) == 1:
                self.control.EditLabel(selected[0])

    def _get_column(self, x, translate=False):
        """ Returns the column index corresponding to a specified x position.
        """
        if x >= 0:
            control = self.control
            for i in range(control.GetColumnCount()):
                x -= control.GetColumnWidth(i)
                if x < 0:
                    if translate:
                        return self.adapter.get_column(
                            self.object, self.name, i)

                    return i

        return None

    def _mouse_click(self, event, trait):
        """ Generate a TabularEditorEvent event for a specified mouse event and
            editor trait name.
        """
        x = event.GetX()
        row, flags = self.control.HitTest(wx.Point(x, event.GetY()))
        if row == wx.NOT_FOUND:
            if self.factory.multi_select:
                self.multi_selected = []
                self.multi_selected_rows = []
            else:
                self.selected = None
                self.selected_row = -1
        else:
            if self.factory.multi_select and event.ShiftDown():
                # Handle shift-click multi-selections because the wx.ListCtrl
                # does not (by design, apparently).
                # We must append this to the event queue because the
                # multi-selection will not be recorded until this event handler
                # finishes and lets the widget actually handle the event.
                do_later(self._item_selected, None)

            setattr(self, trait, TabularEditorEvent(
                editor=self,
                row=row,
                column=self._get_column(x, translate=True)
            ))

        # wx should continue with additional event handlers. Skip(False)
        # actually means to skip looking, skip(True) means to keep looking.
        # This seems backwards to me...
        event.Skip(True)

#-------------------------------------------------------------------------
#  'TabularEditorEvent' class:
#-------------------------------------------------------------------------


class TabularEditorEvent(HasStrictTraits):

    # The index of the row:
    row = Int

    # The id of the column (either a string or an integer):
    column = Any

    # The row item:
    item = Property

    #-- Private Traits -------------------------------------------------------

    # The editor the event is associated with:
    editor = Instance(TabularEditor)

    #-- Property Implementations ---------------------------------------------

    def _get_item(self):
        editor = self.editor
        return editor.adapter.get_item(editor.object, editor.name, self.row)
