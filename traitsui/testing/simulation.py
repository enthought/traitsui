
import contextlib

_TRAITSUI, _ = __name__.split(".", 1)


class BaseSimulator:
    """ The base class whose subclasses are responsible simulating user
    interactions with a specific GUI component. This is typically used for
    testing GUI applications written using TraitsUI.

    Each simulator subclass can be associated with one or many toolkit specific
    subclasses of Editor. Each instance of a BaseSimulator should be associated
    with a single instance of Editor in a UI.

    Concrete implementations should aim at programmatically triggering UI
    events by manipulating UI components, e.g. clicking a button, instead of
    calling event handlers on an editor.

    Methods for simulating user interactions are optional. Whether they are
    implemented depends on the context of an editor.

    A simulator targeting a DateEditor may support setting a date or a
    text but not an index, whereas a simulator targeting an EnumEditor may
    support setting a text and an index but not a date.

    Attributes
    ----------
    editor : Editor
        An instance of Editor. It is assumed to have a valid, non-None GUI
        widget in its ``control`` attribute.
    """

    def __init__(self, editor):
        self.editor = editor

    @contextlib.contextmanager
    def get_ui(self):
        """ A context manager to yield an instance of traitsui.ui.UI for
        delegating actions to.

        Subclass may override this method, e.g. to delegate actions or queries
        on a different simulator. Default implementation is to yield
        NotImplemented and perform no additional clean ups; the original UI
        will be used.

        Yields
        ------
        ui : traitsui.ui.UI or NotImplemeneted
        """
        yield NotImplemented

    def get_text(self):
        """ Return the text value being presented by the editor.

        This is an optional method. Subclass may not have implemented this
        method if it is not applicable for the editor.

        Returns
        -------
        text : str

        Raises
        ------
        SimulationError
        """
        raise NotImplementedError(
            "{!r} has not implemented 'get_text'.".format(self.__class__)
        )

    def set_text(self, text, confirmed=True):
        """ Set the text value for an editor.

        This is an optional method. Subclass may not have implemented this
        method if it is not applicable for the editor.

        Parameters
        ----------
        text : str
            Text to be set on the GUI component.
        confirmed : boolean, optional
            Whether the text change is confirmed. Useful for testing the absent
            of events when ``auto_set`` is set to false. Default is to confirm
            the change.

        Raises
        ------
        SimulationError
        """
        raise NotImplementedError(
            "{!r} has not implemented 'set_text'.".format(self.__class__)
        )

    def get_date(self):
        """ Return the date value being presented by the editor.

        This is an optional method. Subclass may not have implemented this
        method if it is not applicable for the editor.

        Returns
        -------
        date : datetime.date

        Raises
        ------
        SimulationError
        """
        raise NotImplementedError(
            "{!r} has not implemented 'get_date'.".format(self.__class__)
        )

    def set_date(self, date):
        """ Set the date value for an editor.

        This is an optional method. Subclass may not have implemented this
        method if it is not applicable for the editor.

        Parameters
        ----------
        date : datetime.date

        Raises
        ------
        SimulationError
        """
        raise NotImplementedError(
            "{!r} has not implemented 'set_date'.".format(self.__class__)
        )

    def click_date(self, date):
        """ Perform a click event on the GUI component where it can be uniquely
        identified by a date.

        This is an optional method. Subclass may not have implemented this
        method if it is not applicable for the editor.

        Parameters
        ----------
        date : datetime.date

        Raises
        ------
        SimulationError
        """
        raise NotImplementedError(
            "{!r} has not implemented 'click_date'.".format(self.__class__)
        )

    def click(self):
        """ Perform a click event on the editor.

        This is an optional method. Subclass may not have implemented this
        method if it is not applicable for the editor.

        Raises
        ------
        SimulationError
        """
        raise NotImplementedError(
            "{!r} has not implemented 'click'.".format(self.__class__)
        )

    def click_index(self, index):
        """ Perform a click event on the GUI component where it can be uniquely
        identified by a 0-based index.

        This is an optional method. Subclass may not have implemented this
        method if it is not applicable for the editor.

        Parameters
        ----------
        index : int

        Raises
        ------
        SimulationError
        """
        raise NotImplementedError(
            "{!r} has not implemented 'click_index'.".format(self.__class__)
        )


# -----------------------------
# Simulator registration
# -----------------------------

class SimulatorRegistry:
    """ A registry for mapping toolkit-specific Editor class to a subclass
    of BaseSimulator.

    When an instance of Editor is retrieved from a UI, this registry will
    provide the simulator class approprites for simulating user actions.
    """

    def __init__(self):
        self.editor_to_simulator = {}

    def register(self, editor_class, simulator_class):
        """ Register a subclass of BaseSimulator to a subclass of Editor.

        Parameters
        ----------
        editor_class : subclass of traitsui.editor.Editor
            The Editor class to simulate.
        simulator_class : subclass of BaseSimulator
            The simulator class.
        """

        if editor_class in self.editor_to_simulator:
            raise ValueError(
                "{!r} was already registered.".format(editor_class)
            )
        self.editor_to_simulator[editor_class] = simulator_class

    def unregister(self, editor_class, simulator_class=None):
        """ Reverse the register action.

        Parameters
        ----------
        editor_class : subclass of traitsui.editor.Editor
            The Editor class to simulate.
        simulator_class : subclass of BaseSimulator, optional.
            The simulator class. If provided and the target simulator class
            does not match the provided one, an error will be raised and
            no unregistration is performed.
        """
        to_be_removed = self.editor_to_simulator[editor_class]
        if simulator_class is not None and to_be_removed is not simulator_class:
            raise ValueError(
                "Provided {!r} does not matched the registered {!r}".format(
                    simulator_class, to_be_removed
                ))
        del self.editor_to_simulator[editor_class]

    def get_simulator_class(self, editor_class):
        """ Retrieve the simulator class for a given instance of Editor
        subclass.

        Parameters
        ----------
        editor_class : subclass of traitsui.editor.Editor
            The Editor class to simulate.

        Raises
        ------
        KeyError
        """
        try:
            return self.editor_to_simulator[editor_class]
        except KeyError:
            # Re-raise for a better error message.
            raise KeyError(
                "No simulators can be found for {!r}".format(editor_class)
            ) from None


#: Registry for providing traitsui default simulators.
DEFAULT_REGISTRY = SimulatorRegistry()


def simulate(editor_class, registry):
    """ Decorator for registering a subclass of BaseSimulator for simulating
    a particular subclass of Editor.

    When this decorator is used outside of TraitsUI, it is highly recommended
    that a separate registry is used instead of TraitsUI's default registry.
    This will prevent conflicts with default simulators being contributed by
    TraitsUI now or in the future.

    See ``UITester`` for supplying a list of registries to try in the order
    of priority.

    Parameters
    ----------
    editor_class : subclass of traitsui.editor.Editor
        The Editor class to simulate.
    registry : SimulatorRegistry
        Registry to be used for mapping the editor to the simulator.
    """
    def wrapper(simulator_class):
        registry.register(editor_class, simulator_class)
        return simulator_class
    return wrapper


def set_editor_value(ui, name, setter, gui, registries):
    """ Perform actions to modify GUI components.

    Parameters
    ----------
    ui : traitsui.ui.UI
        The UI from which an editor will be retrieved.
    name : str
        An extended name for retreiving an editor on a UI.
        e.g. "model.attr1.attr2"
    setter : callable(BaseSimulator)
        Callable to perform simulation.
    gui : pyface.gui.GUI
        Object for driving the GUI event loop.
    registries : list of SimulatorRegistry
        The registries from which to find a BaseSimulator for the retrieved
        editor. The first registry that returns a simulator will stop other
        registries from being used.
    """
    editor, name = _get_editor(ui, name)
    editor_class = editor.__class__

    exceptions = []

    for simulator_class in _iter_simulator_classes(registries, editor_class):
        simulator = simulator_class(editor)
        with simulator.get_ui() as alternative_ui:
            try:
                if alternative_ui is not NotImplemented:
                    set_editor_value(
                        ui=alternative_ui,
                        name=name,
                        setter=setter,
                        gui=gui,
                        registries=registries,
                    )
                else:
                    setter(simulator)

            except NotImplementedError as e:
                exceptions.append(e)
                continue
            else:
                gui.process_events()
                return

    raise NotImplementedError(
        "No implementation found for simulating {!r}. "
        "These simulators are tried:\n{}".format(
            editor,
            "\n".join(str(exception) for exception in exceptions)
        )
    )


def get_editor_value(ui, name, getter, gui, registries):
    """ Perform a query on GUI components for inspection purposes.

    Parameters
    ----------
    ui : traitsui.ui.UI
        The UI from which an editor will be retrieved.
    name : str
        An extended name for retreiving an editor on a UI.
        e.g. "model.attr1.attr2"
    getter : callable(BaseSimulator) -> any
        Callable to retrieve value or values from the GUI.
    gui : pyface.gui.GUI
        Object for driving the GUI event loop.
    registries : list of SimulatorRegistry
        The registries from which to find a BaseSimulator for the retrieved
        editor. The first registry that returns a simulator will stop other
        registries from being used.

    Returns
    -------
    value : any
        Any value returned by the getter.
    """
    editor, name = _get_editor(ui, name)
    editor_class = editor.__class__

    exceptions = []

    for simulator_class in _iter_simulator_classes(registries, editor_class):
        simulator = simulator_class(editor)
        with simulator.get_ui() as alternative_ui:
            gui.process_events()
            try:
                if alternative_ui is not NotImplemented:
                    return get_editor_value(
                        ui=alternative_ui,
                        name=name,
                        getter=getter,
                        gui=gui,
                        registries=registries,
                    )
                else:
                    return getter(simulator)

            except NotImplementedError as e:
                exceptions.append(e)
                continue

    raise NotImplementedError(
        "No implementation found for simulating {!r}. "
        "These simulators are tried:\n{}".format(
            editor,
            "\n".join(str(exception) for exception in exceptions)
        )
    )


def _iter_simulator_classes(registries, editor_class):
    """ For a given list of SimulatorRegistry, yield all the simulator classes
    for the given Editor class.

    Parameters
    ----------
    registries : list of SimulatorRegistry
        List of registries to obtain simulators from.
    editor_class : traitsui.ui.editor.Editor
        The editor class to obtain simulators for.

    Yields
    ------
    simulator_class : subclass of BaseSimulator
    """
    for registry in registries:
        try:
            yield registry.get_simulator_class(editor_class)
        except KeyError:
            continue


def _get_editors(ui, name):
    """ Return a list of Editor from an instance of traitsui.ui.UI
    with a given extended name.

    Parameters
    ----------
    ui : traitsui.ui.UI
        The UI from which an editor will be retrieved.
    name : str
        A single or an extended name for retreiving an editor on a UI.
        e.g. "attr", "model.attr1.attr2"

    Returns
    -------
    editors : list of Editor
        The editors found. The list may be empty.
    """
    if "." in name:
        editor_name, name = name.split(".", 1)
    else:
        editor_name = name
    return ui.get_editors(editor_name), name


def _get_editor(ui, name):
    """ Return a single Editor from an instance of traitsui.ui.UI with
    a given extended name. Raise if zero or many editors are found.

    Parameters
    ----------
    ui : traitsui.ui.UI
        The UI from which an editor will be retrieved.
    name : str
        A single or an extended name for retreiving an editor on a UI.
        e.g. "attr", "model.attr1.attr2"

    Returns
    -------
    editor : Editor
        The single editor found.
    name : str
        Modified name if the original name is an extended name.
    """
    editors, new_name = _get_editors(ui, name)
    if not editors:
        raise ValueError(
            "No editors can be found with name {!r}".format(name)
        )
    if len(editors) > 1:
        raise ValueError("Found multiple editors with name {!r}.".format(name))
    editor, = editors
    return editor, new_name
