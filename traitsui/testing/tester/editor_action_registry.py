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

from traitsui.testing.tester.abstract_registry import AbstractRegistry
from traitsui.testing.tester.exceptions import ActionNotSupported


class EditorActionRegistry(AbstractRegistry):
    """ A registry for mapping from editor type + action type to a specific
    implementation for simulating user interaction.

    The action type can be a subclass of any type. There are a few pre-defined
    action types in
    - ``traitsui.testing.tester.command``
    - ``traitsui.testing.tester.query``

    For example, to simulate clicking a button in TraitsUI's ButtonEditor, the
    implementation for Qt may look like this::

        def mouse_click_qt_button(interactor, action):
            # interactor is an instance of UserInteractor
            interactor.editor.control.click()

    The functon can then be registered with the editor class and an action
    type::

        registry = EditorActionRegistry()
        registry.register(
            editor_class=traitsui.qt4.button_editor.SimpleEditor,
            action_class=traitsui.testing.tester.command.MouseClick,
            handler=mouse_click_qt_button,
        )

    Similarly, a wx implementation of clicking a button can be registered
    to the registry (the content of ``mouse_click_wx_button`` is not shown)::

        registry.register(
            editor_class=traitsui.wx.button_editor.SimpleEditor,
            action_class=traitsui.testing.tester.command.MouseClick,
            handler=mouse_click_wx_button,
        )

    Then this registry can be used with the ``UITester`` to support toolkit
    agnostic test code.
    """

    def __init__(self):
        # dict(Editor subclass, dict(action type, callable))
        self._editor_to_action_to_handler = {}

    def register(self, editor_class, action_class, handler):
        """ Register a handler for a given Editor subclass and action type.

        Parameters
        ----------
        editor_class : subclass of traitsui.editor.Editor
            A toolkit specific Editor class.
        action_class : subclass of type
            Any class.
        handler : callable(UserInteractor, action) -> any
            The function to handle the particular action on an editor.
            ``action`` should be an instance of ``action_class``.

        Raises
        ------
        ValueError
            If a handler has already be registered for the same editor class
            and action class.
        """
        action_to_handler = self._editor_to_action_to_handler.setdefault(
            editor_class, {}
        )
        if action_class in action_to_handler:
            raise ValueError(
                "A handler for editor {!r} and action type {!r} already "
                "exists.".format(editor_class, action_class)
            )
        action_to_handler[action_class] = handler

    # Interface of AbstractRegistry -------------------------------------------

    def get_handler(self, editor_class, action_class):
        """ Return a callable for handling an action for a given editor class.

        Parameters
        ----------
        editor_class : subclass of traitsui.editor.Editor
            A toolkit specific Editor class.
        action_class : subclass of type
            Any class.

        Returns
        -------
        handler : callable(UserInteractor, action) -> any
            The function to handle the particular action on an editor.
            ``action`` should be an instance of ``action_class``.
        """
        if editor_class not in self._editor_to_action_to_handler:
            raise ActionNotSupported(
                editor_class=editor_class,
                action_class=action_class,
                supported=[],
            )
        action_to_handler = self._editor_to_action_to_handler[editor_class]
        if action_class not in action_to_handler:
            raise ActionNotSupported(
                editor_class=editor_class,
                action_class=action_class,
                supported=list(action_to_handler),
            )
        return action_to_handler[action_class]
