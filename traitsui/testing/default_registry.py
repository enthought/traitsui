import importlib

from pyface.base_toolkit import find_toolkit

from traitsui.ui import UI
from traitsui.testing import locator, command
from traitsui.testing.interactor_registry import InteractionRegistry


def get_default_registries():
    # side-effect to determine current toolkit
    package = find_toolkit("traitsui.testing")
    module = importlib.import_module(".default_registry", package.__name__)
    return [
        module.get_default_registry(),
    ]


def _get_editor_by_id(ui, id):
    """ Return aan editor identified by a id.

    Parameters
    ----------
    ui : traitsui.ui.UI
        The UI from which an editor will be retrieved.
    id : str
        Id for finding an item in the UI.
    """
    try:
        editor = getattr(ui.info, id)
    except AttributeError:
        raise ValueError(
            "No editors found with id {!r}. Got these: {!r}".format(
                id, ui._names)
            )
    return editor


def _get_editor_by_name(ui, name):
    """ Return a single Editor from an instance of traitsui.ui.UI with
    a given extended name. Raise if zero or many editors are found.

    Parameters
    ----------
    ui : traitsui.ui.UI
        The UI from which an editor will be retrieved.
    name : str
        A single name for retreiving an editor on a UI.

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
        raise ValueError(
            "Found multiple editors with name {!r}.".format(name))
    editor, = editors
    return editor


def _resolve_ui_editor_by_id(interactor, location):
    return _get_editor_by_id(interactor.editor, location.id)


def _resolve_ui_editor_by_name(interactor, location):
    return _get_editor_by_name(interactor.editor, location.name)


def get_ui_registry():
    """ Return a registry for traitsui.ui.UI only.
    """
    registry = InteractionRegistry()
    registry.register_location_solver(
        target_class=UI,
        locator_class=locator.TargetById,
        solver=_resolve_ui_editor_by_id,
    )
    registry.register_location_solver(
        target_class=UI,
        locator_class=locator.TargetByName,
        solver=_resolve_ui_editor_by_name,
    )
    registry.register_location_solver(
        target_class=UI,
        locator_class=locator.NestedUI,
        solver=lambda interactor, _: interactor.editor,
    )
    return registry
