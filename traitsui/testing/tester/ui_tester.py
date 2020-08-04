#  Copyright (c) 2005-2020, Enthought, Inc.
#  All rights reserved.
#
#  This software is provided without warranty under the terms of the BSD
#  license included in LICENSE.txt and may be redistributed only
#  under the conditions described in the aforementioned license.  The license
#  is also available online at http://www.enthought.com/licenses/BSD.txt
#
#  Thanks for using Enthought open source!
#

from contextlib import contextmanager

from traitsui.testing.tester import query
from traitsui.testing.tester.abstract_registry import AbstractRegistry
from traitsui.testing.tester.exceptions import (
    ActionNotSupported,
    EditorNotFound,
)
from traitsui.tests._tools import (
    create_ui as _create_ui,
    process_cascade_events,
    reraise_exceptions,
)


@contextmanager
def _event_processed():
    """ Context manager to ensure GUI events are processed upon entering
    and exiting the context.
    """
    with reraise_exceptions():
        process_cascade_events()
        try:
            yield
        finally:
            process_cascade_events()


class _CustomActionRegistry(AbstractRegistry):
    """ This registry is defined such that CustomAction can be used with
    any editor.
    This allows arbitrary extension using the UITester API.
    """

    def get_handler(self, editor_class, action_class):
        """ Return a callable for handling an action for a given editor class.

        Parameters
        ----------
        editor_class : subclass of traitsui.editor.Editor
            A toolkit specific Editor class.
        action_class : subclass of type
            Any class.

        Returns
        -------
        handler : callable(UserInteractor, action) -> any
        """
        if issubclass(action_class, query.CustomAction):
            return _CustomActionRegistry._custom_action_handler

        raise ActionNotSupported(
            editor_class=editor_class,
            action_class=action_class,
            supported=[query.CustomAction],
        )

    @staticmethod
    def _custom_action_handler(interactor, action):
        return action.func(interactor)


class UITester:
    """ UITester assists testing of GUI applications developed using TraitsUI.

    The following actions typically found in tests are supported by the tester:

    - (1) Create a GUI that will be cleaned up when the test exits.
    - (2) Locate the GUI element to be tested.
    - (3) Perform the user interaction for side effects (e.g. mouse clicking)
    - (4) Inspect GUI element as a user would (e.g. checking the displayed text
          on a widget)

    Creating a GUI
    --------------
    Given a ``HasTraits`` object, a GUI can be created using the
    ``UITester.create_ui`` method::

        class App(HasTraits):
            text = Str()

        obj = App()
        tester = UITester()
        with tester.create_ui(obj) as ui:
            pass

    ``create_ui`` is a context manager such that it ensures the GUI is always
    disposed of at the end of a test.

    The returned value is an instance of ``traitsui.ui.UI``. This is the entry
    point for locating GUI elements for further testing.

    Locating GUI elements
    ---------------------
    After creating an ``UI`` object, ``UITester.find_by_name`` can be used
    to locate a specific UI editor::

        obj = App()
        tester = UITester()
        with tester.create_ui(obj) as ui:
            interactor = tester.find_by_name(ui, "text")

    The returned value is an instance of ``UserInteractor``. It wraps the
    UI editor instance found and allows further test actions to be performed on
    the editor.

    Since it is fairly typical for a UI editor to have a nested UI (and those
    nested UI may bave more nested UI), to locate these nested UIs,
    ``UserInteractor.find_by_name``  can be used::

        class Person(HasTraits):
            name = Str()

        class Account(HasTraits):
            person = Instance(Person)

        view = View(Item(name="person", style="custom"))
        account = Account(person=Person())
        tester = UITester()
        with tester.create_ui(account, dict(view=view)) as ui:
            interactor = tester.find_by_name(ui, "person").find_by_name("name")

    Performing an action (commands)
    -------------------------------
    After locating the GUI element, we typically want to perform some user
    actions on it for testing. Examples of user interactions that produce side
    effects are clicking or double clicking a mouse button, typing some keys
    on the keyboard, etc.

    To perform an action for side effects, call the ``UserInteractor.perform``
    method with the action required. A set of predefined command types can be
    found in the ``traitsui.testing.tester.command``.

    Example::

        with tester.create_ui(app, dict(view=view)) as ui:
            tester.find_by_name(ui, "button").perform(command.MouseClick())
            assert app.clicked

    Inspecting GUI element (queries)
    --------------------------------
    Sometimes, the test may want to inspect visual elements on the GUI, e.g.
    checking if a textbox has displayed the expected value.

    To perform an action for queries, call the ``UserInteractor.inspect``
    method with the query required. A set of predefined query types can be
    found in the ``traitsui.testing.tester.query``.

    Example::

        with tester.create_ui(app, dict(view=view)) as ui:
            text = (
                tester.find_by_name(ui, "text").inspect(query.DisplayedText()
            )
            assert text == "Hello"

    Extending the API
    -----------------
    There are two ways to extend the API.

    (1) Provide a custom function in an ad-hoc fashion using
        ``traitsui.testing.tester.query.CustomAction``.
    (2) Define a registry for mapping editor and action types to a specific
        implementation that handles the action.

    Using CustomAction
    ^^^^^^^^^^^^^^^^^^
    This method is quick and easy but it does not scale well with multiple
    toolkit support.

    For example::

        def test_my_editor(self):

            def custom_function(interactor):
                # Toolkit specific code
                return interactor.editor.control.getText()

            tester = UITester()
            with tester.create_ui(obj) as ui:
                value = tester.find_by_name(ui, "my_trait").inspect(
                    query.CustomAction(func=custom_function)
                )

    Using registry
    ^^^^^^^^^^^^^^
    This method is more scalable for supporting multiple toolkit. This is the
    preferred approach for library code to support testing of UI editor they
    maintain.

    For example, suppose there is a custom UI editor ``MyEditor``, to implement
    a custom action type ``ManyMouseClick`` for this editor::

        custom_registry = EditorActionRegistry()
        custom_registry.register(
            editor_class=MyEditor,
            action_class=ManyMouseClick,
            handler=lambda interactor, action: interactor.editor.do_something()
        )

    Then the registry can be used in a UITester::

        tester = UITester([custom_registry])

    This is how TraitsUI supplies testing support for specific editors; the
    default setup of ``UITester`` comes with a registry for testing TraitsUI
    editors.

    See documentation on the ``AbstractRegistry`` and ``EditorActionRegistry``
    for details.
    """

    def __init__(self, registries=None):
        """ Instantiate the UI tester.

        Parameters
        ----------
        registries : list of AbstractRegistry, optional
            Registries of interactors for different editors, in the order
            of decreasing priority. A shallow copy will be made.
            Default is a list containing default implementations provided
            by TraitsUI as well as a registry for supporting ``CustomAction``.
        """

        if registries is None:
            self._registries = [
                _CustomActionRegistry(),
            ]
        else:
            self._registries = registries.copy()

    def create_ui(self, object, ui_kwargs=None):
        """ Context manager to create a UI and dispose it upon exit.

        Parameters
        ----------
        object : HasTraits
            An instance of HasTraits for which a GUI will be created.
        ui_kwargs : dict or None, optional
            Keyword arguments to be provided to ``HasTraits.edit_traits``.
            Default is to call ``edit_traits`` with no additional keyword
            arguments.

        Yields
        ------
        ui : traitsui.ui.UI
        """
        return _create_ui(object, ui_kwargs)

    def find_by_name(self, ui, name):
        """ Find the UI editor with the given name and return an object for
        simulating user interactions with the editor. The list of
        ``InteractorRegistry`` in this tester is used for finding the editor
        specified. If no specific interactor can be found from the registries,
        a default interactor wrapping the found editor is returned.

        Parameters
        ----------
        ui : traitsui.ui.UI
            The UI created, e.g. by ``create_ui``.
        name : str
            A single or an extended name for retreiving an editor on a UI.
            e.g. "attr", "model.attr1.attr2"

        Returns
        -------
        interactor : UserInteractor
        """
        editor = _get_editor_by_name(ui, name)
        return UserInteractor(
            editor=editor,
            registries=self._registries,
        )


class UserInteractor:
    """
    Attributes
    ----------
    editor : Editor
        An instance of Editor. It is assumed to be in a state after the UI
        has been initialized but before it is disposed of.
    """

    def __init__(self, editor, registries):
        self.editor = editor
        self.registries = registries

    def find_by_name(self, name):
        """ Find an editor inside the nested UI in the current editor

        Similar to UITester, but the UI is given by the editor in this
        interactor.

        Parameters
        ----------
        ui : traitsui.ui.UI
            The UI created, e.g. by ``create_ui``.
        name : str
            A single name for retreiving an editor on a UI.

        Returns
        -------
        interactor : UserInteractor
        """
        ui = self.inspect(query.NestedUI())
        editor = _get_editor_by_name(ui, name)
        return UserInteractor(
            editor=editor,
            registries=self.registries,
        )

    def perform(self, action):
        """ Perform a user action that causes side effects.

        Parameters
        ----------
        action : object
            An action instance that defines the user action.
            See ``traitsui.testing.tester.command`` module for builtin
            query objects.
            e.g. ``traitsui.testing.tester.command.MouseClick``
        """
        self._perform_or_inspect(action)

    def inspect(self, action):
        """ Return a value or values for inspection.

        Parameters
        ----------
        action : object
            An action instance that defines the inspection.
            See ``traitsui.testing.tester.query`` module for builtin
            query objects.
            e.g. ``traitsui.testing.tester.query.DisplayedText``
        """
        return self._perform_or_inspect(action)

    def _perform_or_inspect(self, action):
        """ Perform a user action or a user inspection.
        """
        action_class = action.__class__
        supported = []
        for registry in self.registries:
            try:
                handler = registry.get_handler(
                    editor_class=self.editor.__class__,
                    action_class=action_class,
                )
            except ActionNotSupported as e:
                supported.extend(e.supported)
                continue
            else:
                with _event_processed():
                    return handler(self, action)

        raise ActionNotSupported(
            editor_class=self.editor.__class__,
            action_class=action.__class__,
            supported=supported,
        )


def _get_editor_by_name(ui, name):
    """ Return a single Editor from an instance of traitsui.ui.UI with
    a given name. Raise if zero or many editors are found.

    Parameters
    ----------
    ui : traitsui.ui.UI
        The UI from which an editor will be retrieved.
    name : str
        A single name for retreiving an editor on a UI.

    Returns
    -------
    editor : Editor
        The single editor found.

    Raises
    ------
    EditorNotFound
        If the editor cannot be found.
    ValueError
        If multiple editors are associated with the given name.
    """
    editors = ui.get_editors(name)

    if not editors:
        raise EditorNotFound(
            "No editors can be found with name {!r}.".format(name)
        )
    if len(editors) > 1:
        raise ValueError(
            "Found multiple editors with name {!r}.".format(name))
    editor, = editors
    return editor
