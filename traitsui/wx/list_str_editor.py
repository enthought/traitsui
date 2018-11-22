#-------------------------------------------------------------------------
#
#  Copyright (c) 2007-13, Enthought, Inc.
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
#  Date:   05/08/2007
#
#-------------------------------------------------------------------------

""" Traits UI editor for editing lists of strings.
"""

#-------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------

from __future__ import absolute_import
import wx

from traits.api \
    import Str, Int, List, Bool, Instance, Any, Event, TraitListEvent, \
    Property

# FIXME: ListStrEditor is a proxy class defined here just for backward
# compatibility. The class has been moved to the
# traitsui.editors.list_editor file.
from traitsui.editors.list_str_editor \
    import ListStrEditor

from traitsui.list_str_adapter \
    import ListStrAdapter

from traitsui.wx.editor \
    import Editor

from pyface.image_resource \
    import ImageResource

from .helper \
    import disconnect, disconnect_no_id
from six.moves import range

try:
    from pyface.wx.drag_and_drop \
        import PythonDropSource, PythonDropTarget
except:
    PythonDropSource = PythonDropTarget = None

#-------------------------------------------------------------------------
#  'wxListCtrl' class:
#-------------------------------------------------------------------------


class wxListCtrl(wx.ListCtrl):
    """ Subclass of wx.ListCtrl to provide correct virtual list behavior.
    """

    def OnGetItemAttr(self, index):
        """ Returns the display attributes to use for the specified list item.
        """
        # fixme: There appears to be a bug in wx in that they do not correctly
        # manage the reference count for the returned object, and it seems to be
        # gc'ed before they finish using it. So we store an object reference to
        # it to prevent it from going away too soon...
        self._attr = attr = wx.ListItemAttr()
        editor = self._editor
        adapter = editor.adapter

        if editor._is_auto_add(index):
            bg_color = adapter.get_default_bg_color(editor.object,
                                                    editor.name)
            color = adapter.get_default_text_color(editor.object, editor.name)
        else:
            bg_color = adapter.get_bg_color(editor.object, editor.name, index)
            color = adapter.get_text_color(editor.object, editor.name, index)

        if bg_color is not None:
            attr.SetBackgroundColour(bg_color)

        if color is not None:
            attr.SetTextColour(color)

        return attr

    def OnGetItemImage(self, index):
        """ Returns the image index to use for the specified list item.
        """
        editor = self._editor
        if editor._is_auto_add(index):
            image = editor.adapter.get_default_image(editor.object,
                                                     editor.name)
        else:
            image = editor.adapter.get_image(editor.object, editor.name,
                                             index)

        image = editor._get_image(image)
        if image is not None:
            return image

        return -1

    def OnGetItemText(self, index, column):
        """ Returns the text to use for the specified list item.
        """
        editor = self._editor

        if editor._is_auto_add(index):
            return editor.adapter.get_default_text(editor.object, editor.name)

        return editor.adapter.get_text(editor.object, editor.name, index)

#-------------------------------------------------------------------------
#  '_ListStrEditor' class:
#-------------------------------------------------------------------------


class _ListStrEditor(Editor):
    """ Traits UI editor for editing lists of strings.
    """

    #-- Trait Definitions ----------------------------------------------------

    # The title of the editor:
    title = Str

    # The current set of selected items (which one is used depends upon the
    # initial state of the editor factory 'multi_select' trait):
    selected = Any
    multi_selected = List

    # The current set of selected item indices (which one is used depends upon
    # the initial state of the editor factory 'multi_select' trait):
    selected_index = Int
    multi_selected_indices = List(Int)

    # The most recently actived item and its index:
    activated = Any
    activated_index = Int

    # The most recently right_clicked item and its index:
    right_clicked = Event
    right_clicked_index = Event

    # Is the list editor scrollable? This value overrides the default.
    scrollable = True

    # Index of item to select after rebuilding editor list:
    index = Any

    # Should the selected item be edited after rebuilding the editor list:
    edit = Bool(False)

    # The adapter from list items to editor values:
    adapter = Instance(ListStrAdapter)

    # Dictionaly mapping image names to wx.ImageList indices:
    images = Any({})

    # Dictionary mapping ImageResource objects to wx.ImageList indices:
    image_resources = Any({})

    # The current number of item currently in the list:
    item_count = Property

    # The current search string:
    search = Str

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
        self.sync_value(factory.adapter_name, 'adapter', 'from')

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
        self.control = control = wxListCtrl(parent, -1, style=style)
        control._editor = self

        # Create the list control column:
        control.InsertColumn(0, '')

        # Set up the list control's event handlers:
        id = control.GetId()
        wx.EVT_LIST_BEGIN_DRAG(parent, id, self._begin_drag)
        wx.EVT_LIST_BEGIN_LABEL_EDIT(parent, id, self._begin_label_edit)
        wx.EVT_LIST_END_LABEL_EDIT(parent, id, self._end_label_edit)
        wx.EVT_LIST_ITEM_SELECTED(parent, id, self._item_selected)
        wx.EVT_LIST_ITEM_DESELECTED(parent, id, self._item_selected)
        wx.EVT_LIST_ITEM_RIGHT_CLICK(parent, id, self._right_clicked)
        wx.EVT_LIST_ITEM_ACTIVATED(parent, id, self._item_activated)
        wx.EVT_SIZE(control, self._size_modified)

        # Handle key events:
        wx.EVT_CHAR(control, self._key_pressed)

        # Handle mouse events:
        if 'edit' in factory.operations:
            wx.EVT_LEFT_DOWN(control, self._left_down)

        # Set up the drag and drop target:
        if PythonDropTarget is not None:
            control.SetDropTarget(PythonDropTarget(self))

        # Initialize the editor title:
        self.title = factory.title
        self.sync_value(factory.title_name, 'title', 'from')

        # Set up the selection listener (if necessary):
        if factory.multi_select:
            self.sync_value(factory.selected, 'multi_selected', 'both',
                            is_list=True)
            self.sync_value(factory.selected_index, 'multi_selected_indices',
                            'both', is_list=True)
        else:
            self.sync_value(factory.selected, 'selected', 'both')
            self.sync_value(factory.selected_index, 'selected_index', 'both')

        # Synchronize other interesting traits as necessary:
        self.sync_value(factory.activated, 'activated', 'to')
        self.sync_value(factory.activated_index, 'activated_index', 'to')

        self.sync_value(factory.right_clicked, 'right_clicked', 'to')
        self.sync_value(factory.right_clicked_index, 'right_clicked_index',
                        'to')

        # Make sure we listen for 'items' changes as well as complete list
        # replacements:
        self.context_object.on_trait_change(
            self.update_editor,
            self.extended_name + '_items',
            dispatch='ui')

        # Create the mapping from user supplied images to wx.ImageList indices:
        for image_resource in factory.images:
            self._add_image(image_resource)

        # Refresh the editor whenever the adapter changes:
        self.on_trait_change(self._refresh, 'adapter.+update',
                             dispatch='ui')

        # Set the list control's tooltip:
        self.set_tooltip()

    def dispose(self):
        """ Disposes of the contents of an editor.
        """
        disconnect(self.control, wx.EVT_LIST_BEGIN_DRAG,
                   wx.EVT_LIST_BEGIN_LABEL_EDIT, wx.EVT_LIST_END_LABEL_EDIT,
                   wx.EVT_LIST_ITEM_SELECTED, wx.EVT_LIST_ITEM_DESELECTED,
                   wx.EVT_LIST_ITEM_RIGHT_CLICK, wx.EVT_LIST_ITEM_ACTIVATED)

        disconnect_no_id(self.control,
                         wx.EVT_SIZE, wx.EVT_CHAR, wx.EVT_LEFT_DOWN)

        self.context_object.on_trait_change(
            self.update_editor,
            self.extended_name + '_items',
            remove=True)
        self.on_trait_change(self._refresh, 'adapter.+update', remove=True)

        super(_ListStrEditor, self).dispose()

    def update_editor(self):
        """ Updates the editor when the object trait changes externally to the
            editor.
        """
        control = self.control
        top = control.GetTopItem()
        pn = control.GetCountPerPage()
        n = self.adapter.len(self.object, self.name)
        if self.factory.auto_add:
            n += 1

        control.DeleteAllItems()
        control.SetItemCount(n)
        if control.GetItemCount() > 0:
            control.RefreshItems(0, control.GetItemCount() - 1)
        control.SetColumnWidth(0, control.GetClientSizeTuple()[0])

        edit, self.edit = self.edit, False
        index, self.index = self.index, None

        if index is not None:
            if index >= n:
                index -= 1
                if index < 0:
                    index = None

        if index is None:
            visible = top + pn - 2
            if visible >= 0 and visible < control.GetItemCount():
                control.EnsureVisible(visible)
            if self.factory.multi_select:
                for index in self.multi_selected_indices:
                    if 0 <= index < n:
                        control.SetItemState(index, wx.LIST_STATE_SELECTED,
                                             wx.LIST_STATE_SELECTED)
            else:
                if 0 <= self.selected_index < n:
                    control.SetItemState(
                        self.selected_index,
                        wx.LIST_STATE_SELECTED,
                        wx.LIST_STATE_SELECTED)
            return

        if 0 <= (index - top) < pn:
            control.EnsureVisible(max(0, top + pn - 2))
        elif index < top:
            control.EnsureVisible(min(n, index + pn - 1))
        else:
            control.EnsureVisible(index)

        control.SetItemState(index,
                             wx.LIST_STATE_SELECTED | wx.LIST_STATE_FOCUSED,
                             wx.LIST_STATE_SELECTED | wx.LIST_STATE_FOCUSED)

        if edit:
            control.EditLabel(index)

    #-- Property Implementations ---------------------------------------------

    def _get_item_count(self):
        return (self.control.GetItemCount() - self.factory.auto_add)

    #-- Trait Event Handlers -------------------------------------------------

    def _title_changed(self, title):
        """ Handles the editor title being changed.
        """
        list_item = wx.ListItem()
        list_item.SetText(title)
        self.control.SetColumn(0, list_item)

    def _selected_changed(self, selected):
        """ Handles the editor's 'selected' trait being changed.
        """
        if not self._no_update:
            try:
                self.control.SetItemState(
                    self.value.index(selected),
                    wx.LIST_STATE_SELECTED,
                    wx.LIST_STATE_SELECTED)
            except Exception:
                pass

    def _selected_index_changed(self, selected_index):
        """ Handles the editor's 'selected_index' trait being changed.
        """
        if not self._no_update:
            try:
                self.control.SetItemState(
                    selected_index,
                    wx.LIST_STATE_SELECTED,
                    wx.LIST_STATE_SELECTED)
            except Exception:
                pass

    def _multi_selected_changed(self, selected):
        """ Handles the editor's 'multi_selected' trait being changed.
        """
        if not self._no_update:
            values = self.value
            try:
                self._multi_selected_indices_changed([values.index(item)
                                                      for item in selected])
            except Exception:
                pass

    def _multi_selected_items_changed(self, event):
        """ Handles the editor's 'multi_selected' trait being modified.
        """
        values = self.values
        try:
            self._multi_selected_indices_items_changed(TraitListEvent(0, [values.index(
                item) for item in event.removed], [values.index(item) for item in event.added]))
        except Exception:
            pass

    def _multi_selected_indices_changed(self, selected_indices):
        """ Handles the editor's 'multi_selected_indices' trait being changed.
        """
        if not self._no_update:
            control = self.control
            selected = self._get_selected()

            # Select any new items that aren't already selected:
            for index in selected_indices:
                if index in selected:
                    selected.remove(index)
                else:
                    try:
                        control.SetItemState(index, wx.LIST_STATE_SELECTED,
                                             wx.LIST_STATE_SELECTED)
                    except Exception:
                        pass

            # Unselect all remaining selected items that aren't selected now:
            for index in selected:
                control.SetItemState(index, 0, wx.LIST_STATE_SELECTED)

    def _multi_selected_indices_items_changed(self, event):
        """ Handles the editor's 'multi_selected_indices' trait being modified.
        """
        control = self.control

        # Remove all items that are no longer selected:
        for index in event.removed:
            control.SetItemState(index, 0, wx.LIST_STATE_SELECTED)

        # Select all newly added items:
        for index in event.added:
            control.SetItemState(index, wx.LIST_STATE_SELECTED,
                                 wx.LIST_STATE_SELECTED)

    #-- List Control Event Handlers ------------------------------------------

    def _begin_drag(self, event):
        """ Handles the user beginning a drag operation with the left mouse
            button.
        """
        if PythonDropSource is not None:
            adapter = self.adapter
            object, name = self.object, self.name
            index = event.GetIndex()
            selected = self._get_selected()
            drag_items = []

            # Collect all of the selected items to drag:
            for index in selected:
                drag = adapter.get_drag(object, name, index)
                if drag is None:
                    return

                drag_items.append(drag)

            # Save the drag item indices, so that we can later handle a
            # completed 'move' operation:
            self._drag_indices = selected

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
                    indices = self._drag_indices
                    indices.reverse()
                    for index in indices:
                        adapter.delete(object, name, index)
            finally:
                self._drag_indices = None
                self._drag_local = False

    def _begin_label_edit(self, event):
        """ Handles the user starting to edit an item label.
        """
        index = event.GetIndex()

        if ((not self._is_auto_add(index)) and (
                not self.adapter.get_can_edit(self.object, self.name, index))):
            event.Veto()

    def _end_label_edit(self, event):
        """ Handles the user finishing editing an item label.
        """
        self._set_text_current(event.GetIndex(), event.GetText())

    def _item_selected(self, event):
        """ Handles an item being selected.
        """
        self._no_update = True
        try:
            get_item = self.adapter.get_item
            object, name = self.object, self.name
            selected_indices = self._get_selected()
            if self.factory.multi_select:
                self.multi_selected_indices = selected_indices
                self.multi_selected = [get_item(object, name, index)
                                       for index in selected_indices]
            elif len(selected_indices) == 0:
                self.selected_index = -1
                self.selected = None
            else:
                self.selected_index = selected_indices[0]
                self.selected = get_item(object, name,
                                         selected_indices[0])
        finally:
            self._no_update = False

    def _item_activated(self, event):
        """ Handles an item being activated (double-clicked or enter pressed).
        """
        self.activated_index = event.GetIndex()
        if 'edit' in self.factory.operations:
            self._edit_current()
        else:
            self.activated = self.adapter.get_item(self.object, self.name,
                                                   self.activated_index)

    def _right_clicked(self, event):
        """ Handles an item being right clicked.
        """
        self.right_clicked_index = index = event.GetIndex()
        self.right_clicked = self.adapter.get_item(self.object, self.name,
                                                   index)

    def _key_pressed(self, event):
        key = event.GetKeyCode()
        control = event.ControlDown()

        if 32 <= key <= 126:
            self.search += chr(key).lower()
            self._search_for_string()
        elif key in (wx.WXK_HOME, wx.WXK_PAGEUP, wx.WXK_PAGEDOWN):
            self.search = ''
            event.Skip()
        elif key == wx.WXK_END:
            self.search = ''
            self._append_new()
        elif (key == wx.WXK_UP) and control:
            self._search_for_string(-1)
        elif (key == wx.WXK_DOWN) and control:
            self._search_for_string(1)
        elif key in (wx.WXK_BACK, wx.WXK_DELETE):
            self._delete_current()
        elif key == wx.WXK_INSERT:
            self._insert_current()
        elif key == wx.WXK_LEFT:
            self._move_up_current()
        elif key == wx.WXK_RIGHT:
            self._move_down_current()
        elif key == wx.WXK_RETURN:
            self._edit_current()
        elif key == 3:    # Ctrl-C
            self._copy_current()
        elif key == 22:   # Ctrl-V
            self._paste_current()
        elif key == 24:   # Ctrl-X
            self._cut_current()
        else:
            event.Skip()

    def _size_modified(self, event):
        """ Handles the size of the list control being changed.
        """
        dx, dy = self.control.GetClientSizeTuple()
        self.control.SetColumnWidth(0, dx - 1)
        event.Skip()

    def _left_down(self, event):
        """ Handles the user pressing the left mouse button.
        """
        index, flags = self.control.HitTest(wx.Point(event.GetX(),
                                                     event.GetY()))
        selected = self._get_selected()
        if (len(selected) == 1) and (index == selected[0]):
            self._edit_current()
        else:
            event.Skip()

    #-- Drag and Drop Event Handlers -----------------------------------------

    def wx_dropped_on(self, x, y, data, drag_result):
        """ Handles a Python object being dropped on the list control.
        """
        index, flags = self.control.HitTest(wx.Point(x, y))

        # If the user dropped it on an empty list, set the target as past the
        # end of the list:
        if ((index == -1) and
            ((flags & wx.LIST_HITTEST_NOWHERE) != 0) and
                (self.control.GetItemCount() == 0)):
            index = 0

        # If we have a valid drop target index, proceed:
        if index != -1:
            if not isinstance(data, list):
                # Handle the case of just a single item being dropped:
                self._wx_dropped_on(index, data)
            else:
                # Handles the case of a list of items being dropped, being
                # careful to preserve the original order of the source items if
                # possible:
                data.reverse()
                for item in data:
                    self._wx_dropped_on(index, item)

            # If this was an inter-list drag, mark it as 'local':
            if self._drag_indices is not None:
                self._drag_local = True

            # Return a successful drop result:
            return drag_result

        # Indicate we could not process the drop:
        return wx.DragNone

    def _wx_dropped_on(self, index, item):
        """ Helper method for handling a single item dropped on the list
            control.
        """
        adapter = self.adapter
        object, name = self.object, self.name

        # Obtain the destination of the dropped item relative to the target:
        destination = adapter.get_dropped(object, name, index, item)

        # Adjust the target index accordingly:
        if destination == 'after':
            index += 1

        # Insert the dropped item at the requested position:
        adapter.insert(object, name, index, item)

        # If the source for the drag was also this list control, we need to
        # adjust the original source indices to account for their new position
        # after the drag operation:
        indices = self._drag_indices
        if indices is not None:
            for i in range(len(indices) - 1, -1, -1):
                if indices[i] < index:
                    break

                indices[i] += 1

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

        index, flags = self.control.HitTest(wx.Point(x, y))

        # If the user is dragging over an empty list, set the target to the end
        # of the list:
        if ((index == -1) and
            ((flags & wx.LIST_HITTEST_NOWHERE) != 0) and
                (self.control.GetItemCount() == 0)):
            index = 0

        # If the drag target index is valid and the adapter says it is OK to
        # drop the data here, then indicate the data can be dropped:
        if ((index != -1) and
                self.adapter.get_can_drop(self.object, self.name, index, data)):
            return drag_result

        # Else indicate that we will not accept the data:
        return wx.DragNone

    #-- Private Methods ------------------------------------------------------

    def _refresh(self):
        """ Refreshes the contents of the editor's list control.
        """
        self.control.RefreshItems(0, len(self.value) - 1)

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
            self.images[image_resource.name] = index = image_list.Add(bitmap)

        return index

    def _get_image(self, image):
        """ Converts a user specified image to a wx.ListCtrl image index.
        """
        if isinstance(image, ImageResource):
            result = self.image_resources.get(image)
            if result is not None:
                return result

            return self._add_image(image)

        return self.images.get(image)

    def _get_selected(self):
        """ Returns a list of the indices of all currently selected list items.
        """
        selected = []
        item = -1
        control = self.control
        while True:
            item = control.GetNextItem(item, wx.LIST_NEXT_ALL,
                                       wx.LIST_STATE_SELECTED)
            if item == -1:
                break

            selected.append(item)

        return selected

    def _search_for_string(self, increment=0):
        """ Searches for the next occurrence of the current search string.
        """
        selected = self._get_selected()
        if len(selected) > 1:
            return

        start = 0
        if len(selected) == 1:
            start = selected[0] + increment

        get_text = self.adapter.get_text
        search = self.search
        object = self.object
        name = self.name

        if increment >= 0:
            items = range(start, self.item_count)
        else:
            items = range(start, -1, -1)

        for index in items:
            if search in get_text(object, name, index).lower():
                self.index = index
                self.update_editor()
                break

    def _append_new(self):
        """ Append a new item to the end of the list control.
        """
        if 'append' in self.factory.operations:
            self.edit = True
            adapter = self.adapter
            index = self.control.GetItemCount()
            if self.factory.auto_add:
                self.index = index - 1
                self.update_editor()
            else:
                self.index = index
                adapter.insert(
                    self.object,
                    self.name,
                    self.index,
                    adapter.get_default_value(
                        self.object,
                        self.name))

    def _copy_current(self):
        """ Copies the currently selected list control item to the clipboard.
        """
        selected = self._get_selected()
        if len(selected) == 1:
            index = selected[0]
            if index < self.item_count:
                try:
                    from pyface.wx.clipboard import clipboard

                    clipboard.data = self.adapter.get_text(self.object,
                                                           self.name, index)
                except:
                    # Handle the traits.util package not being installed by
                    # just ignoring the request:
                    pass

    def _cut_current(self):
        """ Cuts the currently selected list control item and places its value
            in the clipboard.
        """
        ops = self.factory.operations
        if ('insert' in ops) and ('delete' in ops):
            selected = self._get_selected()
            if len(selected) == 1:
                index = selected[0]
                if index < self.item_count:
                    try:
                        from pyface.wx.clipboard import clipboard

                        clipboard.data = self.adapter.get_text(
                            self.object, self.name, index)
                        self.index = index
                        self.adapter.delete(self.object, self.name, index)
                    except:
                        # Handle the traits.util package not being installed
                        # by just ignoring the request:
                        pass

    def _paste_current(self):
        """ Pastes the clipboard contents into the currently selected list
            control item.
        """
        if 'insert' in self.factory.operations:
            selected = self._get_selected()
            if len(selected) == 1:
                try:
                    from pyface.wx.clipboard import clipboard

                    self._set_text_current(selected[0], clipboard.text_data,
                                           insert=True)
                except:
                    # Handle the traits.util package not being installed by
                    # just ignoring the request:
                    pass

    def _insert_current(self):
        """ Inserts a new item after the currently selected list control item.
        """
        if 'insert' in self.factory.operations:
            selected = self._get_selected()
            if len(selected) == 1:
                self.index = selected[0]
                self.edit = True
                adapter = self.adapter
                adapter.insert(
                    self.object,
                    self.name,
                    selected[0],
                    adapter.get_default_value(
                        self.object,
                        self.name))

    def _delete_current(self):
        """ Deletes the currently selected items from the list control.
        """
        if 'delete' in self.factory.operations:
            selected = self._get_selected()
            if len(selected) == 0:
                return

            n = self.item_count
            delete = self.adapter.delete
            selected.reverse()
            self.index = selected[-1]
            for index in selected:
                if index < n:
                    delete(self.object, self.name, index)

    def _move_up_current(self):
        """ Moves the currently selected item up one line in the list control.
        """
        if 'move' in self.factory.operations:
            selected = self._get_selected()
            if len(selected) == 1:
                index = selected[0]
                n = self.item_count
                if 0 < index < n:
                    adapter = self.adapter
                    object, name = self.object, self.name
                    item = adapter.get_item(object, name, index)
                    adapter.delete(object, name, index)
                    self.index = index - 1
                    adapter.insert(object, name, index - 1, item)

    def _move_down_current(self):
        """ Moves the currently selected item down one line in the list control.
        """
        if 'move' in self.factory.operations:
            selected = self._get_selected()
            if len(selected) == 1:
                index = selected[0]
                n = self.item_count - 1
                if index < n:
                    adapter = self.adapter
                    object, name = self.object, self.name
                    item = adapter.get_item(object, name, index)
                    adapter.delete(object, name, index)
                    self.index = index + 1
                    adapter.insert(object, name, index + 1, item)

    def _edit_current(self):
        """ Allows the user to edit the current item in the list control.
        """
        if 'edit' in self.factory.operations:
            selected = self._get_selected()
            if len(selected) == 1:
                self.control.EditLabel(selected[0])

    def _is_auto_add(self, index):
        """ Returns whether or not the index is the special 'auto add' item at
            the end of the list.
        """
        return (self.factory.auto_add and
                (index >= self.adapter.len(self.object, self.name)))

    def _set_text_current(self, index, text, insert=False):
        """ Sets the text value of the specified list control item.
        """
        if text.strip() != '':
            object, name, adapter = self.object, self.name, self.adapter
            if insert or self._is_auto_add(index):
                adapter.insert(object, name, index,
                               adapter.get_default_value(object, name))
                self.edit = (not insert)

            self.index = index + 1
            adapter.set_text(object, name, index, text)

#--EOF-------------------------------------------------------------------------
