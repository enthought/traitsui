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


class SimulationError(Exception):
    """ Raised when simulating user interactions on GUI."""
    pass


class EditorNotFound(LookupError, SimulationError):
    """ Raised when an Editor cannot be found by the UI tester or the
    interactor.
    """
    pass


class ActionNotSupported(SimulationError):
    """ Raised when an action is not supported by an interactor.

    Parameters
    ----------
    editor_class : subclass of traitsui.editor.Editor
        Editor class for which the action is targeting.
    action_class : subclass of type
        Any class for the action.
    supported : list of types
        List of supported action types.
    """

    def __init__(self, editor_class, action_class, supported):
        self.editor_class = editor_class
        self.action_class = action_class
        self.supported = supported

    def __str__(self):
        return (
            "No handler is found for editor {!r} with action {!r}. "
            "Supported these: {!r}".format(
                self.editor_class, self.action_class, self.supported
            )
        )
