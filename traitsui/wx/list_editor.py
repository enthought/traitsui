# (C) Copyright 2004-2023 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

""" Defines the various list editors for the wxPython user interface toolkit.
"""


import wx

import wx.lib.scrolledpanel as wxsp

from traits.api import (
    Any,
    Bool,
    cached_property,
    Instance,
    Property,
    Str,
    TraitError,
)
from traits.trait_base import user_name_for, xgetattr

from traitsui.ui_traits import Image, convert_bitmap
from traitsui.editors.list_editor import ListItemProxy, ToolkitEditorFactory
from traitsui.dockable_view_element import DockableViewElement

from pyface.dock.api import (
    DockWindow,
    DockSizer,
    DockSection,
    DockRegion,
    DockControl,
)

from . import toolkit
from .constants import scrollbar_dx
from .editor import Editor
from .menu import MakeMenu
from .image_control import ImageControl


# -------------------------------------------------------------------------
#  'SimpleEditor' class:
# -------------------------------------------------------------------------


class SimpleEditor(Editor):
    """Simple style of editor for lists, which displays a scrolling list box
    with only one item visible at a time. A icon next to the list box displays
    a menu of operations on the list.
    """

    # -------------------------------------------------------------------------
    #  Trait definitions:
    # -------------------------------------------------------------------------

    #: The kind of editor to create for each list item
    kind = Str()

    #: Is the list of items being edited mutable?
    mutable = Bool()

    #: The image used by the editor:
    image = Image("list_editor")

    #: The bitmap used by the editor:
    bitmap = Property()

    # -------------------------------------------------------------------------
    #  Class constants:
    # -------------------------------------------------------------------------

    #: Whether the list is displayed in a single row
    single_row = True

    # -------------------------------------------------------------------------
    #  Normal list item menu:
    # -------------------------------------------------------------------------

    #: Menu for modifying the list
    list_menu = """
       Add Before     [_menu_before]: self.add_before()
       Add After      [_menu_after]:  self.add_after()
       ---
       Delete         [_menu_delete]: self.delete_item()
       ---
       Move Up        [_menu_up]:     self.move_up()
       Move Down      [_menu_down]:   self.move_down()
       Move to Top    [_menu_top]:    self.move_top()
       Move to Bottom [_menu_bottom]: self.move_bottom()
    """

    # -------------------------------------------------------------------------
    #  Empty list item menu:
    # -------------------------------------------------------------------------

    empty_list_menu = """
       Add: self.add_empty()
    """

    def init(self, parent):
        """Finishes initializing the editor by creating the underlying toolkit
        widget.
        """
        # Initialize the trait handler to use:
        trait_handler = self.factory.trait_handler
        if trait_handler is None:
            trait_handler = self.object.base_trait(self.name).handler
        self._trait_handler = trait_handler

        # Create a scrolled window to hold all of the list item controls:
        self.control = wxsp.ScrolledPanel(parent, -1)
        self.control.SetBackgroundColour(parent.GetBackgroundColour())
        self.control.SetAutoLayout(True)

        # Remember the editor to use for each individual list item:
        editor = self.factory.editor
        if editor is None:
            editor = trait_handler.item_trait.get_editor()
        self._editor = getattr(editor, self.kind)

        # Set up the additional 'list items changed' event handler needed for
        # a list based trait. Note that we want to fire the update_editor_item
        # only when the items in the list change and not when intermediate
        # traits change. Therefore, replace "." by ":" in the extended_name
        # when setting up the listener.
        extended_name = self.extended_name.replace(".", ":")
        self.context_object.on_trait_change(
            self.update_editor_item, extended_name + "_items?", dispatch="ui"
        )
        self.set_tooltip()

    def dispose(self):
        """Disposes of the contents of an editor."""
        extended_name = self.extended_name.replace(".", ":")
        self.context_object.on_trait_change(
            self.update_editor_item, extended_name + "_items?", remove=True
        )
        self._dispose_items()

        super().dispose()

    def update_editor(self):
        """Updates the editor when the object trait changes externally to the
        editor.
        """
        # Disconnect the editor from any control about to be destroyed:
        self._dispose_items()

        # Get rid of any previous contents:
        list_pane = self.control
        list_pane.SetSizer(None)
        for child in list_pane.GetChildren():
            toolkit.destroy_control(child)

        # Create all of the list item trait editors:
        trait_handler = self._trait_handler
        resizable = (
            trait_handler.minlen != trait_handler.maxlen
        ) and self.mutable
        item_trait = trait_handler.item_trait
        factory = self.factory
        list_sizer = wx.FlexGridSizer(
            len(self.value), (1 + resizable) * factory.columns, 0, 0
        )
        j = 0
        for i in range(factory.columns):
            list_sizer.AddGrowableCol(j)
            j += 1 + resizable

        values = self.value
        index = 0
        width, height = 0, 0

        is_fake = resizable and (values is None or len(values) == 0)
        if is_fake:
            values = [item_trait.default_value()[1]]

        panel_height = 0
        editor = self._editor
        for value in values:
            width1 = height = 0
            if resizable:
                control = ImageControl(
                    list_pane, self.bitmap, -1, self.popup_menu
                )
                width1, height = control.GetSize()
                width1 += 4

            try:
                proxy = ListItemProxy(
                    self.object, self.name, index, item_trait, value
                )
                if resizable:
                    control.proxy = proxy
                peditor = editor(
                    self.ui, proxy, "value", self.description, list_pane
                ).trait_set(object_name="")
                peditor.prepare(list_pane)
                pcontrol = peditor.control
                pcontrol.proxy = proxy
            except:
                if not is_fake:
                    raise

                pcontrol = wx.Button(list_pane, -1, "sample")

            pcontrol.Fit()
            width2, height2 = size = pcontrol.GetSize()
            pcontrol.SetMinSize(size)
            width = max(width, width1 + width2)
            height = max(height, height2)
            panel_height += height

            list_sizer.Add(pcontrol, 0, wx.EXPAND)

            if resizable:
                list_sizer.Add(control, 0, wx.LEFT | wx.RIGHT, 2)

            index += 1

        list_pane.SetSizer(list_sizer)

        if not self.mutable:
            # list_sizer.SetDimension(0,0,width, panel_height)
            list_pane.SetInitialSize(list_sizer.GetSize())

        if is_fake:
            self._cur_control = control
            self.empty_list()
            control.Destroy()
            pcontrol.Destroy()

        rows = 1
        if not self.single_row:
            rows = self.factory.rows

        # Make sure we have valid values set for width and height (in case there
        # was no data to base them on):
        if width == 0:
            width = 100

        if panel_height == 0:
            panel_height = 20

        list_pane.SetMinSize(
            wx.Size(
                width + ((trait_handler.maxlen > rows) * scrollbar_dx),
                panel_height,
            )
        )

        list_pane.SetupScrolling()
        list_pane.GetParent().Layout()

    def update_editor_item(self, obj, name, event):
        """Updates the editor when an item in the object trait changes
        externally to the editor.
        """
        # If this is not a simple, single item update, rebuild entire editor:
        if (len(event.removed) != 1) or (len(event.added) != 1):
            self.update_editor()
            return

        # Otherwise, find the proxy for this index and update it with the
        # changed value:
        for control in self.control.GetChildren():
            proxy = control.proxy
            if proxy.index == event.index:
                proxy.value = event.added[0]
                break

    def empty_list(self):
        """Creates an empty list entry (so the user can add a new item)."""
        control = ImageControl(
            self.control, self.bitmap, -1, self.popup_empty_menu
        )
        control.is_empty = True
        proxy = ListItemProxy(self.object, self.name, -1, None, None)
        pcontrol = wx.StaticText(self.control, -1, "   (Empty List)")
        pcontrol.proxy = control.proxy = proxy
        self.reload_sizer([(control, pcontrol)])

    def reload_sizer(self, controls, extra=0):
        """Reloads the layout from the specified list of ( button, proxy )
        pairs.
        """
        sizer = self.control.GetSizer()
        for i in range(2 * len(controls) + extra):
            sizer.Remove(0)
        index = 0
        for control, pcontrol in controls:
            sizer.Add(pcontrol, 1, wx.EXPAND)
            sizer.Add(control, 0, wx.LEFT | wx.RIGHT, 2)
            control.proxy.index = index
            index += 1
        sizer.Layout()
        self.control.SetVirtualSize(sizer.GetMinSize())

    def get_info(self):
        """Returns the associated object list and current item index."""
        proxy = self._cur_control.proxy
        return (proxy.list, proxy.index)

    def popup_empty_menu(self, control):
        """Displays the empty list editor popup menu."""
        self._cur_control = control
        menu = MakeMenu(self.empty_list_menu, self, True, self.control).menu
        self.control.PopupMenu(menu, control.GetPosition())
        menu.Destroy()

    def popup_menu(self, control):
        """Displays the list editor popup menu."""
        self._cur_control = control
        # Makes sure that any text that was entered get's added (Pressure
        # #145):
        control.SetFocus()
        proxy = control.proxy
        index = proxy.index
        menu = MakeMenu(self.list_menu, self, True, self.control).menu
        len_list = len(proxy.list)
        not_full = len_list < self._trait_handler.maxlen
        self._menu_before.enabled(not_full)
        self._menu_after.enabled(not_full)
        self._menu_delete.enabled(len_list > self._trait_handler.minlen)
        self._menu_up.enabled(index > 0)
        self._menu_top.enabled(index > 0)
        self._menu_down.enabled(index < (len_list - 1))
        self._menu_bottom.enabled(index < (len_list - 1))
        x, y = control.GetPosition()

        self.control.PopupMenu(menu, (x + 8, y + 32))
        menu.Destroy()

    def add_item(self, offset):
        """Adds a new value at the specified list index."""
        list, index = self.get_info()
        index += offset
        item_trait = self._trait_handler.item_trait
        if self.factory.item_factory:
            value = self.factory.item_factory(
                *self.factory.item_factory_args,
                **self.factory.item_factory_kwargs,
            )
        else:
            value = item_trait.default_value_for(self.object, self.name)
        try:
            self.value = list[:index] + [value] + list[index:]
        # if the default new item is invalid, we just don't add it to the list.
        # traits will still give an error message, but we don't want to crash
        except TraitError:
            from traitsui.api import raise_to_debug

            raise_to_debug()
        wx.CallAfter(self.update_editor)

    def add_before(self):
        """Inserts a new item before the current item."""
        self.add_item(0)

    def add_after(self):
        """Inserts a new item after the current item."""
        self.add_item(1)

    def add_empty(self):
        """Adds a new item when the list is empty."""
        list, index = self.get_info()
        self.add_item(0)

    def delete_item(self):
        """Delete the current item."""
        list, index = self.get_info()
        self.value = list[:index] + list[index + 1 :]
        wx.CallAfter(self.update_editor)

    def move_up(self):
        """Move the current item up one in the list."""
        list, index = self.get_info()
        self.value = (
            list[: index - 1]
            + [list[index], list[index - 1]]
            + list[index + 1 :]
        )
        wx.CallAfter(self.update_editor)

    def move_down(self):
        """Moves the current item down one in the list."""
        list, index = self.get_info()
        self.value = (
            list[:index] + [list[index + 1], list[index]] + list[index + 2 :]
        )
        wx.CallAfter(self.update_editor)

    def move_top(self):
        """Moves the current item to the top of the list."""
        list, index = self.get_info()
        self.value = [list[index]] + list[:index] + list[index + 1 :]
        wx.CallAfter(self.update_editor)

    def move_bottom(self):
        """Moves the current item to the bottom of the list."""
        list, index = self.get_info()
        self.value = list[:index] + list[index + 1 :] + [list[index]]
        wx.CallAfter(self.update_editor)

    # -- Property Implementations ---------------------------------------------

    @cached_property
    def _get_bitmap(self):
        return convert_bitmap(self.image)

    # -- Private Methods ------------------------------------------------------

    def _dispose_items(self):
        """Disposes of each current list item."""
        for control in self.control.GetChildren():
            editor = getattr(control, "_editor", None)
            if editor is not None:
                try:
                    editor.dispose()
                except Exception:
                    pass
                editor.control = None

    # -- Trait initializers ----------------------------------------------------

    def _kind_default(self):
        """Returns a default value for the 'kind' trait."""
        return self.factory.style + "_editor"

    def _mutable_default(self):
        """Trait handler to set the mutable trait from the factory."""
        return self.factory.mutable


class CustomEditor(SimpleEditor):
    """Custom style of editor for lists, which displays the items as a series
    of text fields. If the list is editable, an icon next to each item displays
    a menu of operations on the list.
    """

    # -------------------------------------------------------------------------
    #  Class constants:
    # -------------------------------------------------------------------------

    #: Whether the list is displayed in a single row. This value overrides the
    #: default.
    single_row = False

    # -------------------------------------------------------------------------
    #  Trait definitions:
    # -------------------------------------------------------------------------

    #: Is the list editor is scrollable? This values overrides the default.
    scrollable = True


# -------------------------------------------------------------------------
#  'TextEditor' class:
# -------------------------------------------------------------------------


class TextEditor(CustomEditor):

    #: The kind of editor to create for each list item. This value overrides the
    #: default.
    kind = "text_editor"


class ReadonlyEditor(CustomEditor):

    #: Is the list of items being edited mutable? This value overrides the
    #: default.
    mutable = False


class NotebookEditor(Editor):
    """An editor for lists that displays the list as a "notebook" of tabbed
    pages.
    """

    # -------------------------------------------------------------------------
    #  Trait definitions:
    # -------------------------------------------------------------------------

    #: Is the notebook editor scrollable? This values overrides the default:
    scrollable = True

    #: The currently selected notebook page object:
    selected = Any()

    def init(self, parent):
        """Finishes initializing the editor by creating the underlying toolkit
        widget.
        """
        self._uis = []

        # Create a DockWindow to hold each separate object's view:
        theme = self.factory.dock_theme or self.item.container.dock_theme
        dw = DockWindow(parent, theme=theme)
        self.control = dw.control
        self._sizer = DockSizer(DockSection(dock_window=dw))
        self.control.SetSizer(self._sizer)

        # Set up the additional 'list items changed' event handler needed for
        # a list based trait. Note that we want to fire the update_editor_item
        # only when the items in the list change and not when intermediate
        # traits change. Therefore, replace "." by ":" in the extended_name
        # when setting up the listener.
        extended_name = self.extended_name.replace(".", ":")
        self.context_object.on_trait_change(
            self.update_editor_item, extended_name + "_items?", dispatch="ui"
        )

        # Set of selection synchronization:
        self.sync_value(self.factory.selected, "selected")

    def update_editor(self):
        """Updates the editor when the object trait changes externally to the
        editor.
        """
        # Make sure the DockWindow is in a correct state:
        self._sizer.Reset(self.control)

        # Destroy the views on each current notebook page:
        self.close_all()

        # Create a DockControl for each object in the trait's value:
        uis = self._uis
        dock_controls = []
        for object in self.value:
            dock_control, view_object, monitoring = self._create_page(object)
            # Remember the DockControl for later deletion processing:
            uis.append([dock_control, object, view_object, monitoring])
            dock_controls.append(dock_control)
            if len(uis) == 1:
                dock_control.dockable.dockable_tab_activated(dock_control, True)

        # Add the new items to the DockWindow:
        self.add_controls(dock_controls)

        if self.ui.info.initialized:
            self.update_layout()

    def update_editor_item(self, event):
        """Handles an update to some subset of the trait's list."""
        # Make sure the DockWindow is in a correct state:
        self._sizer.Reset(self.control)

        index = event.index

        # Delete the page corresponding to each removed item:
        layout = (len(event.removed) + len(event.added)) <= 1
        for i in range(len(event.removed)):
            dock_control, object, view_object, monitoring = self._uis[index]
            if monitoring:
                view_object.on_trait_change(
                    self.update_page_name,
                    self.factory.page_name[1:],
                    remove=True,
                )
            dock_control.close(layout=layout, force=True)
            del self._uis[index]

        # Add a page for each added object:
        dock_controls = []
        for object in event.added:
            dock_control, view_object, monitoring = self._create_page(object)
            self._uis[index:index] = [
                [dock_control, object, view_object, monitoring]
            ]
            dock_controls.append(dock_control)
            index += 1

        # Add the new items to the DockWindow:
        self.add_controls(dock_controls)

        self.update_layout()

    def close_all(self):
        """Closes all currently open notebook pages."""
        page_name = self.factory.page_name[1:]
        for dock_control, object, view_object, monitoring in self._uis:
            if monitoring:
                view_object.on_trait_change(
                    self.update_page_name, page_name, remove=True
                )
            dock_control.close(layout=False, force=True)

        # Reset the list of ui's and dictionary of page name counts:
        self._uis = []
        self._pages = {}

    def dispose(self):
        """Disposes of the contents of an editor."""
        self.context_object.on_trait_change(
            self.update_editor_item, self.name + "_items?", remove=True
        )
        self.close_all()

        super().dispose()

    def add_controls(self, controls):
        """Adds a group of new DockControls to the view."""
        if len(controls) > 0:
            section = self.control.GetSizer().GetContents()
            if (len(section.contents) == 0) or (
                not isinstance(section.contents[-1], DockRegion)
            ):
                section.contents.append(DockRegion(contents=controls))
            else:
                for control in controls:
                    section.contents[-1].add(control, activate=False)
            # Fire this event to activate the dock control corresponding
            # to the selected object, if any.
            self._selected_changed(None, self.selected)

    def update_layout(self):
        """Updates the layout of the DockWindow."""
        self.control.Layout()
        self.control.Refresh()

    def update_page_name(self):
        """Handles the trait defining a particular page's name being changed."""
        changed = False
        for i, value in enumerate(self._uis):
            dock_control, user_object, view_object, monitoring = value
            if dock_control.control is not None:
                name = None
                handler = getattr(
                    self.ui.handler,
                    "%s_%s_page_name" % (self.object_name, self.name),
                    None,
                )
                if handler is not None:
                    name = handler(self.ui.info, user_object)

                if name is None:
                    name = str(
                        xgetattr(
                            view_object, self.factory.page_name[1:], "???"
                        )
                    )

                changed |= dock_control.name != name
                dock_control.name = name

        if changed:
            self.update_layout()

    def _create_page(self, object):
        """Creates a DockControl for a specified object."""
        # Create the view for the object:
        view_object = object
        factory = self.factory
        if factory.factory is not None:
            view_object = factory.factory(object)

        ui = view_object.edit_traits(
            parent=self.control, view=factory.view, kind=factory.ui_kind
        ).trait_set(parent=self.ui)

        # Get the name of the page being added to the notebook:
        name = ""
        monitoring = False
        prefix = "%s_%s_page_" % (self.object_name, self.name)
        page_name = self.factory.page_name
        if page_name[0:1] == ".":
            name = xgetattr(view_object, page_name[1:], None)
            monitoring = name is not None
            if monitoring:
                handler_name = None
                method = getattr(self.ui.handler, prefix + "name", None)
                if method is not None:
                    handler_name = method(self.ui.info, object)
                if handler_name is not None:
                    name = handler_name
                else:
                    name = str(name) or "???"
                view_object.on_trait_change(
                    self.update_page_name, page_name[1:], dispatch="ui"
                )
            else:
                name = ""
        elif page_name != "":
            name = page_name

        if name == "":
            name = user_name_for(view_object.__class__.__name__)

        # Make sure the name is not a duplicate:
        if not monitoring:
            self._pages[name] = count = self._pages.get(name, 0) + 1
            if count > 1:
                name += " %d" % count

        # Return a new DockControl for the ui, and whether or not its name is
        # being monitored:
        image = None
        method = getattr(self.ui.handler, prefix + "image", None)
        if method is not None:
            image = method(self.ui.info, object)
        dock_control = DockControl(
            control=ui.control,
            id=str(id(ui.control)),
            name=name,
            style=factory.dock_style,
            image=image,
            export=factory.export,
            closeable=factory.deletable,
            dockable=DockableListElement(ui=ui, editor=self),
        )
        return (dock_control, view_object, monitoring)

    # -------------------------------------------------------------------------
    #  Activates the corresponding dock window when the 'selected' trait of
    #  the editor is changed.
    # -------------------------------------------------------------------------
    def _selected_changed(self, old, new):
        """Activates the corresponding dock window when the 'selected' trait
        of the editor is changed.
        """
        for i, value in enumerate(self._uis):
            if new == value[1]:
                value[0].activate()
                break
        return


class DockableListElement(DockableViewElement):

    # -------------------------------------------------------------------------
    #  Trait definitions:
    # -------------------------------------------------------------------------

    #: The editor this dockable item is associated with:
    editor = Instance(NotebookEditor)

    def dockable_close(self, dock_control, force):
        """Returns whether it is OK to close the control."""
        return self.close_dock_control(dock_control, force)

    def close_dock_control(self, dock_control, abort):
        """Closes a DockControl."""
        if abort:
            return super().close_dock_control(dock_control, False)

        view_object = self.ui.context["object"]
        for i, value in enumerate(self.editor._uis):
            if view_object is value[2]:
                del self.editor.value[i]

        return False

    def dockable_tab_activated(self, dock_control, activated):
        """Handles a notebook tab being activated or deactivated.
        Sets the value of the editor's selected trait to the activated
        dock_control's object.

        """
        for i, value in enumerate(self.editor._uis):
            if dock_control is value[0] and activated:
                self.editor.selected = value[1]
                break
