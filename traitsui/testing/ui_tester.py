
from contextlib import contextmanager

from traitsui.tests._tools import (
    create_ui as _create_ui,
    process_cascade_events,
    reraise_exceptions,
)
from traitsui.testing import command
from traitsui.testing import locator
from traitsui.testing.exceptions import (
    ActionNotSupported,
    LocationNotSupported,
)
from traitsui.testing.default_registry import (
    get_default_registries,
    get_ui_registry,
)


@contextmanager
def event_processed():
    """ Context manager to ensure GUI events are processed upon entering
    and exiting the context.
    """
    with reraise_exceptions():
        process_cascade_events()
    try:
        yield
    finally:
        with reraise_exceptions():
            process_cascade_events()


class UITester:
    """ This tester is a public API for assisting GUI testing with TraitsUI.

    An instance of UITester can be instantiated inside a test and then be
    used to drive changes on a TraitsUI application via GUI components. It
    performs actions that imitate what a user may do or see in a GUI,
    e.g. clicking a button, checking the text shown in a particular textbox.

    There are two main functions on the ``UITester``:

    - ``find_by_name``: Find an editor with the given extended name.
      This locates the editor the developer would like to simulate user
      interactions on. In order to use this function, the editor must be
      uniquely identifiable by the given extended name.
    - ``perform``: Perform the required user interaction.
      This function makes sure that any pending GUI events are processed before
      and after the action takes place. It also captures and reraises any
      uncaught exceptions, as they may not otherwise have caused a test to
      fail.

    Example::

        from traitsui.testing.api import command, UITester

        class App(HasTraits):

            button = Button()
            clicked = Bool(False)

            def _button_fired(self):
                self.clicked = True

        app = App()
        view = View(Item("button"))
        tester = UITester()
        with tester.create_ui(app, dict(view=view)) as ui:
            tester.find_by_name(ui, "button").perform(command.MouseClick())
            assert app.clicked

    While user interactions are being simulated programmatically, this does not
    fully replace manual testing by an actual human. In particular, platform
    specific differences may not be taken into account.

    ``UITester`` can be used alongside other testing facilities such as
    the ``GuiTestAssistant`` and ``ModalDialogTester``, to achieve other
    testing objectives.

    ``UITester.perform`` accepts an action object which is defined in
    ``traitsui.testing.api.command`` or ``traitsui.testing.api.query``. Note
    that for a given editor, not all actions are supported, e.g. a button would
    not support an action for entering some text. In those circumstances, an
    error will be raised with suggestions on what actions are supported.
    Custom actions can be defined via an instance of ``InteractionRegistry``
    provided to the ``UITester``.

    For example::

        class MyAction:
            pass

        class MyEditor(Editor):
            ...

        def click(interactor, action):
            # ``interactor`` is an instance of UIWrapper
            interactor.editor.control.click()

        my_registry = InteractionRegistry()
        my_registry.register(
            target_class=MyEditor, interaction_class=MyAction, handler=click,
        )

        def test_something(ui):
            tester = UITester()
            tester.add_registry(my_registry)
            tester.find_by_name(ui, "some_name").perform(MyAction())

    What the registry pattern replaces is the following alternative::

        with capture_and_reraise_exceptions():
            GUI.process_events()
            try:
                UITester().find_by_name(ui, "some_name").editor.control.click()
            finally:
                GUI.process_events()

    The benefits of using a registry:
    (1) Toolkit specific implementation are managed by the registry.
        Test code using ``UITester`` can be kept toolkit agnostic.
    (2) Event processing and exception handling capabilities can be reused.
    """

    def __init__(self, registries=None, delay=0):
        """ Initialize a tester for testing GUI and traits interaction.

        Parameters
        ----------
        registries : list of InteractionRegistry, optional
            Registries of interactors for different editors, in the order
            of decreasing priority. A shallow copy will be made.
            Default is a list containing TraitsUI's registry only.
        """

        if registries is None:
            self._registries = get_default_registries()
        else:
            self._registries = registries.copy()
        self._registries.append(get_ui_registry())
        self.delay = delay

    def add_registry(self, registry):
        """ Add a InteractionRegistry to the top of the registry list, i.e.
        registry with the highest priority.

        Parameters
        ----------
        registry : InteractionRegistry
        """
        self._registries.insert(0, registry)

    def create_ui(self, object, ui_kwargs=None):
        """ Context manager to create a UI and dispose it upon exit.

        ``start`` must have been called prior to calling this method.

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
        ``InteractionRegistry`` in this tester is used for finding the editor
        specified.

        Parameters
        ----------
        ui : traitsui.ui.UI
            The UI created, e.g. by ``create_ui``.
        name : str
            A single or an extended name for retreiving an editor on a UI.
            e.g. "attr", "model.attr1.attr2"

        Returns
        -------
        interactor : BaseUserInteractor
        """
        return (
            self._get_ui_interactor(ui).locate(locator.TargetByName(name=name))
        )

    def find_by_id(self, ui, id):
        """ Find the UI editor with the given identifier and return an object
        for simulating user interactions with the editor. The list of
        ``InteractionRegistry`` in this tester is used for finding the editor
        specified.

        Parameters
        ----------
        ui : traitsui.ui.UI
            The UI created, e.g. by ``create_ui``.
        id : str
            Id for finding an item in the UI.

        Returns
        -------
        interactor : BaseUserInteractor
        """
        return self._get_ui_interactor(ui).locate(locator.TargetById(id=id))

    def _get_ui_interactor(self, ui):
        return UIWrapper(
            editor=ui,
            registries=self._registries,
            delay=self.delay,
        )


class UIWrapper:
    """
    An ``UIWrapper`` is responsible for dispatching specified user
    interactions to toolkit specific implementations in order to test a GUI
    component written using TraitsUI.

    Each instance of ``UIWrapper`` wraps an instance of Editor obtained
    from a UI object. The editor should be in the state where the GUI has been
    initialized and has not been disposed of such that it accepts user
    commands.

    A ``UIWrapper`` finds toolkit specific implementations for simulating
    user interactions from one or many ``InteractionRegistry`` objects. These
    registries are typically provided via another public interface, e.g.
    ``UITester``.

    Attributes
    ----------
    editor : Editor
        An instance of Editor. It is assumed to be in a state after the UI
        has been initialized but before it is disposed of.
    """

    def __init__(
            self, editor, registries, delay=0, ancestor=None):
        self.editor = editor
        self.registries = registries.copy()
        self.delay = delay
        self.ancestor = ancestor

    def perform(self, action):
        """ Perform a user action that causes side effects.

        Parameters
        ----------
        action : object
            An action instance that defines the user action.
            See ``traitsui.testing.command`` module for builtin
            query objects.
            e.g. ``traitsui.testing.command.MouseClick``
        """
        self._resolve(
            lambda interactor: interactor._perform_or_inspect(action),
            catches=ActionNotSupported,
        )

    def inspect(self, action):
        """ Return a value or values for inspection.

        Parameters
        ----------
        action : object
            An action instance that defines the inspection.
            See ``traitsui.testing.query`` module for builtin
            query objects.
            e.g. ``traitsui.testing.query.DisplayedText``
        """
        return self._resolve(
            lambda interactor: interactor._perform_or_inspect(action),
            catches=ActionNotSupported,
        )

    def locate(self, location):
        """ Return a new interactor for performing user actions on a specific
        location specified.

        Implementations must validate the type of the location given.
        However, it is optional for the implementation to resolve the given
        location on the current UI at this stage.

        Parameters
        ----------
        location : Location
        """
        return self._resolve(
            lambda interactor: interactor._new_from_location(location),
            catches=LocationNotSupported,
        )

    def find_by_name(self, name):
        """ Find the next target using a given name.

        Note that this is not a recursive search.

        Parameters
        ----------
        name : str
            A single name for retreiving the next target.

        Returns
        -------
        interactor : UIWrapper
        """
        return self.locate(locator.TargetByName(name=name))

    def find_by_id(self, id):
        """ Find the next target using a unique identifier.

        Note that this is not a recursive search.

        Parameters
        ----------
        id : any
            An object for uniquely identifying target.

        Returns
        -------
        interactor : UIWrapper
        """
        return self.locate(locator.TargetById(id=id))

    def _resolve(self, function, catches):
        """ Execute the given callable with this interactor, if fails, try
        again with the default target (if there is one).

        Parameters
        ----------
        function : callable(UIWrapper) -> any
            Function to resolve.
        catches : Exception or tuple of Exception
            Exceptions to catch and then retry with the default target.

        Returns
        -------
        value : any
            Returned value from the given function.
        """
        try:
            return function(self)
        except catches as e:
            try:
                default = self._new_from_location(locator.DefaultTarget())
            except LocationNotSupported:
                raise e
            else:
                return function(default)

    def _new_from_location(self, location):
        """ Attempt to resolve the given location and return a new
        UIWrapper.

        Parameters
        ----------
        location : Location

        Raises
        ------
        LocationNotSupported
            If the given location is not supported.
        """
        handler = self._resolve_location_solver(location)
        return UIWrapper(
            editor=handler(self, location),
            registries=self.registries,
            delay=self.delay,
            ancestor=self,
        )

    def _resolve_location_solver(self, location):
        supported = set()
        for registry in self.registries:
            try:
                return registry.get_location_solver(
                    self.editor.__class__,
                    location.__class__,
                )
            except LocationNotSupported as e:
                supported |= set(e.supported)

        raise LocationNotSupported(
            target_class=self.editor.__class__,
            locator_class=location.__class__,
            supported=list(supported),
        )

    def _resolve_handler(self, action):
        interaction_class = action.__class__
        supported = set()
        for registry in self.registries:
            try:
                return registry.get_handler(
                    target_class=self.editor.__class__,
                    interaction_class=interaction_class,
                )
            except ActionNotSupported as e:
                supported |= set(e.supported)

        raise ActionNotSupported(
            target_class=self.editor.__class__,
            interaction_class=action.__class__,
            supported=list(supported),
        )

    def _perform_or_inspect(self, action):
        """ Perform a user action or a user inspection.
        """
        handler = self._resolve_handler(action)
        with event_processed():
            return handler(self, action)
