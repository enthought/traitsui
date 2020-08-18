from traitsui.api import Editor

from traitsui.testing.exceptions import (
    ActionNotSupported, LocationNotSupported,
)


class InteractionRegistry:

    def __init__(self):
        self.editor_to_action_to_handler = {}
        self.editor_to_location_solver = {}

    def register(self, target_class, interaction_class, handler, force=False):
        action_to_handler = self.editor_to_action_to_handler.setdefault(
            target_class, {}
        )
        if interaction_class in action_to_handler and not force:
            raise ValueError(
                "A handler for editor {!r} and action type {!r} already "
                "exists and 'force' is set to false.".format(
                    target_class,
                    interaction_class,
                )
            )
        action_to_handler[interaction_class] = handler

    def get_handler(self, target_class, interaction_class):
        if target_class not in self.editor_to_action_to_handler:
            raise ActionNotSupported(
                target_class=target_class,
                interaction_class=interaction_class,
                supported=[],
            )
        action_to_handler = self.editor_to_action_to_handler[target_class]
        if interaction_class not in action_to_handler:
            raise ActionNotSupported(
                target_class=target_class,
                interaction_class=interaction_class,
                supported=list(action_to_handler),
            )
        return action_to_handler[interaction_class]

    def register_location_solver(self, target_class, locator_class, solver):
        """ Register a callable for resolving location.

        Parameters
        ----------
        target_class : subclass of traitsui.editor.Editor
        locator_class : type
        solver : callable(UIWrapper, location) -> any
            A callable for resolving a location into a new target.
            The location argument will be an instance of locator_class.
        """
        locator_to_solver = self.editor_to_location_solver.setdefault(
            target_class, {}
        )
        if locator_class in locator_to_solver:
            raise ValueError(
                "A solver already exists for {!r} with locator {!r}".format(
                    target_class, locator_class,
                )
            )

        locator_to_solver[locator_class] = solver

    def get_location_solver(self, target_class, locator_class):
        """ Return a solver for the given location.

        Parameters
        ----------
        target_class : subclass of traitsui.editor.Editor
        locator_class : type

        Raises
        ------
        LocationNotSupported
        """
        locator_to_solver = self.editor_to_location_solver.get(
            target_class, {}
        )
        try:
            return locator_to_solver[locator_class]
        except KeyError:
            raise LocationNotSupported(
                target_class=target_class,
                locator_class=locator_class,
                supported=list(locator_to_solver),
            )
