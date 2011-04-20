# Standard library imports.
import sys

# Enthought library imports.
from enthought.pyface.tasks.i_editor_area_pane import IEditorAreaPane, \
    MEditorAreaPane
from enthought.traits.api import implements, on_trait_change

# System library imports.
from enthought.qt import QtCore, QtGui

# Local imports.
from task_pane import TaskPane


class EditorAreaPane(TaskPane, MEditorAreaPane):
    """ The toolkit-specific implementation of a EditorAreaPane.

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
        # Create and configure the tab widget.
        self.control = control = QtGui.QTabWidget(parent)
        control.tabBar().setVisible(not self.hide_tab_bar)
        control.setDocumentMode(True)
        control.setMovable(True)
        control.setTabsClosable(True)

        # Connect to the widget's signals.
        control.currentChanged.connect(self._update_active_editor)
        control.tabCloseRequested.connect(self._close_requested)

        # Add shortcuts for scrolling through tabs.
        mod = 'Meta+' if sys.platform == 'darwin' else 'Alt+'
        shortcut = QtGui.QShortcut(QtGui.QKeySequence(mod+'n'), self.control)
        shortcut.activated.connect(self._next_tab)
        shortcut = QtGui.QShortcut(QtGui.QKeySequence(mod+'p'), self.control)
        shortcut.activated.connect(self._previous_tab)

        # Add shortcuts for switching to a specific tab.
        mapper = QtCore.QSignalMapper(self.control)
        mapper.mapped.connect(self.control.setCurrentIndex)
        for i in xrange(1, 10):
            sequence = QtGui.QKeySequence(mod + str(i))
            shortcut = QtGui.QShortcut(sequence, self.control)
            shortcut.activated.connect(mapper.map)
            mapper.setMapping(shortcut, i - 1)

    ###########################################################################
    # 'IEditorAreaPane' interface.
    ###########################################################################

    def activate_editor(self, editor):
        """ Activates the specified editor in the pane.
        """
        self.control.setCurrentWidget(editor.control)
        
    def add_editor(self, editor):
        """ Adds an editor to the pane.
        """
        editor.editor_area = self
        editor.create(self.control)
        self.control.addTab(editor.control, self._get_label(editor))
        self.editors.append(editor)
        self._update_tab_bar()

        # The 'currentChanged' signal, used below, is not emitted when the first
        # editor is added.
        if len(self.editors) == 1:
            self.active_editor = editor

    def remove_editor(self, editor):
        """ Removes an editor from the pane.
        """
        self.editors.remove(editor)
        self.control.removeTab(self.control.indexOf(editor.control))
        editor.destroy()
        editor.editor_area = None
        self._update_tab_bar()

    ###########################################################################
    # Protected interface.
    ###########################################################################

    def _get_label(self, editor):
        """ Return a tab label for an editor.
        """
        label = editor.name
        if editor.dirty:
            label = '*' + label
        return label

    def _get_editor_with_control(self, control):
        """ Return the editor with the specified control.
        """
        for editor in self.editors:
            if editor.control == control:
                return editor
        return None

    def _next_tab(self):
        """ Activate the tab after the currently active tab.
        """
        self.control.setCurrentIndex(self.control.currentIndex() + 1)

    def _previous_tab(self):
        """ Activate the tab before the currently active tab.
        """
        self.control.setCurrentIndex(self.control.currentIndex() - 1)

    #### Trait change handlers ################################################

    @on_trait_change('editors:[dirty, name]')
    def _update_label(self, editor, name, new):
        index = self.control.indexOf(editor.control)
        self.control.setTabText(index, self._get_label(editor))

    #### Signal handlers ######################################################

    def _close_requested(self, index):
        control = self.control.widget(index)
        editor = self._get_editor_with_control(control)
        editor.close()
        
    def _update_active_editor(self, index):
        if index == -1:
            self.active_editor = None
        else:
            control = self.control.widget(index)
            self.active_editor = self._get_editor_with_control(control)

    @on_trait_change('hide_tab_bar')
    def _update_tab_bar(self):
        if self.control is not None:
            visible = self.control.count() > 1 if self.hide_tab_bar else True
            self.control.tabBar().setVisible(visible)
