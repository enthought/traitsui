""" Defines the various text editors for the ipywidgets user interface toolkit.
"""

import ipywidgets as widgets

from traits.api import TraitError

# FIXME: ToolkitEditorFactory is a proxy class defined here just for backward
# compatibility. The class has been moved to the
# traitsui.editors.text_editor file.
from traitsui.editors.text_editor import evaluate_trait, ToolkitEditorFactory

from .editor import Editor

# FIXME
#  from editor_factory import ReadonlyEditor as BaseReadonlyEditor

from .constants import OKColor


class SimpleEditor(Editor):
    """ Simple style text editor, which displays a text field.
    """

    # Flag for window styles:
    base_style = widgets.DatePicker

    def init(self, parent):
        """ Finishes initializing the editor by creating the underlying toolkit
            widget.
        """
        factory = self.factory
        wtype = self.base_style

        control = wtype(value=self.value, description='')

        control.observe(self.update_object, 'value')

        self.control = control
        self.set_error_state(False)
        self.set_tooltip()

    def update_object(self, event=None):
        """ Handles the user entering input data in the edit control.
        """
        if (not self._no_update) and (self.control is not None):
            try:
                self.value = self.control.value

                if self._error is not None:
                    self._error = None
                    self.ui.errors -= 1

                self.set_error_state(False)

            except TraitError as excp:
                pass

    def update_editor(self):
        """ Updates the editor when the object trait changes externally to the
            editor.
        """
        self.control.value = self.value

    def error(self, excp):
        """ Handles an error that occurs while setting the object's trait value.
        """
        if self._error is None:
            self._error = True
            self.ui.errors += 1

        self.set_error_state(True)

    def in_error_state(self):
        """ Returns whether or not the editor is in an error state.
        """
        return (self.invalid or self._error)


class CustomEditor(SimpleEditor):
    """ Custom style of text editor, which displays a multi-line text field.
    """

    pass


class ReadonlyEditor(SimpleEditor):
    """ Read-only style of text editor, which displays a read-only text field.
    """

    def init(self, parent):
        super(ReadonlyEditor, self).init(parent)

        self.control.disabled = True
