from traitsui.testing import locator


def find_by_id_in_nested_ui(interactor, location):
    new_interactor = interactor.locate(locator.NestedUI())
    return new_interactor.find_by_id(location.id).editor


def find_by_name_in_nested_ui(interactor, location):
    new_interactor = interactor.locate(locator.NestedUI())
    return new_interactor.find_by_name(location.name).editor


def register_find_by_in_nested_ui(registry, target_class):
    registry.register_location_solver(
        target_class=target_class,
        locator_class=locator.TargetById,
        solver=find_by_id_in_nested_ui,
    )
    registry.register_location_solver(
        target_class=target_class,
        locator_class=locator.TargetByName,
        solver=find_by_name_in_nested_ui,
    )
