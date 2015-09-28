#------------------------------------------------------------------------------
# Copyright (c) 2008, Riverbank Computing Limited
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD license.
# However, when used with the GPL version of PyQt the additional terms described in the PyQt GPL exception also apply

#
# Author: Riverbank Computing Limited
#------------------------------------------------------------------------------

""" Defines the various instance editors and the instance editor factory for
    the PyQt user interface toolkit..
"""

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from pyface.qt import QtCore, QtGui

from traits.api \
    import HasTraits, Property

# FIXME: ToolkitEditorFactory is a proxy class defined here just for backward
# compatibility. The class has been moved to the
# traitsui.editors.instance_editor file.
from traitsui.editors.instance_editor \
    import ToolkitEditorFactory

from traitsui.ui_traits \
    import AView

from traitsui.helper \
    import user_name_for

from traitsui.handler \
    import Handler

from traitsui.instance_choice \
    import InstanceChoiceItem

from editor \
    import Editor

from constants \
    import DropColor

from helper \
    import position_window

#-------------------------------------------------------------------------------
#  Constants:
#-------------------------------------------------------------------------------

OrientationMap = {
    'default':    None,
    'horizontal': QtGui.QBoxLayout.LeftToRight,
    'vertical':   QtGui.QBoxLayout.TopToBottom
}

#-------------------------------------------------------------------------------
#  'CustomEditor' class:
#-------------------------------------------------------------------------------

class CustomEditor ( Editor ):
    """ Custom style of editor for instances. If selection among instances is
    allowed, the editor displays a combo box listing instances that can be
    selected. If the current instance is editable, the editor displays a panel
    containing trait editors for all the instance's traits.
    """

    # Background color when an item can be dropped on the editor:
    ok_color = DropColor

    # The orientation of the instance editor relative to the instance selector:
    orientation = QtGui.QBoxLayout.TopToBottom

    # Class constant:
    extra = 0

    #---------------------------------------------------------------------------
    #  Trait definitions:
    #---------------------------------------------------------------------------

    # List of InstanceChoiceItem objects used by the editor
    items = Property

    # The view to use for displaying the instance
    view = AView

    #---------------------------------------------------------------------------
    #  Finishes initializing the editor by creating the underlying toolkit
    #  widget:
    #---------------------------------------------------------------------------

    def init ( self, parent ):
        """ Finishes initializing the editor by creating the underlying toolkit
            widget.
        """
        factory = self.factory
        if factory.name != '':
            self._object, self._name, self._value = \
                self.parse_extended_name( factory.name )

        # Create a panel to hold the object trait's view:
        if factory.editable:
            self.control = self._panel = parent = QtGui.QWidget()

        # Build the instance selector if needed:
        selectable = factory.selectable
        droppable  = factory.droppable
        items      = self.items
        for item in items:
            droppable  |= item.is_droppable()
            selectable |= item.is_selectable()

        if selectable:
            self._object_cache = {}
            item = self.item_for( self.value )
            if item is not None:
                self._object_cache[ id( item ) ] = self.value

            self._choice = QtGui.QComboBox()
            QtCore.QObject.connect(self._choice,
                    QtCore.SIGNAL('activated(QString)'), self.update_object)

            self.set_tooltip( self._choice )

            if factory.name != '':
                self._object.on_trait_change( self.rebuild_items,
                                              self._name, dispatch = 'ui' )
                self._object.on_trait_change( self.rebuild_items,
                                 self._name + '_items', dispatch = 'ui' )

            factory.on_trait_change( self.rebuild_items, 'values',
                                     dispatch = 'ui' )
            factory.on_trait_change( self.rebuild_items, 'values_items',
                                     dispatch = 'ui' )

            self.rebuild_items()

        elif droppable:
            self._choice = QtGui.QLineEdit()
            self._choice.setReadOnly(True)
            self.set_tooltip( self._choice )

        if droppable:
            self._choice.SetDropTarget( PythonDropTarget( self ) )

        orientation = OrientationMap[ factory.orientation ]
        if orientation is None:
            orientation = self.orientation

        if (selectable or droppable) and factory.editable:
            layout = QtGui.QBoxLayout(orientation, parent)
            layout.setContentsMargins(0, 0, 0, 0)
            layout.addWidget(self._choice)

            if orientation == QtGui.QBoxLayout.TopToBottom:
                hline = QtGui.QFrame()
                hline.setFrameShape(QtGui.QFrame.HLine)
                hline.setFrameShadow(QtGui.QFrame.Sunken)

                layout.addWidget(hline)

            self.create_editor(parent, layout)
        elif self.control is None:
            if self._choice is None:
                self._choice = QtGui.QComboBox()
                QtCore.QObject.connect(self._choice,
                        QtCore.SIGNAL('activated(QString)'),
                        self.update_object)

            self.control = self._choice
        else:
            layout = QtGui.QBoxLayout(orientation, parent)
            layout.setContentsMargins(0, 0, 0, 0)
            self.create_editor(parent, layout)

        # Synchronize the 'view' to use:
        # fixme: A normal assignment can cause a crash (for unknown reasons) in
        # some cases, so we make sure that no notifications are generated:
        self.trait_setq( view = factory.view )
        self.sync_value( factory.view_name, 'view', 'from' )

    #---------------------------------------------------------------------------
    #  Creates the editor control:
    #---------------------------------------------------------------------------

    def create_editor(self, parent, layout):
        """ Creates the editor control.
        """
        self._panel = QtGui.QWidget()
        layout.addWidget(self._panel)

    #---------------------------------------------------------------------------
    #  Gets the current list of InstanceChoiceItem items:
    #---------------------------------------------------------------------------

    def _get_items ( self ):
        """ Gets the current list of InstanceChoiceItem items.
        """
        if self._items is not None:
            return self._items

        factory = self.factory
        if self._value is not None:
            values = self._value() + factory.values
        else:
            values = factory.values

        items = []
        adapter = factory.adapter
        for value in values:
            if not isinstance( value, InstanceChoiceItem ):
                value = adapter( object = value )
            items.append( value )

        self._items = items

        return items

    #---------------------------------------------------------------------------
    #  Rebuilds the object selector list:
    #---------------------------------------------------------------------------

    def rebuild_items ( self ):
        """ Rebuilds the object selector list.
        """
        # Clear the current cached values:
        self._items = None

        # Rebuild the contents of the selector list:
        name   = -1
        value  = self.value
        choice = self._choice
        choice.clear()
        for i, item in enumerate(self.items):
            if item.is_selectable():
                choice.addItem(item.get_name())
                if item.is_compatible( value ):
                    name = i

        # Reselect the current item if possible:
        if name >= 0:
            choice.setCurrentIndex(name)
        else:
            # Otherwise, current value is no longer valid, try to discard it:
            try:
                self.value = None
            except:
                pass

    #---------------------------------------------------------------------------
    #  Returns the InstanceChoiceItem for a specified object:
    #---------------------------------------------------------------------------

    def item_for ( self, object ):
        """ Returns the InstanceChoiceItem for a specified object.
        """
        for item in self.items:
            if item.is_compatible( object ):
                return item

        return None

    #---------------------------------------------------------------------------
    #  Returns the view to use for a specified object:
    #---------------------------------------------------------------------------

    def view_for ( self, object, item ):
        """ Returns the view to use for a specified object.
        """
        view = ''
        if item is not None:
            view = item.get_view()

        if view == '':
            view = self.view

        return self.ui.handler.trait_view_for( self.ui.info, view, object,
                                               self.object_name, self.name )

    #---------------------------------------------------------------------------
    #  Handles the user selecting a new value from the combo box:
    #---------------------------------------------------------------------------

    def update_object(self, text):
        """ Handles the user selecting a new value from the combo box.
        """
        name = unicode(text)
        for item in self.items:
            if name == item.get_name():
                id_item = id( item )
                object  = self._object_cache.get( id_item )
                if object is None:
                    object = item.get_object()
                    if (not self.factory.editable) and item.is_factory:
                        view = self.view_for( object, self.item_for( object ) )
                        view.ui( object, self.control, 'modal' )

                    if self.factory.cachable:
                        self._object_cache[ id_item ] = object

                self.value = object
                self.resynch_editor()
                break

    #---------------------------------------------------------------------------
    #  Updates the editor when the object trait changes external to the editor:
    #---------------------------------------------------------------------------

    def update_editor ( self ):
        """ Updates the editor when the object trait changes externally to the
            editor.
        """
        # Synchronize the editor contents:
        self.resynch_editor()

        # Update the selector (if any):
        choice = self._choice
        item   = self.item_for( self.value )
        if (choice is not None) and (item is not None):
            name = item.get_name( self.value )
            if self._object_cache is not None:
                idx = choice.findText(name)
                if idx < 0:
                    idx = choice.count()
                    choice.addItem(name)

                choice.setCurrentIndex(idx)
            else:
                choice.setText(name)

    #---------------------------------------------------------------------------
    #  Resynchronizes the contents of the editor when the object trait changes
    #  external to the editor:
    #---------------------------------------------------------------------------

    def resynch_editor ( self ):
        """ Resynchronizes the contents of the editor when the object trait
        changes externally to the editor.
        """
        panel = self._panel
        if panel is not None:
            # Dispose of the previous contents of the panel:
            layout = panel.layout()
            if layout is None:
                layout = QtGui.QVBoxLayout(panel)
                layout.setContentsMargins(0, 0, 0, 0)
            elif self._ui is not None:
                self._ui.dispose()
                self._ui = None
            else:
                child = layout.takeAt(0)
                while child is not None:
                    child = layout.takeAt(0)

                del child

            # Create the new content for the panel:
            stretch = 0
            value   = self.value
            if not isinstance( value, HasTraits ):
                str_value = ''
                if value is not None:
                    str_value = self.str_value
                control = QtGui.QLabel(str_value)
            else:
                view    = self.view_for( value, self.item_for( value ) )
                context = value.trait_context()
                handler = None
                if isinstance( value, Handler ):
                    handler = value
                context.setdefault( 'context', self.object )
                context.setdefault( 'context_handler', self.ui.handler )
                self._ui = ui = view.ui( context, panel, 'subpanel',
                                         value.trait_view_elements(), handler,
                                         self.factory.id )
                control         = ui.control
                self.scrollable = ui._scrollable
                ui.parent       = self.ui

                if view.resizable or view.scrollable or ui._scrollable:
                    stretch = 1

            # FIXME: Handle stretch.
            layout.addWidget(control)

    #---------------------------------------------------------------------------
    #  Disposes of the contents of an editor:
    #---------------------------------------------------------------------------

    def dispose ( self ):
        """ Disposes of the contents of an editor.
        """
        # Make sure we aren't hanging on to any object refs:
        self._object_cache = None

        if self._ui is not None:
            self._ui.dispose()

        if self._choice is not None:
            if self._object is not None:
                self._object.on_trait_change( self.rebuild_items,
                                              self._name, remove = True )
                self._object.on_trait_change( self.rebuild_items,
                                 self._name + '_items', remove = True )

            self.factory.on_trait_change( self.rebuild_items, 'values',
                                          remove = True )
            self.factory.on_trait_change( self.rebuild_items,
                                          'values_items', remove = True )

        super( CustomEditor, self ).dispose()

    #---------------------------------------------------------------------------
    #  Handles an error that occurs while setting the object's trait value:
    #---------------------------------------------------------------------------

    def error ( self, excp ):
        """ Handles an error that occurs while setting the object's trait value.
        """
        pass

    #---------------------------------------------------------------------------
    #  Returns the editor's control for indicating error status:
    #---------------------------------------------------------------------------

    def get_error_control ( self ):
        """ Returns the editor's control for indicating error status.
        """
        return (self._choice or self.control)

    #-- UI preference save/restore interface -----------------------------------

    #---------------------------------------------------------------------------
    #  Restores any saved user preference information associated with the
    #  editor:
    #---------------------------------------------------------------------------

    def restore_prefs ( self, prefs ):
        """ Restores any saved user preference information associated with the
            editor.
        """
        ui = self._ui
        if (ui is not None) and (prefs.get( 'id' ) == ui.id):
            ui.set_prefs( prefs.get( 'prefs' ) )

    #---------------------------------------------------------------------------
    #  Returns any user preference information associated with the editor:
    #---------------------------------------------------------------------------

    def save_prefs ( self ):
        """ Returns any user preference information associated with the editor.
        """
        ui = self._ui
        if (ui is not None) and (ui.id != ''):
            return { 'id':    ui.id,
                     'prefs': ui.get_prefs() }

        return None

    #-- Traits event handlers --------------------------------------------------

    def _view_changed ( self, view ):
        self.resynch_editor()

#-------------------------------------------------------------------------------
#  'SimpleEditor' class:
#-------------------------------------------------------------------------------

class SimpleEditor ( CustomEditor ):
    """ Simple style of editor for instances, which displays a button. Clicking
    the button displays a dialog box in which the instance can be edited.
    """

    # Class constants:
    orientation = QtGui.QBoxLayout.LeftToRight
    extra       = 2

    #---------------------------------------------------------------------------
    #  Creates the editor control:
    #---------------------------------------------------------------------------

    def create_editor(self, parent, layout):
        """ Creates the editor control (a button).
        """
        self._button = QtGui.QPushButton()
        layout.addWidget(self._button)
        QtCore.QObject.connect(self._button, QtCore.SIGNAL('clicked()'),
                self.edit_instance)

    #---------------------------------------------------------------------------
    #  Edit the contents of the object trait when the user clicks the button:
    #---------------------------------------------------------------------------

    def edit_instance(self):
        """ Edit the contents of the object trait when the user clicks the
            button.
        """
        # Create the user interface:
        factory = self.factory
        view    = self.ui.handler.trait_view_for( self.ui.info, factory.view,
                                                  self.value, self.object_name,
                                                  self.name )
        ui = self.value.edit_traits( view, kind=factory.kind, id=factory.id )

        # Make sure the editor is properly disposed
        QtCore.QObject.connect( self._button, QtCore.SIGNAL( 'destroyed()' ),
                                lambda: ui.dispose() )

        # Check to see if the view was 'modal', in which case it will already
        # have been closed (i.e. is None) by the time we get control back:
        if ui.control is not None:
            # Position the window on the display:
            position_window( ui.control )

            # Chain our undo history to the new user interface if it does not
            # have its own:
            if ui.history is None:
                ui.history = self.ui.history

    #---------------------------------------------------------------------------
    #  Resynchronizes the contents of the editor when the object trait changes
    #  external to the editor:
    #---------------------------------------------------------------------------

    def resynch_editor ( self ):
        """ Resynchronizes the contents of the editor when the object trait
            changes externally to the editor.
        """
        button = self._button
        if button is not None:
            label = self.factory.label
            if label == '':
                label = user_name_for( self.name )

            button.setText(label)
            button.setEnabled(isinstance(self.value, HasTraits))
