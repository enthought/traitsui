""" Defines the various Boolean editors for the PyQt user interface toolkit.
"""

import ipywidgets as widgets

from editor import Editor

# This needs to be imported in here for use by the editor factory for boolean
# editors (declared in traitsui). The editor factory's text_editor
# method will use the TextEditor in the ui.
from text_editor import SimpleEditor as TextEditor


class SimpleEditor(Editor):
    """ Simple style of editor for Boolean values, which displays a check box.
    """
    def init(self, parent):
        """ Finishes initializing the editor by creating the underlying toolkit
            widget.
        """
        self.control = widgets.Checkbox(value=True, description='')
        self.control.observe(self.update_object, 'value')
        self.set_tooltip()

    def update_object(self, event=None):
        """ Handles the user clicking the checkbox.
        """
        self.value = bool(self.control.value)

    def update_editor(self):
        """ Updates the editor when the object trait changes externally to the
            editor.
        """
        self.control.value = self.value


class ReadonlyEditor(Editor):
    """ Read-only style of editor for Boolean values, which displays static text
    of either "True" or "False".
    """

    def init(self, parent):
        """ Finishes initializing the editor by creating the underlying toolkit
            widget.
        """
        self.control = widgets.Valid(value=self.value, readout='')

    def update_editor(self):
        """ Updates the editor when the object trait changes externally to the
            editor.
        """
        self.control.value = self.value
