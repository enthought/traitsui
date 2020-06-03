
from contextlib import contextmanager

from pyface.gui import GUI

from traitsui.testing.simulation import (
    get_editor_value, set_editor_value, DEFAULT_REGISTRY,
)
from traitsui.tests._tools import store_exceptions_on_all_threads


class UITester:
    """ This tester is a public API for assisting GUI testing with TraitsUI.

    An instance of UITester can be instantiated inside a test and then be
    used to drive changes on a Traits application via GUI components, imitating
    user interactions. Inspection methods are also defined.

    Note that for a given GUI component, not all types of user interactions are
    possible. The corresponding methods are likely not implemented in that
    sitations.

    ``UITester`` can be used as a context manager. Alternatively its ``start``
    and ``stop`` methods can be used in a test's set up and tear down code.
    """

    def __init__(self, registries=None):
        """ Initialize a tester for testing GUI and traits interaction.

        Parameters
        ----------
        registries : list of SimulatorRegistry, optional
            Registries of simulators for different editors, in the order
            of decreasing priority. A shallow copy will be made.
            Default is a list containing TraitsUI's registry only.
        """
        self.gui = None

        if registries is None:
            self._registries = [DEFAULT_REGISTRY]
        else:
            self._registries = registries.copy()

    def start(self):
        """ Start GUI testing.
        """
        if self.gui is None:
            self.gui = GUI()

    def stop(self):
        """ Stop GUI testing and perform clean up.
        """
        if self.gui is not None:
            with store_exceptions_on_all_threads():
                self.gui.process_events()
        self.gui = None

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, *args, **kwargs):
        self.stop()

    def add_registry(self, registry):
        """ Add a SimulatorRegistry to the top of the registry list, i.e.
        registry with the highest priority.

        Parameters
        ----------
        registry : SimulatorRegistry
        """
        self._registries.insert(0, registry)

    @contextmanager
    def create_ui(self, object, ui_kwargs=None):
        """ Context manager to create a UI and dispose it upon exit.

        ``start`` must have been called prior to calling this method.

        Parameters
        ----------
        object : HasTraits
            An instance of HasTraits for which a GUI will be created.
        ui_kwargs : dict, or None
            Keyword arguments to be provided to ``HasTraits.edit_traits``.

        Yields
        ------
        ui : traitsui.ui.UI
        """
        self._ensure_started()
        if ui_kwargs is None:
            ui_kwargs = {}
        ui = object.edit_traits(**ui_kwargs)
        try:
            yield ui
        finally:
            ui.dispose()

    def get_text(self, ui, name):
        """ Retrieve a text displayed on the GUI component uniquely identified
        by a name (or extended name).

        This method may not be implemented by editors that do not support
        the representation of text.

        Parameters
        ----------
        ui : traitsui.ui.UI
            The UI created, e.g. by ``create_ui``.
        name : str
            A single or an extended name for retreiving an editor on a UI.
            e.g. "attr", "model.attr1.attr2"

        Returns
        -------
        text : str
        """
        return self.get_editor_value(
            ui=ui, name=name, getter=lambda s: s.get_text()
        )

    def set_text(self, ui, name, text, confirmed=True):
        """ Set a text on the GUI component uniquely identified by a name (or
        extended name).

        This method may not be implemented by editors that do not support
        text editing.

        Parameters
        ----------
        ui : traitsui.ui.UI
            The UI created, e.g. by ``create_ui``.
        name : str
            A single or an extended name for retreiving an editor on a UI.
            e.g. "attr", "model.attr1.attr2"
        text : str
            The text to be set.
        confirmed : boolean, optional
            Whether the change is confirmed. e.g. a text editor may require
            the user to hit the return key in order to register the change.
            Useful for testing the absence of events when an editor is
            configured such that no events are fired until the user confirms
            the change.
        """
        self.set_editor_value(
            ui=ui,
            name=name,
            setter=lambda s: s.set_text(text, confirmed=confirmed)
        )

    def get_date(self, ui, name):
        """ Retrieve the date displayed on the GUI component uniquely
        identified by a name (or extended name).

        This method may not be implemented by editors that do not support
        the representation of dates.

        Parameters
        ----------
        ui : traitsui.ui.UI
            The UI created, e.g. by ``create_ui``.
        name : str
            A single or an extended name for retreiving an editor on a UI.
            e.g. "attr", "model.attr1.attr2"

        Returns
        -------
        date : datetime.date
        """
        return self.get_editor_value(
            ui=ui, name=name, getter=lambda s: s.get_date()
        )

    def set_date(self, ui, name, date):
        """ Set a date on the GUI component uniquely identified by a name (or
        extended name).

        This method may not be implemented by editors that do not support
        the representation of dates.

        Parameters
        ----------
        ui : traitsui.ui.UI
            The UI created, e.g. by ``create_ui``.
        name : str
            A single or an extended name for retreiving an editor on a UI.
            e.g. "attr", "model.attr1.attr2"
        date : datetime.date
            The date to be set.
        """
        self.set_editor_value(
            ui=ui, name=name, setter=lambda s: s.set_date(date)
        )

    def click_date(self, ui, name, date):
        """ Perform a click (or toggle) action a GUI component with the given
        date.

        This method may not be implemented by editors that do not support
        the representation of dates.

        Parameters
        ----------
        ui : traitsui.ui.UI
            The UI created, e.g. by ``create_ui``.
        name : str
            A single or an extended name for retreiving an editor on a UI.
            e.g. "attr", "model.attr1.attr2"
        date : datetime.date
            The date to be set.
        """
        self.set_editor_value(
            ui=ui, name=name, setter=lambda s: s.click_date(date)
        )

    def click(self, ui, name):
        """ Perform a click (or toggle) action on a GUI component uniquely
        identified by the given name (or extended name).

        This method may not be implemented by editors that do not respond to
        click events.

        Parameters
        ----------
        ui : traitsui.ui.UI
            The UI created, e.g. by ``create_ui``.
        name : str
            A single or an extended name for retreiving an editor on a UI.
            e.g. "attr", "model.attr1.attr2"
        """
        self.set_editor_value(
            ui=ui, name=name, setter=lambda s: s.click()
        )

    def click_index(self, ui, name, index):
        """ Perform a click (or toggle) action on a GUI component uniquely
        identified by the given name (or extended name). The index should
        uniquely define where the click should occur in the context of the
        GUI component.

        This method may not be implemented by editors that do not respond to
        click events or editors that do not handle sequences.

        Parameters
        ----------
        ui : traitsui.ui.UI
            The UI created, e.g. by ``create_ui``.
        name : str
            A single or an extended name for retreiving an editor on a UI.
            e.g. "attr", "model.attr1.attr2"
        index : int
            A 0-based index to indicate where the click event should occur.
        """
        self.set_editor_value(
            ui=ui, name=name, setter=lambda s: s.click_index(index)
        )

    def set_editor_value(self, ui, name, setter):
        """ General method for setting value(s) on an editor via a simulator.

        Useful for calling a custom method on a custom simulator.

        Parameters
        ----------
        ui : traitsui.ui.UI
            The UI created, e.g. by ``create_ui``.
        name : str
            A single or an extended name for retreiving an editor on a UI.
            e.g. "attr", "model.attr1.attr2"
        setter : callable(BaseSimulator)
            Callable for simulating user interaction on the editor retrieved.
            The callable will receive an instance of a BaseSimulator
            created for the found editor. The simulator type refers to the
            first simulator class found in the registries provided to this
            tester.
        """
        self._ensure_started()
        with store_exceptions_on_all_threads():
            set_editor_value(
                ui, name, setter, self.gui, registries=self._registries)
            self.gui.process_events()

    def get_editor_value(self, ui, name, getter):
        """ General method for getting value(s) on an editor via a simulator.

        Useful for calling a custom method on a custom simulator.

        Parameters
        ----------
        ui : traitsui.ui.UI
            The UI created, e.g. by ``create_ui``.
        name : str
            A single or an extended name for retreiving an editor on a UI.
            e.g. "attr", "model.attr1.attr2"
        getter : callable(BaseSimulator) -> any
            Callable for querying GUI component state on the editor retrieved.
            The callable will receive an instance of a BaseSimulator
            created for the found editor. The simulator type refers to the
            first simulator class found in the registries provided to this
            tester.

        Returns
        -------
        value : any
            Value returned by the getter.
        """
        self._ensure_started()
        with store_exceptions_on_all_threads():
            self.gui.process_events()
            return get_editor_value(
                ui, name, getter, self.gui, registries=self._registries)

    # Private methods

    def _ensure_started(self):
        if self.gui is None:
            raise ValueError(
                "'start' has not been called on {!r}.".format(self))
