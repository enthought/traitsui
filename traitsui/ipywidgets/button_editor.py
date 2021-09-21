"""Defines the various button editors for the ipywidgets user interface
toolkit.
"""

import ipywidgets as widgets

from traits.api import Unicode, Str

# FIXME: ToolkitEditorFactory is a proxy class defined here just for backward
# compatibility. The class has been moved to the
# traitsui.editors.button_editor file.
from traitsui.editors.button_editor import ToolkitEditorFactory

from editor import Editor


class SimpleEditor(Editor):
    """ Simple style editor for a button.
    """

    # The button label
    label = Unicode

    # The selected item in the drop-down menu.
    selected_item = Str

    def init(self, parent):
        """ Finishes initializing the editor by creating the underlying toolkit
            widget.
        """
        label = self.factory.label or self.item.get_label(self.ui)

        # FIXME: the button widget does not support images apparently.
        # FIXME: Menus are not supported currently so ...
        if self.factory.values_trait:
            raise RuntimeError('ipywidgets does not yet support this feature.')
        else:
            self.control = widgets.Button(description=self.string_value(label))

        self.sync_value(self.factory.label_value, 'label', 'from')
        self.control.on_click(self.update_object)
        self.set_tooltip()

    def dispose(self):
        """ Disposes of the contents of an editor.
        """
        if self.control is not None:
            self.control.on_click(self.update_object, remove=False)
        super(SimpleEditor, self).dispose()

    def _label_changed(self, label):
        self.control.description = self.string_value(label)

    def update_object(self, event=None):
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


class CustomEditor(SimpleEditor):
    """ Custom style editor for a button, which can contain an image.
    """

    def init(self, parent):
        """ Finishes initializing the editor by creating the underlying toolkit
            widget.
        """
        # FIXME: We ignore orientation, width_padding, the icon,
        # and height_padding

        factory = self.factory
        if factory.label:
            label = factory.label
        else:
            label = self.item.get_label(self.ui)
        self.control = widgets.Button(description=self.string_value(label))

        self.sync_value(self.factory.label_value, 'label', 'from')
        self.control.on_click(self.update_object)
        self.set_tooltip()
