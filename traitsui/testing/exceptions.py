
class SimulationError(Exception):
    """ Raised when simulating user interactions on GUI."""
    pass


class Disabled(SimulationError):
    """ Raised when a simulation fails because the widget is disabled.
    """
    pass


class ActionNotSupported(SimulationError):
    """ Raised when an action is not supported by an interactor.
    """

    def __init__(self, target_class, interaction_class, supported):
        self.target_class = target_class
        self.interaction_class = interaction_class
        self.supported = supported

    def __str__(self):
        return (
            "No handler is found for editor {!r} with action {!r}. "
            "Supported these: {!r}".format(
                self.target_class, self.interaction_class, self.supported
            )
        )


class LocationNotSupported(SimulationError):
    """ Raised when attempt to resolve a location on a UI fails
    because the location type is not supported.
    """

    def __init__(self, target_class, locator_class, supported):
        self.target_class = target_class
        self.locator_class = locator_class
        self.supported = supported

    def __str__(self):
        return (
            "Location {!r} is not supported for {!r}. "
            "Supported these: {!r}".format(
                self.locator_class, self.target_class, self.supported
            )
        )
