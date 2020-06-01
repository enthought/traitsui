
import contextlib


class BaseSimulator:
    """ The base class for all simulators to be used for simulating user
    interactions with GUI components for testing TraitsUI and applications
    written using TraitsUI.

    Each simulator should be associated with one or many specific Editor of
    TraitsUI.

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


#: Default registry for providing default simulators.
REGISTRY = SimulatorRegistry()


def simulate(editor_class, registry=REGISTRY):
    """ Decorator for registering a subclass of BaseSimulator for simulating
    a particular subclass of Editor.

    Parameters
    ----------
    editor_class : subclass of traitsui.editor.Editor
        The Editor class to simulate.
    registry : SimulatorRegistry, optional
        Registry to used. Default is to use a global registry provided
        by TraitsUI.
        To undo a registration, see ``SimulatorRegistry.unregister``.
    """
    def wrapper(simulator_class):
        registry.register(editor_class, simulator_class)
        return simulator_class
    return wrapper


def set_editor_value(ui, name, setter, gui, registry=REGISTRY):
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
    registry : SimulatorRegistry, optional
        The registry from which to find a BaseSimulator for the retrieved
        editor.
    """
    simulator, name = _get_one_simulator(ui=ui, name=name, registry=registry)
    with simulator.get_ui() as alternative_ui:
        if alternative_ui is not NotImplemented:
            set_editor_value(
                ui=alternative_ui,
                name=name,
                setter=setter,
                gui=gui,
                registry=registry,
            )
        else:
            setter(simulator)
        gui.process_events()


def get_editor_value(ui, name, getter, gui, registry=REGISTRY):
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
    registry : SimulatorRegistry, optional
        The registry from which to find a BaseSimulator for the retrieved
        editor.

    Returns
    -------
    value : any
        Any value returned by the getter.
    """
    simulator, name = _get_one_simulator(ui=ui, name=name, registry=registry)
    with simulator.get_ui() as alternative_ui:
        gui.process_events()
        if alternative_ui is not NotImplemented:
            return get_editor_value(
                ui=alternative_ui,
                name=name,
                getter=getter,
                gui=gui,
                registry=registry,
            )
        return getter(simulator)


def _get_one_simulator(ui, name, registry=REGISTRY):
    """ Return one instance of BaseSimulation for an editor uniquely identified
    from the given UI and name.

    Parameters
    ----------
    ui : traitsui.ui.UI
        The UI from which an editor will be retrieved.
    name : str
        A single or an extended name for retreiving an editor on a UI.
        e.g. "attr", "model.attr1.attr2"
    registry : SimulatorRegistry, optional
        The registry from which to find a BaseSimulator for the retrieved
        editor.

    Returns
    -------
    simulator : BaseSimulator
        Simulator for the editor found.
    name : str
        Modified name if the original name is an extended name.

    Raises
    ------
    ValuError
        If zero or more than one editors are found.
    """
    simulators, new_name = _get_simulators(ui=ui, name=name, registry=registry)

    if not simulators:
        raise ValueError(
            "No editors can be found with name {!r}".format(name)
        )
    if len(simulators) > 1:
        raise ValueError("Found multiple editors with name {!r}.".format(name))

    simulator, = simulators
    return simulator, new_name


def _get_simulators(ui, name, registry=REGISTRY):
    """ Return instances of BaseSimulator from an instance of traitsui.ui.UI
    with a given extended name.

    Parameters
    ----------
    ui : traitsui.ui.UI
    name : str
    """
    if "." in name:
        editor_name, name = name.split(".", 1)
    else:
        editor_name = name
    editors = ui.get_editors(editor_name)

    simulators = [
        registry.get_simulator_class(editor.__class__)(editor)
        for editor in editors
    ]
    return simulators, name
