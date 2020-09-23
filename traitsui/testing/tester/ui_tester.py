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
import contextlib

from traitsui.ui import UI
from traitsui.testing._gui import process_cascade_events
from traitsui.testing._exception_handling import reraise_exceptions
from traitsui.testing.tester._ui_tester_register.default_registry import get_default_registry
from traitsui.testing.tester.registry import TargetRegistry
from traitsui.testing.tester._ui_tester_register._traitsui_ui import (
    register_traitsui_ui_solvers,
)
from traitsui.testing.tester.ui_wrapper import UIWrapper


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
    to locate a specific UI target::

        obj = App()
        tester = UITester()
        with tester.create_ui(obj) as ui:
            wrapper = tester.find_by_name(ui, "text")

    The returned value is an instance of ``UIWrapper``. It wraps the
    UI target instance found and allows further test actions to be performed on
    the target.

    Performing an interaction (commands)
    ------------------------------------
    After locating the GUI element, we typically want to perform some user
    actions on it for testing. Examples of user interactions that produce side
    effects are clicking or double clicking a mouse button, typing some keys
    on the keyboard, etc.

    To perform an interaction for side effects, call the ``UIWrapper.perform``
    method with the interaction required. A set of predefined command types can
    be found in the ``traitsui.testing.tester.command``.

    Example::

        with tester.create_ui(app, dict(view=view)) as ui:
            tester.find_by_name(ui, "button").perform(command.MouseClick())
            assert app.clicked

    Inspecting GUI element (queries)
    --------------------------------
    Sometimes, the test may want to inspect visual elements on the GUI, e.g.
    checking if a textbox has displayed the expected value.

    To perform an interaction for queries, call the ``UIWrapper.inspect``
    method with the query required. A set of predefined query types can be
    found in the ``traitsui.testing.tester.query``.

    Example::

        with tester.create_ui(app, dict(view=view)) as ui:
            text = (
                tester.find_by_name(ui, "text").inspect(query.DisplayedText())
            )
            assert text == "Hello"

    Extending the API
    -----------------
    The API can be extended by defining a registry for mapping target and
    interaction types to a specific implementation that handles the
    interaction.

    For example, suppose there is a custom UI target ``MyEditor``, to implement
    a custom interaction type ``ManyMouseClick`` for this target::

        custom_registry = TargetRegistry()
        custom_registry.register_handler(
            target_class=MyEditor,
            interaction_class=ManyMouseClick,
            handler=lambda wrapper, interaction: wrapper._target.do_something()
        )

    Then the registry can be used in a UITester::

        tester = UITester(registries=[custom_registry])

    This is how TraitsUI supplies testing support for specific editors; the
    default setup of ``UITester`` comes with a registry for testing TraitsUI
    editors.

    Similar the location resolution logic can be extended.

    See documentation on ``TargetRegistry`` for details.

    Parameters
    ----------
    registries : list of TargetRegistry, optional
        Registries of interaction for different targets, in the order
        of decreasing priority. If provided, a shallow copy will be made.
        Default registries are always appended to the list to provide
        builtin support for TraitsUI UI and editors.
    delay : int, optional
        Time delay (in ms) in which actions by the tester are performed. Note
        it is propagated through to created child wrappers. The delay allows
        visual confirmation test code is working as desired. Defaults to 0.

    Attributes
    ----------
    delay : int
        Time delay (in ms) in which actions by the tester are performed. Note
        it is propagated through to created child wrappers. The delay allows
        visual confirmation test code is working as desired.
    """

    def __init__(self, registries=None, delay=0):
        if registries is None:
            self._registries = []
        else:
            self._registries = registries.copy()

        # The find_by_name method in this class depends on this registry
        self._registries.append(_get_ui_registry())
        self._registries.append(get_default_registry())
        self.delay = delay

    @contextlib.contextmanager
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
        # Nothing here uses UITester, but it is an instance method to preserve
        # options to extend using instance states.

        ui_kwargs = {} if ui_kwargs is None else ui_kwargs
        ui = object.edit_traits(**ui_kwargs)
        try:
            yield ui
        finally:
            with reraise_exceptions():
                # At the end of a test, there may be events to be processed.
                # If dispose happens first, those events will be processed
                # after various editor states are removed, causing errors.
                process_cascade_events()
                try:
                    ui.dispose()
                finally:
                    # dispose is not atomic and may push more events to the
                    # event queue. Flush those too.
                    process_cascade_events()

    def find_by_name(self, ui, name):
        """ Find the TraitsUI editor with the given name and return a new
        ``UIWrapper`` object for further interactions with the editor.

        Parameters
        ----------
        ui : traitsui.ui.UI
            The UI created, e.g. by ``create_ui``.
        name : str
            A single name for retrieving a target on a UI.

        Returns
        -------
        wrapper : UIWrapper
        """
        return UIWrapper(
            target=ui,
            registries=self._registries,
            delay=self.delay,
        ).find_by_name(name=name)

    def find_by_id(self, ui, id):
        """ Find the TraitsUI editor with the given identifier and return a new
        ``UIWrapper`` object for further interactions with the editor.

        Parameters
        ----------
        ui : traitsui.ui.UI
            The UI created, e.g. by ``create_ui``.
        id : str
            Id for finding an item in the UI.

        Returns
        -------
        wrapper : UIWrapper
        """
        return UIWrapper(
            target=ui,
            registries=self._registries,
            delay=self.delay,
        ).find_by_id(id=id)


def _get_ui_registry():
    """ Return a TargetRegistry with traitsui.ui.UI as the target.

    Parameters
    ----------
    registry : TargetRegistry
    """

    registry = TargetRegistry()
    register_traitsui_ui_solvers(
        registry=registry,
        target_class=UI,
        traitsui_ui_getter=lambda target: target,
    )
    return registry
