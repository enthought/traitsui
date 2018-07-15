""" Defines the various text editors for the ipywidgets user interface toolkit.
"""

import ipywidgets as widgets

from traits.api import TraitError

# FIXME: ToolkitEditorFactory is a proxy class defined here just for backward
# compatibility. The class has been moved to the
# traitsui.editors.text_editor file.
from traitsui.editors.text_editor import evaluate_trait, ToolkitEditorFactory

from editor import Editor

# FIXME
#  from editor_factory import ReadonlyEditor as BaseReadonlyEditor

from constants import OKColor


class SimpleEditor(Editor):
    """ Simple style text editor, which displays a text field.
    """

    # Flag for window styles:
    base_style = widgets.Text

    # Background color when input is OK:
    ok_color = OKColor

    # *** Trait definitions ***
    # Function used to evaluate textual user input:
    evaluate = evaluate_trait

    def init(self, parent):
        """ Finishes initializing the editor by creating the underlying toolkit
            widget.
        """
        factory = self.factory
        wtype = self.base_style
        self.evaluate = factory.evaluate
        self.sync_value(factory.evaluate_name, 'evaluate', 'from')

        if not factory.multi_line or factory.is_grid_cell:
            wtype = widgets.Text

        if factory.password:
            wtype = widgets.Password

        multi_line = (wtype is not widgets.Text)
        if multi_line:
            self.scrollable = True

        control = wtype(value=self.str_value, description='')

        if factory.read_only:
            control.disabled = True

        if factory.auto_set and not factory.is_grid_cell:
            control.continous_update = True
        else:
            # Assume enter_set is set, otherwise the value will never get
            # updated.
            control.continous_update = False

        self.control = control
        self.set_error_state(False)
        self.set_tooltip()

    def update_object(self):
        """ Handles the user entering input data in the edit control.
        """
        if (not self._no_update) and (self.control is not None):
            try:
                self.value = self._get_user_value()

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
        user_value = self._get_user_value()
        try:
            unequal = bool(user_value != self.value)
        except ValueError:
            # This might be a numpy array.
            unequal = True

        if unequal:
            self._no_update = True
            self.control.value = self.str_value
            self._no_update = False

        if self._error is not None:
            self._error = None
            self.ui.errors -= 1
            self.set_error_state(False)

    def _get_user_value(self):
        """ Gets the actual value corresponding to what the user typed.
        """
        value = self.control.value

        try:
            value = self.evaluate(value)
        except:
            pass

        try:
            ret = self.factory.mapping.get(value, value)
        except TypeError:
            # The value is probably not hashable.
            ret = value

        return ret

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

    base_style = widgets.Textarea


class ReadonlyEditor(SimpleEditor):
    """ Read-only style of text editor, which displays a read-only text field.
    """

    def init(self, parent):
        super(ReadonlyEditor, self).init(parent)

        self.control.disabled = True
