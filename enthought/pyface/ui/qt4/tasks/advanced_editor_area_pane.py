# Enthought library imports.
from enthought.pyface.tasks.i_editor_area_pane import IEditorAreaPane, \
    MEditorAreaPane
from enthought.traits.api import implements, on_trait_change

# System library imports.
from enthought.qt import QtCore, QtGui

# Local imports.
from task_pane import TaskPane

###############################################################################
# 'AdvancedEditorAreaPane' class.
###############################################################################

class AdvancedEditorAreaPane(TaskPane, MEditorAreaPane):
    """ The toolkit-specific implementation of an AdvancedEditorAreaPane.

    See the IEditorAreaPane interface for API documentation.
    """

    implements(IEditorAreaPane)

    ###########################################################################
    # 'TaskPane' interface.
    ###########################################################################

    def create(self, parent):
        """ Create and set the toolkit-specific control that represents the
            pane.
        """
        self.control = control = EditorAreaWidget(self, parent)

        # Add shortcuts for scrolling through tabs.
        shortcut = QtGui.QShortcut(QtGui.QKeySequence('Alt+n'), self.control)
        shortcut.activated.connect(self._next_tab)
        shortcut = QtGui.QShortcut(QtGui.QKeySequence('Alt+p'), self.control)
        shortcut.activated.connect(self._previous_tab)

        # Add shortcuts for switching to a specific tab.
        mapper = QtCore.QSignalMapper(self.control)
        mapper.mapped.connect(self._activate_tab)
        for i in xrange(1, 10):
            sequence = QtGui.QKeySequence('Alt+%i' % i)
            shortcut = QtGui.QShortcut(sequence, self.control)
            shortcut.activated.connect(mapper.map)
            mapper.setMapping(shortcut, i - 1)

    ###########################################################################
    # 'IEditorAreaPane' interface.
    ###########################################################################

    def activate_editor(self, editor):
        """ Activates the specified editor in the pane.
        """
        editor_widget = editor.control.parent()
        editor_widget.setVisible(True)
        editor_widget.raise_()
        editor.control.setFocus()
        
    def add_editor(self, editor):
        """ Adds an editor to the pane.
        """
        editor.editor_area = self
        editor_widget = EditorWidget(editor, self.control)
        self.control.add_editor_widget(editor_widget)
        self.editors.append(editor)

    def remove_editor(self, editor):
        """ Removes an editor from the pane.
        """
        editor_widget = editor.control.parent()
        self.editors.remove(editor)
        self.control.remove_editor_widget(editor_widget)
        editor.editor_area = None

    ###########################################################################
    # Protected interface.
    ###########################################################################

    def _activate_tab(self, index):
        """ Activates the tab with the specified index, if there is one.
        """
        # FIXME: Not implemented.
        pass

    def _next_tab(self):
        """ Activate the tab after the currently active tab.
        """
        # FIXME: Not implemented.
        pass

    def _previous_tab(self):
        """ Activate the tab before the currently active tab.
        """
        # FIXME: Not implemented.
        pass

    def _get_label(self, editor):
        """ Return a tab label for an editor.
        """
        label = editor.name
        if editor.dirty:
            label = '*' + label
        return label

    #### Trait change handlers ################################################

    @on_trait_change('editors:[dirty, name]')
    def _update_label(self, editor, name, new):
        editor.control.parent().update_title()

    #### Signal handlers ######################################################

    def _update_active_editor(self, index):
        if index == -1:
            self.active_editor = None
        else:
            control = self.control.widget(index)
            self.active_editor = self._get_editor_with_control(control)

    @on_trait_change('hide_tab_bar')
    def _update_tab_bar(self):
        if self.control is not None:
            # FIXME: Not implemented.
            pass

###############################################################################
# Auxillary classes.
###############################################################################

class EditorAreaWidget(QtGui.QMainWindow):
    """ An auxillary widget for implementing AdvancedEditorAreaPane.
    """

    ###########################################################################
    # 'EditorAreaWidget' interface.
    ###########################################################################

    def __init__(self, editor_area, parent=None):
        super(EditorAreaWidget, self).__init__(parent)
        self.editor_area = editor_area
        self.reset_drag()

        # Fish out the rubber band used by Qt to indicate a drop region. We use
        # it to determine which dock widget is the hover widget.
        for child in self.children():
            if isinstance(child, QtGui.QRubberBand):
                child.installEventFilter(self)
                self._rubber_band = child
                break

        # FIXME: Currently animation is not supported.
        self.setAnimated(False)
        
        self.setDockNestingEnabled(True)
        self.setDocumentMode(True)
        self.setTabPosition(QtCore.Qt.AllDockWidgetAreas,
                            QtGui.QTabWidget.North)

    def add_editor_widget(self, editor_widget):
        """ Adds a dock widget to the editor area.
        """
        editor_widget.installEventFilter(self)
        self.addDockWidget(QtCore.Qt.LeftDockWidgetArea, editor_widget)

        # Try to place the editor in a sensible spot.
        top_left = None
        for widget in self.get_dock_widgets():
            if top_left is None or (widget.pos().manhattanLength() <
                                    top_left.pos().manhattanLength()):
                top_left = widget
        if top_left:
            self.tabifyDockWidget(top_left, editor_widget)

        # Qt will not give the dock widget focus by default.
        self.editor_area.activate_editor(editor_widget.editor)

    def get_dock_widgets(self):
        """ Gets all visible dock widgets.
        """
        return [ child for child in self.children()
                 if isinstance(child, QtGui.QDockWidget) and child.isVisible() ]
    
    def get_dock_widgets_for_bar(self, tab_bar):
        """ Get the dock widgets, in order, attached to given tab bar.

        Because QMainWindow locks this info down, we have resorted to a hack.
        """
        pos = tab_bar.pos()
        key = lambda w: QtGui.QVector2D(pos - w.pos()).lengthSquared()
        all_widgets = self.get_dock_widgets()
        if all_widgets:
            current = min(all_widgets, key=key)
            widgets = self.tabifiedDockWidgets(current)
            widgets.insert(tab_bar.currentIndex(), current)
            return widgets
        return []

    def remove_editor_widget(self, editor_widget):
        """ Removes a dock widget from the editor area.
        """
        editor_widget.hide()
        editor_widget.removeEventFilter(self)
        editor_widget.editor.destroy()
        self.removeDockWidget(editor_widget)

    def reset_drag(self):
        """ Clear out all drag state.
        """
        self._drag_widget = None
        self._hover_widget = None
        self._tear_handled = False
        self._tear_widgets = []

    def set_hover_widget(self, widget):
        """ Set the dock widget being 'hovered over' during a drag.
        """
        old_widget = self._hover_widget
        self._hover_widget = widget
        
        if old_widget:
            if old_widget in self._tear_widgets:
                if len(self._tear_widgets) == 1:
                    old_widget.set_title_bar(True)
            elif not self.tabifiedDockWidgets(old_widget):
                old_widget.set_title_bar(True)

        if widget:
            if widget in self._tear_widgets:
                if len(self._tear_widgets) == 1:
                    widget.set_title_bar(False)
            elif len(self.tabifiedDockWidgets(widget)) == 1:
                widget.set_title_bar(False)

    ###########################################################################
    # Event handlers.
    ###########################################################################

    def childEvent(self, event):
        """ Reimplemented to gain access to the tab bars as they are created.
        """
        super(EditorAreaWidget, self).childEvent(event)
        if event.polished():
            child = event.child()
            if isinstance(child, QtGui.QTabBar):
                child.installEventFilter(self)

                # FIXME: We would like to have the tabs movable, but this
                # confuses the QMainWindowLayout. For now, we disable this.
                #child.setMovable(True)
                
                child.setTabsClosable(True)
                child.tabCloseRequested.connect(self._tab_close_requested,
                                                QtCore.Qt.UniqueConnection)

    def eventFilter(self, obj, event):
        """ Reimplemented to dispatch to sub-handlers.
        """
        if isinstance(obj, QtGui.QDockWidget):
            return self._dock_widget_filter(obj, event)

        elif isinstance(obj, QtGui.QRubberBand):
            return self._rubber_band_filter(obj, event)
        
        elif isinstance(obj, QtGui.QTabBar):
            return self._tab_filter(obj, event)
        
        return False

    def _dock_widget_filter(self, widget, event):
        """ Support hover widget state tracking.
        """
        if self._drag_widget and event.type() == QtCore.QEvent.Resize:
            if widget.geometry() == self._rubber_band.geometry():
                self.set_hover_widget(widget)

        elif self._drag_widget == widget and event.type() == QtCore.QEvent.Move:
            if len(self._tear_widgets) == 1 and not self._tear_handled:
                widget = self._tear_widgets[0]
                widget.set_title_bar(True)
                self._tear_handled = True

        return False

    def _tab_filter(self, tab_bar, event):
        """ Support 'tearing off' a tab.
        """
        if event.type() == QtCore.QEvent.MouseMove:
            if tab_bar.rect().contains(event.pos()):
                self.reset_drag()
            else:
                if not self._drag_widget:
                    index = tab_bar.currentIndex()
                    self._tear_widgets = self.get_dock_widgets_for_bar(tab_bar)
                    self._drag_widget = widget = self._tear_widgets.pop(index)

                    pos = QtCore.QPoint(0, 0)
                    press_event = QtGui.QMouseEvent(
                        QtCore.QEvent.MouseButtonPress, pos,
                        widget.mapToGlobal(pos), QtCore.Qt.LeftButton,
                        QtCore.Qt.LeftButton, event.modifiers())
                    QtCore.QCoreApplication.sendEvent(widget, press_event)
                    return True

                event = QtGui.QMouseEvent(
                        QtCore.QEvent.MouseMove, event.pos(), event.globalPos(),
                        event.button(), event.buttons(), event.modifiers())
                QtCore.QCoreApplication.sendEvent(self._drag_widget, event)
                return True

        return False

    def _rubber_band_filter(self, rubber_band, event):
        """ Support hover widget state tracking.
        """
        if self._drag_widget and event.type() in (QtCore.QEvent.Resize,
                                                  QtCore.QEvent.Move):
            self.set_hover_widget(None)

        return False

    ###########################################################################
    # Signal handlers.
    ###########################################################################

    def _tab_close_requested(self, index):
        """ Handle a tab close request.
        """
        editor_widget = self.get_dock_widgets_for_bar(self.sender())[index]
        editor_widget.editor.close()

    
class EditorWidget(QtGui.QDockWidget):
    """ An auxillary widget for implementing AdvancedEditorAreaPane.
    """
    
    def __init__(self, editor, parent=None):
        super(EditorWidget, self).__init__(parent)
        self.editor = editor
        self.editor.create(self)
        self.setFeatures(QtGui.QDockWidget.DockWidgetClosable |
                         QtGui.QDockWidget.DockWidgetMovable)
        self.setWidget(editor.control)
        self.update_title()

        self._updating = False
        self.dockLocationChanged.connect(self.update_title_bar)
        self.visibilityChanged.connect(self.update_title_bar)

    def update_title(self):
        title = self.editor.editor_area._get_label(self.editor)
        self.setWindowTitle(title)
        
        title_bar = self.titleBarWidget()
        if isinstance(title_bar, EditorTitleBarWidget):
            title_bar.update_title()

    def update_title_bar(self):
        # Prevent infinite recursion.
        if not self._updating and self not in self.parent()._tear_widgets:
            self._updating = True
            try:
                tabbed = [ w for w in self.parent().tabifiedDockWidgets(self)
                           if w.isVisible() ]
                self.set_title_bar(not tabbed)
            finally:
                self._updating = False

    def set_title_bar(self, title_bar):
        if title_bar:
            self.setTitleBarWidget(EditorTitleBarWidget(self))
        else:
            self.setTitleBarWidget(QtGui.QWidget())
                

class EditorTitleBarWidget(QtGui.QTabBar):
    """ An auxillary widget for implementing AdvancedEditorAreaPane.
    """
    
    def __init__(self, editor_widget):
        super(EditorTitleBarWidget, self).__init__(editor_widget)
        self.addTab(editor_widget.windowTitle())
        self.setDocumentMode(True)
        self.setExpanding(False)
        self.setTabsClosable(True)

        self.tabCloseRequested.connect(editor_widget.editor.close)

    def update_title(self):
        self.setTabText(0, self.parent().windowTitle())

    def mousePressEvent(self, event):
        self.parent().parent().reset_drag()
        self.parent().parent()._drag_widget = self.parent()
        event.ignore()

    def mouseMoveEvent(self, event):
        event.ignore()
        
    def mouseReleaseEvent(self, event):
        event.ignore()
