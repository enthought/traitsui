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
""" Define top-level object(s) to support testing TraitsUI applications.
"""

import contextlib

from traitsui.testing._gui import process_cascade_events
from traitsui.testing._exception_handling import reraise_exceptions
from traitsui.testing.tester._ui_tester_registry.default_registry import (
    get_default_registry
)
from traitsui.testing.tester.ui_wrapper import UIWrapper


class UITester:
    """ UITester assists testing of GUI applications developed using TraitsUI.

    See :ref:`testing-traitsui-applications` Section in the User Manual for
    further details.

    Parameters
    ----------
    registries : list of TargetRegistry, optional
        Registries of interaction for different targets, in the order
        of decreasing priority. If provided, a shallow copy will be made.
        A default registry is always appended to the list to provide
        builtin support for TraitsUI UI and editors.
    delay : int, optional
        Time delay (in ms) in which actions by the tester are performed. Note
        it is propagated through to created child wrappers. The delay allows
        visual confirmation test code is working as desired. Defaults to 0.
    auto_process_events : bool, optional
        Whether to process (cascade) GUI events automatically. Default is True.
        For tests that launch a modal dialog and rely on a recurring timer to
        poll if the dialog is closed, it may be necessary to set this flag to
        false in order to avoid deadlocks. Note that this is propagated
        through to created child wrappers.

    Attributes
    ----------
    delay : int
        Time delay (in ms) in which actions by the tester are performed. Note
        it is propagated through to created child wrappers. The delay allows
        visual confirmation test code is working as desired.
    """

    def __init__(self, *, registries=None, delay=0, auto_process_events=True):
        if registries is None:
            self._registries = []
        else:
            self._registries = registries.copy()

        # This registry contributes the support for TraitsUI UI and editors.
        # The find_by_name/find_by_id methods in this class also depend on
        # this registry.
        self._registries.append(get_default_registry())
        self.delay = delay
        self._auto_process_events = auto_process_events

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

        ui_kwargs = {} if ui_kwargs is None else ui_kwargs
        ui = object.edit_traits(**ui_kwargs)
        try:
            yield ui
        finally:
            with reraise_exceptions():
                if self._auto_process_events:
                    # At the end of a test, there may be events to be
                    # processed. If dispose happens first, those events will be
                    # processed after various editor states are removed,
                    # causing errors. But if we are asked not to process
                    # events, then don't.
                    process_cascade_events()
                try:
                    ui.dispose()
                finally:
                    # dispose is not atomic and may push more events to the
                    # event queue. Flush those too unless we are asked not to.
                    if self._auto_process_events:
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
        return self._get_wrapper(ui).find_by_name(name=name)

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
        return self._get_wrapper(ui).find_by_id(id=id)

    def _get_wrapper(self, ui):
        """ Return a new UIWrapper wrapping the given traitsui.ui.UI.

        Parameters
        ----------
        ui : traitsui.ui.UI
            The UI created, e.g. by ``create_ui``.

        Returns
        -------
        wrapper : UIWrapper
        """
        return UIWrapper(
            target=ui,
            registries=self._registries,
            delay=self.delay,
            auto_process_events=self._auto_process_events,
        )
