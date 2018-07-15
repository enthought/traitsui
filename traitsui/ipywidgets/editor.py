""" Defines the base class for ipywidgets editors.
"""
from __future__ import print_function

from traits.api import HasTraits, Instance, Str, Callable

from traitsui.api import Editor as UIEditor

from constants import OKColor, ErrorColor


class Editor(UIEditor):
    """ Base class for ipywidgets editors for Traits-based UIs.
    """

    def clear_layout(self):
        """ Delete the contents of a control's layout.
        """
        # FIXME?
        pass

    def _control_changed(self, control):
        """ Handles the **control** trait being set.
        """
        # FIXME: Check we actually make use of this.
        if control is not None:
            control._editor = self

    def set_focus(self):
        """ Assigns focus to the editor's underlying toolkit widget.
        """
        # FIXME?
        pass

    def update_editor(self):
        """ Updates the editor when the object trait changes externally to the
            editor.
        """
        new_value = self.value
        if self.control.value != new_value:
            self.control.value = new_value

    def error(self, excp):
        """ Handles an error that occurs while setting the object's trait value.
        """
        # Make sure the control is a widget rather than a layout.
        # FIXME?
        print(self.control, self.description, 'value error', str(excp))

    def set_tooltip(self, control=None):
        """ Sets the tooltip for a specified control.
        """
        desc = self.description
        if desc == '':
            desc = self.object.base_trait(self.name).desc
            if desc is None:
                return False

            desc = 'Specifies ' + desc

        if control is None:
            control = self.control

        if hasattr(control, 'tooltip'):
            control.tooltip = desc

        return True

    def _enabled_changed(self, enabled):
        """Handles the **enabled** state of the editor being changed.
        """
        if self.control is not None:
            self._enabled_changed_helper(self.control, enabled)
        if self.label_control is not None:
            self.label_control.disabled = not enabled

    def _enabled_changed_helper(self, control, enabled):
        """A helper that allows the control to be a layout and recursively
           manages all its widgets.
        """
        if hasattr(control, 'disabled'):
            control.disabled = not enabled
        elif hasattr(control, 'children'):
            for child in control.children:
                child.disabled = not enabled

    def _visible_changed(self, visible):
        """Handles the **visible** state of the editor being changed.
        """
        visibility = 'visible' if visible else 'hidden'
        if self.label_control is not None:
            self.label_control.layout.visibility = visibility
        if self.control is None:
            # We are being called after the editor has already gone away.
            return

        self._visible_changed_helper(self.control, visibility)

    def _visible_changed_helper(self, control, visibility):
        """A helper that allows the control to be a layout and recursively
           manages all its widgets.
        """
        if hasattr(control, 'layout'):
            control.layout.visibility = visibility
        if hasattr(control, 'children'):
            for child in control.children:
                self._visible_changed_helper(child, visibility)

    def get_error_control(self):
        """ Returns the editor's control for indicating error status.
        """
        return self.control

    def in_error_state(self):
        """ Returns whether or not the editor is in an error state.
        """
        return False

    def set_error_state(self, state=None, control=None):
        """ Sets the editor's current error state.
        """
        if state is None:
            state = self.invalid
        state = state or self.in_error_state()

        if control is None:
            control = self.get_error_control()

        if not isinstance(control, list):
            control = [control]

        for item in control:
            if item is None:
                continue

            if state:
                color = ErrorColor
            else:
                color = OKColor

            try:
                if hasattr(item, 'box_style'):
                    item.box_style = color
            # FIXME!
            except Exception:
                pass

    def _invalid_changed(self, state):
        """ Handles the editor's invalid state changing.
        """
        self.set_error_state()

    def eval_when(self, condition, object, trait):
        """ Evaluates a condition within a defined context, and sets a
        specified object trait based on the result, which is assumed to be a
        Boolean.
        """
        if condition != '':
            value = True
            try:
                if not eval(condition, globals(), self._menu_context):
                    value = False
            except:
                from traitsui.api import raise_to_debug
                raise_to_debug()
            setattr(object, trait, value)


class EditorWithList(Editor):
    """ Editor for an object that contains a list.
    """
    # Object containing the list being monitored
    list_object = Instance(HasTraits)

    # Name of the monitored trait
    list_name = Str

    # Function used to evaluate the current list object value:
    list_value = Callable

    def init(self, parent):
        """ Initializes the object.
        """
        factory = self.factory
        name = factory.name
        if name != '':
            self.list_object, self.list_name, self.list_value = \
                self.parse_extended_name(name)
        else:
            self.list_object, self.list_name = factory, 'values'
            self.list_value = lambda: factory.values

        self.list_object.on_trait_change(self._list_updated,
                                         self.list_name, dispatch='ui')
        self.list_object.on_trait_change(
            self._list_updated,
            self.list_name + '_items',
            dispatch='ui')

        self._list_updated()

    def dispose(self):
        """ Disconnects the listeners set up by the constructor.
        """
        self.list_object.on_trait_change(self._list_updated,
                                         self.list_name, remove=True)
        self.list_object.on_trait_change(
            self._list_updated,
            self.list_name + '_items',
            remove=True)

        super(EditorWithList, self).dispose()

    def _list_updated(self):
        """ Handles the monitored trait being updated.
        """
        self.list_updated(self.list_value())

    def list_updated(self, values):
        """ Handles the monitored list being updated.
        """
        raise NotImplementedError


class EditorFromView(Editor):
    """ An editor generated from a View object.
    """

    def init(self, parent):
        """ Initializes the object.
        """
        self._ui = ui = self.init_ui(parent)
        if ui.history is None:
            ui.history = self.ui.history

        self.control = ui.control

    def init_ui(self, parent):
        """ Creates and returns the traits UI defined by this editor.
            (Must be overridden by a subclass).
        """
        raise NotImplementedError

    def update_editor(self):
        """ Updates the editor when the object trait changes externally to the
            editor.
        """
        # Normally nothing needs to be done here, since it should all be
        # handled by the editor's internally created traits UI:
        pass

    def dispose(self):
        """ Disposes of the editor.
        """
        self._ui.dispose()

        super(EditorFromView, self).dispose()
