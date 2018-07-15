""" Defines the various Boolean editors for the PyQt user interface toolkit.
"""

import ipywidgets as widgets

from editor import Editor

from button_editor import SimpleEditor as button_editor

class SimpleEditor(Editor):
    """ Simple style editor for a button.
    """

    #-------------------------------------------------------------------------
    #  Trait definitions:
    #-------------------------------------------------------------------------

    # The button label
    label = widgets.Text

    # The list of items in a drop-down menu, if any
    #menu_items = List

    # The selected item in the drop-down menu.
    selected_item = Str

    #-------------------------------------------------------------------------
    #  Finishes initializing the editor by creating the underlying toolkit
    #  widget:
    #-------------------------------------------------------------------------

    def init(self, parent):
        """ Finishes initializing the editor by creating the underlying toolkit
            widget.
        """
        label = self.factory.label or self.item.get_label(self.ui)

        if self.factory.values_trait:
            self.control = QtGui.QToolButton()
            self.control.toolButtonStyle = QtCore.Qt.ToolButtonTextOnly
            self.control.setText(self.string_value(label))
            self.object.on_trait_change(
                self._update_menu, self.factory.values_trait)
            self.object.on_trait_change(
                self._update_menu,
                self.factory.values_trait + "_items")
            self._menu = QtGui.QMenu()
            self._update_menu()
            self.control.setMenu(self._menu)

        else:
            self.control = QtGui.QPushButton(self.string_value(label))
            self._menu = None
            self.control.setAutoDefault(False)

        self.sync_value(self.factory.label_value, 'label', 'from')
        self.control.clicked.connect(self.update_object)
        self.set_tooltip()

    def dispose(self):
        """ Disposes of the contents of an editor.
        """
        if self.control is not None:
            self.control.clicked.disconnect(self.update_object)
        super(SimpleEditor, self).dispose()

    def _label_changed(self, label):
        self.control.setText(self.string_value(label))

    def _update_menu(self):
        self._menu.blockSignals(True)
        self._menu.clear()
        for item in getattr(self.object, self.factory.values_trait):
            action = self._menu.addAction(item)
            action.triggered.connect(
                lambda event, name=item: self._menu_selected(name))
        self.selected_item = ""
        self._menu.blockSignals(False)

    def _menu_selected(self, item_name):
        self.selected_item = item_name
        self.label = item_name

    def update_object(self):
        """ Handles the user clicking the button by setting the factory value
            on the object.
        """
        if self.control is None:
            return
        if self.selected_item != "":
            self.value = self.selected_item
        else:
            self.value = self.factory.value

        # If there is an associated view, then display it:
        if (self.factory is not None) and (self.factory.view is not None):
            self.object.edit_traits(view=self.factory.view,
                                    parent=self.control)

    def update_editor(self):
        """ Updates the editor when the object trait changes externally to the
            editor.
        """
        pass
