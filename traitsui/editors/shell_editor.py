# (C) Copyright 2004-2023 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

""" Editor that displays an interactive Python shell.
"""

from traits.api import Bool, Str, Event, Property, observe
from traits.observation.api import match

from traitsui.basic_editor_factory import BasicEditorFactory
from traitsui.editor import Editor
from traitsui.toolkit import toolkit_object


class _ShellEditor(Editor):
    """Base class for an editor that displays an interactive Python shell."""

    #: An event fired to execute a command in the shell.
    command_to_execute = Event()

    #: An event fired whenver the user executes a command in the shell:
    command_executed = Event(Bool)

    #: Is the shell editor is scrollable? This value overrides the default.
    scrollable = True

    # -------------------------------------------------------------------------
    # 'Editor' Interface
    # -------------------------------------------------------------------------

    def init(self, parent):
        """Finishes initializing the editor by creating the underlying toolkit
        widget.
        """
        # Moving the import here, since PythonShell is implemented in the
        # Pyface backend packages, and we want to delay loading this toolkit
        # specific class until this editor is actually used.
        from pyface.python_shell import PythonShell

        locals = None
        self._base_locals = None
        value = self.value
        if self.factory.share and isinstance(value, dict):
            locals = value
        self._shell = shell = PythonShell(parent)
        shell.create()
        self.control = shell.control
        if locals:
            for item in locals.items():
                shell.bind(*item)
        if locals is None:
            object = self.object
            shell.bind("self", object)
            shell.observe(
                self.update_object, "command_executed", dispatch="ui"
            )
            if not isinstance(value, dict):
                self._any_trait_observer = lambda name, ctrait: True
                object.observe(
                    self.update_any,
                    match(self._any_trait_observer),
                    dispatch="ui",
                )
            else:
                self._base_locals = locals = {}
                for name in self._shell.interpreter().locals.keys():
                    locals[name] = None

        # Synchronize any editor events:
        self.sync_value(
            self.factory.command_to_execute, "command_to_execute", "from"
        )
        self.sync_value(
            self.factory.command_executed, "command_executed", "to"
        )

        self.set_tooltip()

    def update_object(self, event):
        """Handles the user entering input data in the edit control."""
        locals = self._shell.interpreter().locals
        base_locals = self._base_locals
        if base_locals is None:
            object = self.object
            for name in object.trait_names():
                if name in locals:
                    try:
                        setattr(object, name, locals[name])
                    except:
                        pass
        else:
            dic = self.value
            for name in locals.keys():
                if name not in base_locals:
                    try:
                        dic[name] = locals[name]
                    except:
                        pass

        self.command_executed = True

    def update_editor(self):
        """Updates the editor when the object trait changes externally to the
        editor.
        """
        if self.factory.share:
            value = self.value
            if isinstance(value, dict):
                self._shell.interpreter().locals = value
        else:
            locals = self._shell.interpreter().locals
            base_locals = self._base_locals
            if base_locals is None:
                object = self.object
                for name in object.trait_names():
                    locals[name] = getattr(object, name, None)
            else:
                dic = self.value
                for name, value in dic.items():
                    locals[name] = value

    def update_any(self, event):
        """Updates the editor when the object trait changes externally to the
        editor.
        """
        name, new = event.name, event.new
        locals = self._shell.interpreter().locals
        if self._base_locals is None:
            locals[name] = new
        else:
            self.value[name] = new

    def dispose(self):
        """Disposes of the contents of an editor."""
        if not (self.factory.share and isinstance(self.value, dict)):
            self._shell.observe(
                self.update_object,
                "command_executed",
                remove=True,
                dispatch="ui",
            )
            if self._base_locals is None:
                self.object.observe(
                    self.update_any,
                    match(self._any_trait_observer),
                    remove=True,
                    dispatch="ui",
                )

        super().dispose()

    def restore_prefs(self, prefs):
        """Restores any saved user preference information associated with the
        editor.
        """
        shell = self._shell
        try:
            history = prefs.get("history", [])
            history_index = prefs.get("history_index", -1)
            shell.set_history(history, history_index)
        except:
            pass

    def save_prefs(self):
        """Returns any user preference information associated with the editor."""
        history, history_index = self._shell.get_history()
        return {"history": history, "history_index": history_index}

    # -------------------------------------------------------------------------
    # Private Interface
    # -------------------------------------------------------------------------

    # Trait change handlers --------------------------------------------------

    @observe("command_to_execute")
    def _execute_command(self, event):
        """Handles the 'command_to_execute' trait being fired."""
        # Show the command. A 'hidden' command should be executed directly on
        # the namespace trait!
        command = event.new
        self._shell.execute_command(command, hidden=False)


class ShellEditor(BasicEditorFactory):
    """Editor factory for shell editors."""

    #: The editor class to be instantiated.
    klass = Property()

    #: Should the shell interpreter use the object value's dictionary?
    share = Bool(False)

    #: Extended trait name of the object event trait which triggers a command
    #: execution in the shell when fired.
    command_to_execute = Str()

    #: Extended trait name of the object event trait which is fired when a
    #: command is executed.
    command_executed = Str()

    def _get_klass(self):
        """Returns the toolkit-specific editor class to be used in the UI."""
        return toolkit_object("shell_editor:_ShellEditor")


# This alias is deprecated and will be removed in TraitsUI 8.
ToolkitEditorFactory = ShellEditor
