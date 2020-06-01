
class SimulationError(Exception):
    """ Raised when simulating user interactions on GUI."""
    pass


class Disabled(SimulationError):
    """ Raised when a simulation fails because the widget is disabled.
    """
    pass
