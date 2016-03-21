#------------------------------------------------------------------------------
# Copyright (c) 2007, Riverbank Computing Limited
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD license.
# However, when used with the GPL version of PyQt the additional terms described
# in the PyQt GPL exception also apply

#
# Author: Riverbank Computing Limited
#------------------------------------------------------------------------------

""" Defines the various list editors for the PyQt user interface toolkit.
"""

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from pyface.qt import QtCore, QtGui

from pyface.api import ImageResource

from traits.api import Str, Any, Bool, Dict, Instance
from traits.trait_base import user_name_for, xgetattr

# FIXME: ToolkitEditorFactory is a proxy class defined here just for backward
# compatibility. The class has been moved to the
# traitsui.editors.list_editor file.
from traitsui.editors.list_editor import ListItemProxy, \
    ToolkitEditorFactory

from editor import Editor
from helper import IconButton
from menu import MakeMenu

#-------------------------------------------------------------------------------
#  'SimpleEditor' class:
#-------------------------------------------------------------------------------

class SimpleEditor ( Editor ):
    """ Simple style of editor for lists, which displays a scrolling list box
    with only one item visible at a time. A icon next to the list box displays
    a menu of operations on the list.
    """

    #---------------------------------------------------------------------------
    #  Trait definitions:
    #---------------------------------------------------------------------------

    # The kind of editor to create for each list item
    kind = Str

    # Is the list of items being edited mutable?
    mutable = Bool( True )

    # Signal mapper allowing to identify which icon button requested a context
    # menu
    mapper = Instance(QtCore.QSignalMapper)

    #---------------------------------------------------------------------------
    #  Class constants:
    #---------------------------------------------------------------------------

    # Whether the list is displayed in a single row
    single_row = True

    #---------------------------------------------------------------------------
    #  Normal list item menu:
    #---------------------------------------------------------------------------

    # Menu for modifying the list
    list_menu = """
       Add &Before     [_menu_before]: self.add_before()
       Add &After      [_menu_after]:  self.add_after()
       ---
       &Delete         [_menu_delete]: self.delete_item()
       ---
       Move &Up        [_menu_up]:     self.move_up()
       Move &Down      [_menu_down]:   self.move_down()
       Move to &Top    [_menu_top]:    self.move_top()
       Move to &Bottom [_menu_bottom]: self.move_bottom()
    """

    #---------------------------------------------------------------------------
    #  Empty list item menu:
    #---------------------------------------------------------------------------

    empty_list_menu = """
       Add: self.add_empty()
    """

    #---------------------------------------------------------------------------
    #  Finishes initializing the editor by creating the underlying toolkit
    #  widget:
    #---------------------------------------------------------------------------

    def init ( self, parent ):
        """ Finishes initializing the editor by creating the underlying toolkit
            widget.
        """
        # Initialize the trait handler to use:
        trait_handler = self.factory.trait_handler
        if trait_handler is None:
            trait_handler = self.object.base_trait( self.name ).handler
        self._trait_handler = trait_handler

        # Create a scrolled window to hold all of the list item controls:
        self.control = QtGui.QScrollArea()
        self.control.setFrameShape(QtGui.QFrame.NoFrame)
        self.control.setWidgetResizable(True)

        #Create a mapper to identify which icon button requested a contextmenu
        self.mapper = QtCore.QSignalMapper(self.control)

        # Create a widget with a grid layout as the container.
        self._list_pane = QtGui.QWidget()
        self._list_pane.setSizePolicy(QtGui.QSizePolicy.Expanding,
                                      QtGui.QSizePolicy.Expanding)
        layout = QtGui.QGridLayout(self._list_pane)
        layout.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignTop)
        layout.setContentsMargins(0, 0, 0, 0)

        # Remember the editor to use for each individual list item:
        editor = self.factory.editor
        if editor is None:
            editor = trait_handler.item_trait.get_editor()
        self._editor = getattr( editor, self.kind )

        # Set up the additional 'list items changed' event handler needed for
        # a list based trait. Note that we want to fire the update_editor_item
        # only when the items in the list change and not when intermediate
        # traits change. Therefore, replace "." by ":" in the extended_name
        # when setting up the listener.
        extended_name = self.extended_name.replace('.', ':')
        self.context_object.on_trait_change( self.update_editor_item,
                               extended_name + '_items?', dispatch = 'ui' )
        self.set_tooltip()

    #---------------------------------------------------------------------------
    #  Disposes of the contents of an editor:
    #---------------------------------------------------------------------------

    def dispose ( self ):
        """ Disposes of the contents of an editor.
        """
        self._dispose_items()

        extended_name = self.extended_name.replace('.', ':')
        self.context_object.on_trait_change( self.update_editor_item,
                                 extended_name + '_items?', remove = True )

        super( SimpleEditor, self ).dispose()

    #---------------------------------------------------------------------------
    #  Updates the editor when the object trait changes external to the editor:
    #---------------------------------------------------------------------------

    def update_editor ( self ):
        """ Updates the editor when the object trait changes externally to the
            editor.
        """
        self.mapper = QtCore.QSignalMapper(self.control)
        # Disconnect the editor from any control about to be destroyed:
        self._dispose_items()

        list_pane = self._list_pane
        layout = list_pane.layout()

        # Create all of the list item trait editors:
        trait_handler = self._trait_handler
        resizable     = ((trait_handler.minlen != trait_handler.maxlen) and
                         self.mutable)
        item_trait    = trait_handler.item_trait

        is_fake = (resizable and (len( self.value ) == 0))
        if is_fake:
            self.empty_list()
        else:
            # Asking the mapper to send the sender to the callback method
            self.mapper.mapped[QtCore.QObject].connect(self.popup_menu)

        editor = self._editor
        for index, value in enumerate(self.value):
            row, column = divmod(index, self.factory.columns)

            # Account for the fact that we have <columns> number of
            # pairs
            column = column * 2

            if resizable:
                # Connecting the new button to the mapper
                control = IconButton('list_editor.png', self.mapper.map)
                # Setting the mapping and asking it to send the index of the
                # sender to the callback method
                self.mapper.setMapping(control, control)

                layout.addWidget(control, row, column)

            proxy = ListItemProxy( self.object, self.name, index, item_trait,
                                   value )
            if resizable:
                control.proxy = proxy
            peditor = editor( self.ui, proxy, 'value', self.description,
                              list_pane ).set( object_name = '' )
            peditor.prepare( list_pane )
            pcontrol = peditor.control
            pcontrol.proxy = proxy

            if isinstance(pcontrol, QtGui.QWidget):
                layout.addWidget(pcontrol, row, column+1)
            else:
                layout.addLayout(pcontrol, row, column+1)

        # QScrollArea can have problems if the widget being scrolled is set too
        # early (ie. before it contains something).
        if self.control.widget() is None:
            self.control.setWidget(list_pane)

    #---------------------------------------------------------------------------
    #  Updates the editor when an item in the object trait changes external to
    #  the editor:
    #---------------------------------------------------------------------------

    def update_editor_item ( self, event ):
        """ Updates the editor when an item in the object trait changes
        externally to the editor.
        """
        # If this is not a simple, single item update, rebuild entire editor:
        if (len( event.removed ) != 1) or (len( event.added ) != 1):
            self.update_editor()
            return

        # Otherwise, find the proxy for this index and update it with the
        # changed value:
        for control in self.control.widget().children():
            if isinstance(control, QtGui.QLayout):
                continue

            proxy = control.proxy
            if proxy.index == event.index:
                proxy.value = event.added[0]
                break

    #---------------------------------------------------------------------------
    #  Creates an empty list entry (so the user can add a new item):
    #---------------------------------------------------------------------------

    def empty_list ( self ):
        """ Creates an empty list entry (so the user can add a new item).
        """
        # Connecting the new button to the mapper
        control = IconButton('list_editor.png', self.mapper.map)
        # Setting the mapping and asking it to send the sender to the
        # callback method
        self.mapper.setMapping(control, control)
        self.mapper.mapped[QtCore.QObject].connect(self.popup_empty_menu)
        control.is_empty = True
        self._cur_control = control

        proxy    = ListItemProxy( self.object, self.name, -1, None, None )
        pcontrol = QtGui.QLabel('   (Empty List)')
        pcontrol.proxy = control.proxy = proxy

        layout = self._list_pane.layout()
        layout.addWidget(control, 0, 0)
        layout.addWidget(pcontrol, 0, 1)

    #---------------------------------------------------------------------------
    #  Returns the associated object list and current item index:
    #---------------------------------------------------------------------------

    def get_info ( self ):
        """ Returns the associated object list and current item index.
        """
        proxy = self._cur_control.proxy
        return ( proxy.list, proxy.index )

    #---------------------------------------------------------------------------
    #  Displays the empty list editor popup menu:
    #---------------------------------------------------------------------------

    def popup_empty_menu ( self , sender):
        """ Displays the empty list editor popup menu.
        """
        self._cur_control = control = sender
        menu = MakeMenu( self.empty_list_menu, self, True, control ).menu
        menu.exec_(control.mapToGlobal(QtCore.QPoint(0, 0)))

    #---------------------------------------------------------------------------
    #  Displays the list editor popup menu:
    #---------------------------------------------------------------------------

    def popup_menu ( self , sender):
        """ Displays the list editor popup menu.
        """
        self._cur_control = sender

        proxy    = sender.proxy
        index    = proxy.index
        menu     = MakeMenu( self.list_menu, self, True, sender ).menu
        len_list = len( proxy.list )
        not_full = (len_list < self._trait_handler.maxlen)

        self._menu_before.enabled( not_full )
        self._menu_after.enabled(  not_full )
        self._menu_delete.enabled( len_list > self._trait_handler.minlen )
        self._menu_up.enabled(  index > 0 )
        self._menu_top.enabled( index > 0 )
        self._menu_down.enabled(   index < (len_list - 1) )
        self._menu_bottom.enabled( index < (len_list - 1) )

        menu.exec_(sender.mapToGlobal(QtCore.QPoint(0, 0)))

    #---------------------------------------------------------------------------
    #  Adds a new value at the specified list index:
    #---------------------------------------------------------------------------

    def add_item ( self, offset ):
        """ Adds a new value at the specified list index.
        """
        list, index = self.get_info()
        index      += offset
        item_trait  = self._trait_handler.item_trait
        value       = item_trait.default_value_for( self.object, self.name )
        self.value = list[:index] + [ value ] + list[index:]
        self.update_editor()

    #---------------------------------------------------------------------------
    #  Inserts a new item before the current item:
    #---------------------------------------------------------------------------

    def add_before ( self ):
        """ Inserts a new item before the current item.
        """
        self.add_item( 0 )

    #---------------------------------------------------------------------------
    #  Inserts a new item after the current item:
    #---------------------------------------------------------------------------

    def add_after ( self ):
        """ Inserts a new item after the current item.
        """
        self.add_item( 1 )

    #---------------------------------------------------------------------------
    #  Adds a new item when the list is empty:
    #---------------------------------------------------------------------------

    def add_empty ( self ):
        """ Adds a new item when the list is empty.
        """
        list, index = self.get_info()
        self.add_item( 0 )

    #---------------------------------------------------------------------------
    #  Delete the current item:
    #---------------------------------------------------------------------------

    def delete_item ( self ):
        """ Delete the current item.
        """
        list, index = self.get_info()
        self.value  = list[:index] + list[index+1:]
        self.update_editor()

    #---------------------------------------------------------------------------
    #  Move the current item up one in the list:
    #---------------------------------------------------------------------------

    def move_up ( self ):
        """ Move the current item up one in the list.
        """
        list, index = self.get_info()
        self.value  = (list[:index-1] + [ list[index], list[index-1] ] +
                       list[index+1:])
        self.update_editor()

    #---------------------------------------------------------------------------
    #  Moves the current item down one in the list:
    #---------------------------------------------------------------------------

    def move_down ( self ):
        """ Moves the current item down one in the list.
        """
        list, index = self.get_info()
        self.value  = (list[:index] + [ list[index+1], list[index] ] +
                       list[index+2:])
        self.update_editor()

    #---------------------------------------------------------------------------
    #  Moves the current item to the top of the list:
    #---------------------------------------------------------------------------

    def move_top ( self ):
        """ Moves the current item to the top of the list.
        """
        list, index = self.get_info()
        self.value  = [ list[index] ] + list[:index] + list[index+1:]
        self.update_editor()

    #---------------------------------------------------------------------------
    #  Moves the current item to the bottom of the list:
    #---------------------------------------------------------------------------

    def move_bottom ( self ):
        """ Moves the current item to the bottom of the list.
        """
        list, index = self.get_info()
        self.value  = list[:index] + list[index+1:] + [ list[index] ]
        self.update_editor()

    #-- Private Methods --------------------------------------------------------

    def _dispose_items ( self ):
        """ Disposes of each current list item.
        """
        layout = self._list_pane.layout()
        child = layout.takeAt(0)
        while child is not None:
            control = child.widget()
            if control is not None:
                editor = getattr( control, '_editor', None )
                if editor is not None:
                    editor.dispose()
                    editor.control = None
                control.deleteLater()
            child = layout.takeAt(0)
        del child

    #-- Trait initializers ----------------------------------------------------

    def _kind_default(self):
        """ Returns a default value for the 'kind' trait.
        """
        return self.factory.style + '_editor'

    def _mutable_default(self):
        """ Trait handler to set the mutable trait from the factory.
        """
        return self.factory.mutable

#-------------------------------------------------------------------------------
#  'CustomEditor' class:
#-------------------------------------------------------------------------------

class CustomEditor ( SimpleEditor ):
    """ Custom style of editor for lists, which displays the items as a series
    of text fields. If the list is editable, an icon next to each item displays
    a menu of operations on the list.
    """

    #---------------------------------------------------------------------------
    #  Class constants:
    #---------------------------------------------------------------------------

    # Whether the list is displayed in a single row. This value overrides the
    # default.
    single_row = False

    #---------------------------------------------------------------------------
    #  Trait definitions:
    #---------------------------------------------------------------------------

    # Is the list editor is scrollable? This values overrides the default.
    scrollable = True

#-------------------------------------------------------------------------------
#  'TextEditor' class:
#-------------------------------------------------------------------------------

class TextEditor(CustomEditor):

    # The kind of editor to create for each list item. This value overrides the
    # default.
    kind = 'text_editor'

#-------------------------------------------------------------------------------
#  'ReadonlyEditor' class:
#-------------------------------------------------------------------------------

class ReadonlyEditor(CustomEditor):

    # Is the list of items being edited mutable? This value overrides the
    # default.
    mutable = False

#-------------------------------------------------------------------------------
#  'NotebookEditor' class:
#-------------------------------------------------------------------------------

class NotebookEditor ( Editor ):
    """ An editor for lists that displays the list as a "notebook" of tabbed
    pages.
    """

    # The "Close Tab" button.
    close_button = Any()

    # Maps tab names to QWidgets representing the tab contents
    # TODO: It would be nice to be able to reuse self._pages for this, but
    # its keys are not quite what we want.
    _pagewidgets = Dict

    # Maps names of tabs to their menu QAction instances; used to toggle
    # checkboxes
    _action_dict = Dict


    #---------------------------------------------------------------------------
    #  Trait definitions:
    #---------------------------------------------------------------------------

    # Is the notebook editor scrollable? This values overrides the default:
    scrollable = True

    # The currently selected notebook page object:
    selected = Any

    #---------------------------------------------------------------------------
    #  Finishes initializing the editor by creating the underlying toolkit
    #  widget:
    #---------------------------------------------------------------------------

    def init ( self, parent ):
        """ Finishes initializing the editor by creating the underlying toolkit
            widget.
        """
        self._uis = []

        # Create a tab widget to hold each separate object's view:
        self.control = QtGui.QTabWidget()
        signal = QtCore.SIGNAL( 'currentChanged(int)' )
        QtCore.QObject.connect( self.control, signal, self._tab_activated )

        # minimal dock_style handling
        if self.factory.dock_style == 'tab':
            self.control.setDocumentMode(True)
            self.control.tabBar().setDocumentMode(True)
        elif self.factory.dock_style == 'vertical':
            self.control.setTabPosition(QtGui.QTabWidget.West)

        # Create the button to close tabs, if necessary:
        if self.factory.deletable:
            button = QtGui.QToolButton()
            button.setAutoRaise( True )
            button.setToolTip( 'Remove current tab ')
            button.setIcon ( ImageResource( 'closetab' ).create_icon() )

            self.control.setCornerWidget( button, QtCore.Qt.TopRightCorner )
            signal = QtCore.SIGNAL( 'clicked()' )
            QtCore.QObject.connect( button, signal, self.close_current )
            self.close_button = button

        if self.factory.show_notebook_menu:
            # Create the necessary attributes to manage hiding and revealing of
            # tabs via a context menu
            self._context_menu = QtGui.QMenu()
            self.control.customContextMenuRequested.connect(self._context_menu_requested)
            self.control.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)

        # Set up the additional 'list items changed' event handler needed for
        # a list based trait. Note that we want to fire the update_editor_item
        # only when the items in the list change and not when intermediate
        # traits change. Therefore, replace "." by ":" in the extended_name
        # when setting up the listener.
        extended_name = self.extended_name.replace('.', ':')
        self.context_object.on_trait_change( self.update_editor_item,
                               extended_name + '_items?', dispatch = 'ui' )

        # Set of selection synchronization:
        self.sync_value( self.factory.selected, 'selected' )

    #---------------------------------------------------------------------------
    #  Updates the editor when the object trait changes external to the editor:
    #---------------------------------------------------------------------------

    def update_editor ( self ):
        """ Updates the editor when the object trait changes externally to the
            editor.
        """
        # Destroy the views on each current notebook page:
        self.close_all()

        # Create a tab page for each object in the trait's value:
        for object in self.value:
            ui, view_object, monitoring = self._create_page(object)

            # Remember the page for later deletion processing:
            self._uis.append([ui.control, ui, view_object, monitoring])

        if self.selected:
            self._selected_changed(self.selected)

    #---------------------------------------------------------------------------
    #  Handles some subset of the trait's list being updated:
    #---------------------------------------------------------------------------

    def update_editor_item ( self, event ):
        """ Handles an update to some subset of the trait's list.
        """
        index = event.index

        # Delete the page corresponding to each removed item:
        page_name = self.factory.page_name[1:]

        for i in event.removed:
            page, ui, view_object, monitoring = self._uis[index]
            if monitoring:
                view_object.on_trait_change(self.update_page_name, page_name,
                        remove=True)
            ui.dispose()
            self.control.removeTab(self.control.indexOf(page))

            if self.factory.show_notebook_menu:
                for name, tmp in self._pagewidgets.items():
                    if tmp is page:
                        del self._pagewidgets[name]
                self._context_menu.removeAction(self._action_dict[name])
                del self._action_dict[name]

            del self._uis[index]

        # Add a page for each added object:
        first_page = None
        for object in event.added:
            ui, view_object, monitoring  = self._create_page(object)
            self._uis[index:index] = [[ui.control, ui, view_object, monitoring]]
            index += 1

            if first_page is None:
                first_page = ui.control

        if first_page is not None:
            self.control.setCurrentWidget(first_page)

    #---------------------------------------------------------------------------
    #  Closes the currently selected tab:
    #---------------------------------------------------------------------------

    def close_current ( self, force=False ):
        """ Closes the currently selected tab:
        """
        widget = self.control.currentWidget()
        for i in xrange( len( self._uis ) ):
            page, ui, _, _ = self._uis[i]
            if page is widget:
                if force or ui.handler.close( ui.info, True ):
                    del self.value[i]
                break

        if self.factory.show_notebook_menu:
            # Find the name associated with this widget, so we can purge its action
            # from the menu
            for name, tmp in self._pagewidgets.items():
                if tmp is widget:
                    break
            else:
                # Hmm... couldn't find the widget, assume that we don't need to do
                # anything.
                return

            action = self._action_dict[name]
            self._context_menu.removeAction(action)
            del self._action_dict[name]
            del self._pagewidgets[name]
        return

    #---------------------------------------------------------------------------
    #  Closes all currently open notebook pages:
    #---------------------------------------------------------------------------

    def close_all ( self ):
        """ Closes all currently open notebook pages.
        """
        page_name = self.factory.page_name[1:]

        for _, ui, view_object, monitoring in self._uis:
            if monitoring:
                view_object.on_trait_change(self.update_page_name, page_name,
                        remove=True)
            ui.dispose()

        # Reset the list of ui's and dictionary of page name counts:
        self._uis = []
        self._pages = {}

        self.control.clear()

    #---------------------------------------------------------------------------
    #  Disposes of the contents of an editor:
    #---------------------------------------------------------------------------

    def dispose ( self ):
        """ Disposes of the contents of an editor.
        """
        self.context_object.on_trait_change( self.update_editor_item,
                                self.name + '_items?', remove = True )
        self.close_all()

        super( NotebookEditor, self ).dispose()

    #---------------------------------------------------------------------------
    #  Handles the trait defining a particular page's name being changed:
    #---------------------------------------------------------------------------

    def update_page_name ( self, object, name, old, new ):
        """ Handles the trait defining a particular page's name being changed.
        """
        for i, value in enumerate(self._uis):
            page, ui, _, _ = value
            if object is ui.info.object:
                name = None
                handler = getattr(self.ui.handler,
                        '%s_%s_page_name' % (self.object_name, self.name),
                        None)

                if handler is not None:
                    name = handler(self.ui.info, object)

                if name is None:
                    name = str(xgetattr(object, self.factory.page_name[1:], '???'))
                self.control.setTabText(self.control.indexOf(page), name)
                break

    #---------------------------------------------------------------------------
    #  Creates a page for a specified object and adds it to the tab widget:
    #---------------------------------------------------------------------------

    def _create_page ( self, object ):
        # Create the view for the object:
        view_object = object
        factory = self.factory
        if factory.factory is not None:
            view_object = factory.factory(object)
        ui = view_object.edit_traits( parent = self.control,
                                 view   = factory.view,
                                 kind   = factory.ui_kind ).set(
                                 parent = self.ui )

        # Get the name of the page being added to the notebook:
        name       = ''
        monitoring = False
        prefix     = '%s_%s_page_' % ( self.object_name, self.name )
        page_name  = factory.page_name
        if page_name[0:1] == '.':
            name       = xgetattr( view_object, page_name[1:], None )
            monitoring = (name is not None)
            if monitoring:
                handler_name = None
                method       = getattr( self.ui.handler, prefix + 'name', None )
                if method is not None:
                    handler_name = method( self.ui.info, object )
                if handler_name is not None:
                    name = handler_name
                else:
                    name = str( name ) or '???'
                view_object.on_trait_change( self.update_page_name,
                                        page_name[1:], dispatch = 'ui' )
            else:
                name = ''
        elif page_name != '':
            name = page_name

        if name == '':
            name = user_name_for( view_object.__class__.__name__ )

        # Make sure the name is not a duplicate:
        if not monitoring:
            self._pages[ name ] = count = self._pages.get( name, 0 ) + 1
            if count > 1:
                name += (' %d' % count)

        # Return the control for the ui, and whether or not its name is being
        # monitored:
        image   = None
        method  = getattr( self.ui.handler, prefix + 'image', None )
        if method is not None:
            image = method( self.ui.info, object )

        if image is None:
            self.control.addTab(ui.control, name)
        else:
            self.control.addTab(ui.control, image, name)

        if self.factory.show_notebook_menu:
            newaction = self._context_menu.addAction(name)
            newaction.setText(name)
            newaction.setCheckable(True)
            newaction.setChecked(True)
            newaction.triggered.connect(lambda e,name=name: self._menu_action(e,name=name))
            self._action_dict[name] = newaction
            self._pagewidgets[name] = ui.control

        return (ui, view_object, monitoring)

    def _tab_activated(self, idx):
        """ Handles a notebook tab being "activated" (i.e. clicked on) by the
            user.
        """
        widget = self.control.widget(idx)
        for page, ui, _, _ in self._uis:
            if page is widget:
                self.selected = ui.info.object
                break

    def _selected_changed(self, selected):
        """ Handles the **selected** trait being changed.
        """
        for page, ui, _, _ in self._uis:
            if ui.info and selected is ui.info.object:
                self.control.setCurrentWidget(page)
                break
            deletable = self.factory.deletable
            deletable_trait = self.factory.deletable_trait
            if deletable and deletable_trait:
                enabled = xgetattr(selected, deletable_trait, True)
                self.close_button.setEnabled(enabled)

    def _context_menu_requested(self, event):
        self._context_menu.popup(self.control.mapToGlobal(event))

    def _menu_action(self, event, name=""):
        """ Qt signal handler for when a item in a context menu is actually
        selected.  Not that we get this even after the underlying value has
        already changed.
        """
        action = self._action_dict[name]
        checked = action.isChecked()
        if not checked:
            for ndx in range(self.control.count()):
                if self.control.tabText(ndx) == name:
                    self.control.removeTab(ndx)
        else:
            # TODO: Fix tab order based on the context_object's list
            self.control.addTab(self._pagewidgets[name], name)

    def _context_menu_requested(self, event):
        self._context_menu.popup(self.control.mapToGlobal(event))

    def _menu_action(self, event, name=""):
        """ Qt signal handler for when a item in a context menu is actually
        selected.  Not that we get this even after the underlying value has
        already changed.
        """
        action = self._action_dict[name]
        checked = action.isChecked()
        if not checked:
            for ndx in range(self.control.count()):
                if self.control.tabText(ndx) == name:
                    self.control.removeTab(ndx)
        else:
            # TODO: Fix tab order based on the context_object's list
            self.control.addTab(self._pagewidgets[name], name)
