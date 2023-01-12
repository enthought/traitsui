# (C) Copyright 2004-2023 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

from traitsui.testing.tester.locator import TargetById, TargetByName


def _get_editor_by_name(ui, name):
    """Return a single Editor from an instance of traitsui.ui.UI with
    a given extended name. Raise if zero or many editors are found.

    Parameters
    ----------
    ui : traitsui.ui.UI
        The UI from which an editor will be retrieved.
    name : str
        A single name for retrieving an editor on a UI.

    Returns
    -------
    editor : Editor
        The single editor found.
    """
    editors = ui.get_editors(name)

    all_names = [editor.name for editor in ui._editors]
    if not editors:
        raise ValueError(
            "No editors can be found with name {!r}. "
            "Found these: {!r}".format(name, all_names)
        )
    if len(editors) > 1:
        raise ValueError("Found multiple editors with name {!r}.".format(name))
    (editor,) = editors
    return editor


def _get_editor_by_id(ui, id):
    """Return single Editor from an instance of traitsui.ui.UI with
    the given identifier.

    Parameters
    ----------
    ui : traitsui.ui.UI
        The UI from which an editor will be retrieved.
    id : str
        Id for finding an item in the UI.

    Returns
    -------
    editor : Editor
        The single editor found.
    """
    try:
        editor = getattr(ui.info, id)
    except AttributeError:
        raise ValueError(
            "No editors found with id {!r}. Got these: {!r}".format(
                id, ui._names
            )
        )
    return editor


def register_traitsui_ui_solvers(registry, target_class, traitsui_ui_getter):
    """Function to register solvers for obtaining nested targets inside a
    traitsui.ui.UI inside a (parent) target.

    For example, an instance of TreeEditor may contain a nested
    ``traitsui.ui.UI`` instance. In that case, the ``target_class`` will the
    TreeEditor and the ``traitsui_ui_getter`` specifies how to obtain the
    nested ``traitsui.ui.UI`` UI from it.

    Parameters
    ----------
    registry : TargetRegistry
        The registry being registered to
    target_class : subclass of type
        The type of a UI target being used as the target_class for the
        solvers
    traitsui_ui_getter : callable(target: target_class) -> traitsui.ui.UI
        A callable specific to the particular target_class to obtain a nested
        UI.
    """

    registry.register_location(
        target_class=target_class,
        locator_class=TargetByName,
        solver=lambda wrapper, location: (
            _get_editor_by_name(
                ui=traitsui_ui_getter(wrapper._target),
                name=location.name,
            )
        ),
    )
    registry.register_location(
        target_class=target_class,
        locator_class=TargetById,
        solver=lambda wrapper, location: (
            _get_editor_by_id(
                ui=traitsui_ui_getter(wrapper._target),
                id=location.id,
            )
        ),
    )
