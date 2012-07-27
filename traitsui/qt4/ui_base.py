#------------------------------------------------------------------------------
# Copyright (c) 2007, Riverbank Computing Limited
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD license.
# However, when used with the GPL version of PyQt the additional terms described in the PyQt GPL exception also apply

#
# Author: Riverbank Computing Limited
#------------------------------------------------------------------------------

"""Defines the base class for the PyQt-based Traits UI modal and non-modal
   dialogs.
"""


from pyface.qt import QtCore, QtGui

from traits.api \
    import HasStrictTraits, HasPrivateTraits, Instance, List, Event

from traitsui.api \
    import UI

from traitsui.menu \
    import Action

from constants \
    import DefaultTitle

from editor \
    import Editor

from helper \
    import restore_window, save_window


#-------------------------------------------------------------------------------
#  Constants:
#-------------------------------------------------------------------------------

# List of all predefined system button names:
SystemButtons = ['Undo', 'Redo', 'Apply', 'Revert', 'OK', 'Cancel', 'Help']

# List of alternative context items that might handle an Action 'perform':
PerformHandlers = ( 'object', 'model' )

def default_icon():
    from pyface.image_resource import ImageResource
    return ImageResource('frame.png')

#-------------------------------------------------------------------------------
#  'RadioGroup' class:
#-------------------------------------------------------------------------------

class RadioGroup ( HasStrictTraits ):
    """ A group of mutually-exclusive menu or toolbar actions.
    """
    # List of menu or tool bar items
    items = List

    #---------------------------------------------------------------------------
    #  Handles a menu item in the group being checked:
    #---------------------------------------------------------------------------

    def menu_checked ( self, menu_item ):
        """ Handles a menu item in the group being checked.
        """
        for item in self.items:
            if item is not menu_item:
                item.control.Check( False )
                item.item.action.checked = False

    #---------------------------------------------------------------------------
    #  Handles a tool bar item in the group being checked:
    #---------------------------------------------------------------------------

    def toolbar_checked ( self, toolbar_item ):
        """ Handles a tool bar item in the group being checked.
        """
        for item in self.items:
            if item is not toolbar_item:
                item.tool_bar.ToggleTool( item.control_id, False )
                item.item.action.checked = False

#-------------------------------------------------------------------------------
#  'ButtonEditor' class:
#-------------------------------------------------------------------------------

class ButtonEditor(Editor):
    """ Editor for buttons.
    """
    #---------------------------------------------------------------------------
    #  Trait definitions:
    #---------------------------------------------------------------------------

    # Action associated with the button
    action = Instance(Action)

    #---------------------------------------------------------------------------
    #  Initializes the object:
    #---------------------------------------------------------------------------

    def __init__(self, **traits):
        self.set(**traits)

    #---------------------------------------------------------------------------
    #  Handles the associated button being clicked:
    #---------------------------------------------------------------------------

    def perform(self):
        """Handles the associated button being clicked."""
        self.ui.do_undoable(self._perform, None)

    def _perform(self, event):
        method_name = self.action.action
        if method_name == '':
            method_name = '_%s_clicked' % self.action.name.lower()

        method = getattr(self.ui.handler, method_name, None)
        if method is not None:
            method(self.ui.info)
        else:
            self.action.perform(event)


class BasePanel(object):
    """Base class for Traits UI panels.
    """

    #---------------------------------------------------------------------------
    #  Performs the action described by a specified Action object:
    #---------------------------------------------------------------------------

    def perform ( self, action ):
        """ Performs the action described by a specified Action object.
        """
        self.ui.do_undoable( self._perform, action )

    def _perform ( self, action ):
        method = getattr( self.ui.handler, action.action, None )
        if method is not None:
            method( self.ui.info )
        else:
            # TODO extract to common superclass for wx and qt4

            # cf. commit cdf76eb5965c0184114c4674e06b28beee04af36
            # (July 28, 2008, dmorrill) that fixes this issue for the
            # wx backend

            # look for the method in the context of the handler
            context = self.ui.context
            for item in PerformHandlers:
                handler = context.get( item, None )
                if handler is not None:
                    method = getattr( handler, action.action, None )
                    if method is not None:
                        method()
                        break
            else:
                action.perform()

    #---------------------------------------------------------------------------
    #  Check to see if a specified 'system' button is in the buttons list, and
    # add it if it is not:
    #---------------------------------------------------------------------------

    def check_button ( self, buttons, action ):
        """ Adds *action* to the system buttons list for this dialog, if it is
        not already in the list.
        """
        name = action.name
        for button in buttons:
            if self.is_button( button, name ):
                return
        buttons.append( action )

    #---------------------------------------------------------------------------
    #  Check to see if a specified Action button is a 'system' button:
    #---------------------------------------------------------------------------

    def is_button ( self, action, name ):
        """ Returns whether a specified action button is a system button.
        """
        if isinstance(action, basestring):
            return (action == name)
        return (action.name == name)

    #---------------------------------------------------------------------------
    #  Coerces a string to an Action if necessary:
    #---------------------------------------------------------------------------

    def coerce_button ( self, action ):
        """ Coerces a string to an Action if necessary.
        """
        if isinstance(action, basestring):
            return Action( name   = action,
                           action = '?'[ (not action in SystemButtons): ] )
        return action

    #---------------------------------------------------------------------------
    #  Creates a user specified button:
    #---------------------------------------------------------------------------

    def add_button ( self, action, bbox, role, method=None, enabled=True,
                     name=None, default=False ):
        """ Creates a button.
        """
        ui = self.ui
        if ((action.defined_when != '') and
            (not ui.eval_when( action.defined_when ))):
            return None

        if name is None:
            name = action.name
        id     = action.id
        button = bbox.addButton(name, role)
        button.setAutoDefault(False)
        button.setDefault(default)
        button.setEnabled(enabled)
        if (method is None) or (action.enabled_when != '') or (id != ''):
            editor = ButtonEditor( ui      = ui,
                                   action  = action,
                                   control = button )
            if id != '':
                ui.info.bind( id, editor )
            if action.visible_when != '':
                ui.add_visible( action.visible_when, editor )
            if action.enabled_when != '':
                ui.add_enabled( action.enabled_when, editor )
            if method is None:
                method = editor.perform

        if method is not None:
            button.connect(button, QtCore.SIGNAL('clicked()'), method)

        if action.tooltip != '':
            button.setToolTip(action.tooltip)

        return button

    def _on_help(self):
        """Handles the user clicking the Help button.
        """
        # FIXME: Needs porting to PyQt.
        self.ui.handler.show_help(self.ui.info, event.GetEventObject())

    def _on_undo(self):
        """Handles a request to undo a change.
        """
        self.ui.history.undo()

    def _on_undoable(self, state):
        """Handles a change to the "undoable" state of the undo history
        """
        self.undo.setEnabled(state)

    def _on_redo(self):
        """Handles a request to redo a change.
        """
        self.ui.history.redo()

    def _on_redoable(self, state):
        """Handles a change to the "redoable" state of the undo history.
        """
        self.redo.setEnabled(state)

    def _on_revert(self):
        """Handles a request to revert all changes.
        """
        ui = self.ui
        if ui.history is not None:
            ui.history.revert()
        ui.handler.revert(ui.info)

    def _on_revertable(self, state):
        """ Handles a change to the "revert" state.
        """
        self.revert.setEnabled(state)


class _StickyDialog(QtGui.QDialog):
    """A QDialog that will only close if the traits handler allows it."""

    def __init__(self, ui, parent):
        """Initialise the dialog."""

        QtGui.QDialog.__init__(self, parent)

        # Create the main window so we can add toolbars etc.
        self._mw = QtGui.QMainWindow()
        layout = QtGui.QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self._mw)
        self.setLayout(layout)

        # Set the dialog's window flags and properties.
        if ui.view.resizable:
            flags = QtCore.Qt.Window
        else:
            flags = QtCore.Qt.Dialog | QtCore.Qt.WindowSystemMenuHint
            layout.setSizeConstraint(QtGui.QLayout.SetFixedSize)
            if ui.view.resizable:
                flags |= QtCore.Qt.WindowMinimizeButtonHint | QtCore.Qt.WindowMaximizeButtonHint
        try:
            flags |= QtCore.Qt.WindowCloseButtonHint
            if ui.view.resizable:
                flags |= (QtCore.Qt.WindowMinimizeButtonHint |
                          QtCore.Qt.WindowMaximizeButtonHint)
        except AttributeError:
            # Either PyQt or Qt is too old.
            pass
        self.setWindowFlags(flags)

        self._ui = ui
        self._result = None

    def showEvent(self, e):
        self.raise_()

    def closeEvent(self, e):
        """Reimplemented to check when the clicks the window close button.
        (Note that QDialog doesn't get a close event when the dialog is closed
        in any other way.)"""

        if self._ok_to_close():
            QtGui.QDialog.closeEvent(self, e)
        else:
            # Ignore the event thereby keeping the dialog open.
            e.ignore()

    def keyPressEvent(self, e):
        """Reimplemented to ignore the Escape key if appropriate, and to ignore
        the Enter key if no default button has been explicitly set."""

        if e.key() in (QtCore.Qt.Key_Enter, QtCore.Qt.Key_Return) and \
               not self._ui.view.default_button:
            return
        
        if e.key() == QtCore.Qt.Key_Escape and not self._ok_to_close():
            return
        
        QtGui.QDialog.keyPressEvent(self, e)

    def sizeHint(self):
        """Reimplemented to provide an appropriate size hint for the window.
        """
        size = QtGui.QDialog.sizeHint(self)
        view = self._ui.view
        if view.width > 0:
            size.setWidth(view.width)
        if view.height > 0:
            size.setHeight(view.height)
        return size

    def done(self, r):
        """Reimplemented to ignore calls to accept() or reject() if
        appropriate."""

        # If we already have a result then we already know that we are done.
        if self._result is not None:
            QtGui.QDialog.done(self, self._result)
        elif self._ok_to_close(bool(r)):
            QtGui.QDialog.done(self, r)

    def _ok_to_close(self, is_ok=None):
        """Let the handler decide if the dialog should be closed."""

        # The is_ok flag is also the dialog result.  If we don't know it then
        # the the user closed the dialog other than by an 'Ok' or 'Cancel'
        # button.
        if is_ok is None:
            # Use the view's default, if there is one.
            is_ok = self._ui.view.close_result
            if is_ok is None:
                # There is no default, so use False for a modal dialog and True
                # for a non-modal one.
                is_ok = not self.isModal()

        ok_to_close = self._ui.handler.close(self._ui.info, is_ok)
        if ok_to_close:
            # Save the result now.
            self._result = is_ok

        return ok_to_close


class BaseDialog(BasePanel):
    """Base class for Traits UI dialog boxes."""

    # The different dialog styles.
    NONMODAL, MODAL, POPUP = range(3)

    def init(self, ui, parent, style):
        """Initialise the dialog by creating the controls."""

        raise NotImplementedError

    def create_dialog(self, parent, style):
        """Create the dialog control."""

        self.control = control = _StickyDialog(self.ui, parent)

        view = self.ui.view

        control.setModal(style == BaseDialog.MODAL)
        control.setWindowTitle(view.title or DefaultTitle)

        QtCore.QObject.connect(control, QtCore.SIGNAL('finished(int)'),
                self._on_finished)

    def add_contents(self, panel, buttons):
        """Add a panel (either a widget, layout or None) and optional buttons
        to the dialog."""

        # If the panel is a layout then provide a widget for it.
        if isinstance(panel, QtGui.QLayout):
            w = QtGui.QWidget()
            panel.setContentsMargins(0, 0, 0, 0)
            w.setLayout(panel)
            panel = w

        if panel is not None:
            self.control._mw.setCentralWidget(panel)

        # Add the optional buttons.
        if buttons is not None:
            self.control.layout().addWidget(buttons)

        # Add the menu bar, tool bar and status bar (if any).
        self._add_menubar()
        self._add_toolbar()
        self._add_statusbar()

    def close(self, rc=True):
        """Close the dialog and set the given return code."""

        self.ui.dispose(rc)
        self.ui = self.control = None

    @staticmethod
    def display_ui(ui, parent, style):
        """Display the UI."""

        ui.owner.init(ui, parent, style)
        ui.control = ui.owner.control
        ui.control._parent = parent

        try:
            ui.prepare_ui()
        except:
            ui.control.setParent(None)
            ui.control.ui = None
            ui.control = None
            ui.owner = None
            ui.result = False
            raise

        ui.handler.position(ui.info)
        restore_window(ui)

        if style == BaseDialog.NONMODAL:
            ui.control.show()
        else:
            ui.control.setWindowModality(QtCore.Qt.WindowModal)
            ui.control.exec_()

    def set_icon(self, icon=None):
        """Sets the dialog's icon."""

        from pyface.image_resource import ImageResource

        if not isinstance(icon, ImageResource):
            icon = default_icon()

        self.control.setWindowIcon(icon.create_icon())

    def _on_error(self, errors):
        """Handles editing errors."""

        self.ok.setEnabled(errors == 0)

    #---------------------------------------------------------------------------
    #  Adds a menu bar to the dialog:
    #---------------------------------------------------------------------------

    def _add_menubar(self):
        """Adds a menu bar to the dialog.
        """
        menubar = self.ui.view.menubar
        if menubar is not None:
            self._last_group = self._last_parent = None
            self.control.layout().setMenuBar(
                menubar.create_menu_bar( self.control, self ) )
            self._last_group = self._last_parent = None

    #---------------------------------------------------------------------------
    #  Adds a tool bar to the dialog:
    #---------------------------------------------------------------------------

    def _add_toolbar ( self ):
        """ Adds a toolbar to the dialog.
        """
        toolbar = self.ui.view.toolbar
        if toolbar is not None:
            self._last_group = self._last_parent = None
            qt_toolbar = toolbar.create_tool_bar( self.control, self )
            qt_toolbar.setMovable( False )
            self.control._mw.addToolBar( qt_toolbar )
            self._last_group = self._last_parent = None

    #---------------------------------------------------------------------------
    #  Adds a status bar to the dialog:
    #---------------------------------------------------------------------------

    def _add_statusbar ( self ):
        """ Adds a statusbar to the dialog.
        """
        if self.ui.view.statusbar is not None:
            control = QtGui.QStatusBar()
            control.setSizeGripEnabled(self.ui.view.resizable)
            listeners = []
            for item in self.ui.view.statusbar:
                # Create the status widget with initial text
                name = item.name
                item_control = QtGui.QLabel()
                item_control.setText(self.ui.get_extended_value(name))

                # Add the widget to the control with correct size
                width = abs(item.width)
                stretch = 0
                if width <= 1.0:
                    stretch = int(100 * width)
                else:
                    item_control.setMinimumWidth(width)
                control.addWidget(item_control, stretch)

                # Set up event listener for updating the status text
                col = name.find('.')
                obj = 'object'
                if col >= 0:
                    obj = name[:col]
                    name = name[col+1:]
                obj = self.ui.context[obj]
                set_text = self._set_status_text(item_control)
                obj.on_trait_change(set_text, name, dispatch='ui')
                listeners.append((obj, set_text, name))

            self.control._mw.setStatusBar(control)
            self.ui._statusbar = listeners

    def _set_status_text(self, control):
        """ Helper function for _add_statusbar.
        """
        def set_status_text(text):
            control.setText(text)

        return set_status_text

    #---------------------------------------------------------------------------
    #  Adds a menu item to the menu bar being constructed:
    #---------------------------------------------------------------------------

    def add_to_menu ( self, menu_item ):
        """ Adds a menu item to the menu bar being constructed.
        """
        item   = menu_item.item
        action = item.action

        if action.id != '':
            self.ui.info.bind( action.id, menu_item )

        if action.style == 'radio':
            if ((self._last_group is None) or
                (self._last_parent is not item.parent)):
                self._last_group = RadioGroup()
                self._last_parent = item.parent
            self._last_group.items.append( menu_item )
            menu_item.group = self._last_group

        if action.visible_when != '':
            self.ui.add_visible( action.visible_when, menu_item )

        if action.enabled_when != '':
            self.ui.add_enabled( action.enabled_when, menu_item )

        if action.checked_when != '':
            self.ui.add_checked( action.checked_when, menu_item )

    #---------------------------------------------------------------------------
    #  Adds a tool bar item to the tool bar being constructed:
    #---------------------------------------------------------------------------

    def add_to_toolbar ( self, toolbar_item ):
        """ Adds a toolbar item to the toolbar being constructed.
        """
        self.add_to_menu( toolbar_item )

    def can_add_to_menu(self, action, action_event=None):
        """Returns whether the action should be defined in the user interface.
        """
        if action.defined_when == '':
            return True

        return self.ui.eval_when(action.defined_when)

    def can_add_to_toolbar(self, action):
        """Returns whether the toolbar action should be defined in the user
           interface.
        """
        return self.can_add_to_menu(action)
