
import unittest
from unittest import mock

from traits.api import (
    Button, Instance, HasTraits, Int, Str,
)
from traitsui.api import ButtonEditor, InstanceEditor, Item, ModelView, View
from traitsui.testing.api import (
    command, Disabled, InteractionRegistry, locator, query, UITester,
)
from traitsui.testing.exceptions import (
    LocationNotSupported,
)
from traitsui.testing.ui_tester import (
    UIWrapper,
)
from traitsui.tests._tools import (
    is_qt,
    is_wx,
    requires_toolkit,
    ToolkitName,
)
from traitsui.ui import UI


class Order(HasTraits):

    submit_button = Button()

    submit_n_events = Int()

    submit_label = Str("Submit")

    def _submit_button_fired(self):
        self.submit_n_events += 1
        self.submit_label = (
            "Submit (ordered {} times)".format(self.submit_n_events)
        )


class Model(HasTraits):

    order = Instance(Order, ())


class SimpleApplication(ModelView):

    model = Instance(Model)


def get_view_with_instance_editor(style, enabled_when=""):
    """ Return a view for SimpleApplication using InstanceEditor with the
    given style.
    """
    return View(
        Item(
            "model.order",
            id="model_order_id",
            style=style,
            editor=InstanceEditor(
                view=View(
                    Item(
                        name="submit_button",
                        id="submit_button_id",
                        editor=ButtonEditor(
                            label_value="submit_label",
                        ),
                        enabled_when=enabled_when,
                    ),
                ),
            ),
        )
    )


class ManyMouseClick:
    def __init__(self, n_times):
        self.n_times = n_times


class GetEnableFlag:
    pass


class BadAction:
    pass


def raise_error(interactor, action):
    raise ZeroDivisionError()


if is_qt():
    from traitsui.qt4.button_editor import SimpleEditor as SimpleButtonEditor

    def click_n_times(interactor, action):
        for _ in range(action.n_times):
            if not interactor.editor.control.isEnabled():
                raise Disabled("Button is disabled.")
            interactor.editor.control.click()

    def is_enabled(interactor, action):
        return interactor.editor.control.isEnabled()


if is_wx():
    from traitsui.wx.button_editor import SimpleEditor as SimpleButtonEditor

    def click_n_times(interactor, action):  # noqa: F811
        import wx
        control = interactor.editor.control
        if not control.IsEnabled():
            raise Disabled("Button is disabled.")
        event = wx.CommandEvent(wx.EVT_BUTTON.typeId, control.GetId())
        event.SetEventObject(control)
        for _ in range(action.n_times):
            wx.PostEvent(control, event)

    def is_enabled(interactor, action):   # noqa: F811
        return interactor.editor.control.IsEnabled()


def get_local_registry():
    registry = InteractionRegistry()
    registry.register(
        target_class=SimpleButtonEditor,
        interaction_class=ManyMouseClick,
        handler=click_n_times,
    )
    registry.register(
        target_class=SimpleButtonEditor,
        interaction_class=GetEnableFlag,
        handler=is_enabled,
    )
    registry.register(
        target_class=SimpleButtonEditor,
        interaction_class=BadAction,
        handler=raise_error,
    )
    return registry


@requires_toolkit([ToolkitName.qt, ToolkitName.wx])
class TestUITesterSimulate(unittest.TestCase):
    """ Test using additional interactors with a local registry.
    """

    def check_command_propagated_to_nested_ui(self, style):
        # the default interactor for the instance editor is used, and then
        # the custom simulation on the button is used.
        order = Order()
        view = get_view_with_instance_editor(style)
        app = SimpleApplication(model=Model(order=order))
        tester = UITester()
        tester.add_registry(get_local_registry())
        with tester.create_ui(app, dict(view=view)) as ui:
            tester\
                .find_by_name(ui, "order")\
                .find_by_name("submit_button")\
                .perform(ManyMouseClick(3))
            self.assertEqual(order.submit_n_events, 3)

    def test_command_custom_interactor_with_simple_instance_editor(self):
        # Check command is propagated by the interactor get_ui for
        # simple instance editor.
        self.check_command_propagated_to_nested_ui("simple")

    def test_command_custom_interactor_with_custom_instance_editor(self):
        # Check command is propagated by the interactor get_ui for
        # custom instance editor.
        self.check_command_propagated_to_nested_ui("custom")

    def check_query_propagated_to_nested_ui(self, style):
        # the default interactor for the instance editor is used, and then
        # the custom simulation on the button is used.
        order = Order()
        view = get_view_with_instance_editor(style, enabled_when="False")
        app = SimpleApplication(model=Model(order=order))
        tester = UITester()
        tester.add_registry(get_local_registry())
        with tester.create_ui(app, dict(view=view)) as ui:
            actual = tester\
                .find_by_name(ui, "order")\
                .find_by_name("submit_button")\
                .inspect(GetEnableFlag())
            self.assertIs(actual, False)

    def test_query_custom_interactor_with_simple_instance_editor(self):
        # Check query is propagated by the interactor get_ui for
        # simple instance editor.
        self.check_query_propagated_to_nested_ui("simple")

    def test_query_custom_interactor_with_custom_instance_editor(self):
        # Check query is propagated by the interactor get_ui for
        # custom instance editor.
        self.check_query_propagated_to_nested_ui("custom")

    def test_action_override_by_registry(self):
        order = Order()
        view = View(Item("submit_button"))
        tester = UITester([get_local_registry()])

        new_handler = mock.Mock()
        registry = InteractionRegistry()
        registry.register(
            target_class=SimpleButtonEditor,
            interaction_class=ManyMouseClick,
            handler=new_handler,
        )
        tester.add_registry(registry)

        with tester.create_ui(order, dict(view=view)) as ui:
            tester.find_by_name(ui, "submit_button").perform(
                ManyMouseClick(10)
            )
            # The ManyMouseClick from get_local_registry is not used.
            self.assertEqual(order.submit_n_events, 0)
            # The ManyMouseClick from last register is used.
            self.assertEqual(new_handler.call_count, 1)

    def test_action_override_by_registry_with_ancestor(self):
        order = Order()
        view = View(Item("submit_button"))

        lower_priority_handler = mock.Mock()
        lower_priority_registry = InteractionRegistry()
        lower_priority_registry.register(
            target_class=SimpleButtonEditor,
            interaction_class=ManyMouseClick,
            handler=lower_priority_handler,
        )
        higher_priority_handler = mock.Mock()
        higher_priority_registry = InteractionRegistry()
        higher_priority_registry.register(
            target_class=UI,
            interaction_class=ManyMouseClick,
            handler=higher_priority_handler,
        )
        tester = UITester([higher_priority_registry, lower_priority_registry])
        with tester.create_ui(order, dict(view=view)) as ui:
            tester.find_by_name(ui, "submit_button").perform(ManyMouseClick(1))

        # The one from the lower priority registry is called because the
        # target_class is more specific.
        self.assertEqual(lower_priority_handler.call_count, 1)
        self.assertEqual(higher_priority_handler.call_count, 0)

    def test_backward_compatibility_when_new_location_introduced(self):
        # Test code should not need to change when a new location solver is
        # introduced.
        order = Order()
        view = View(Item("submit_button"))

        handler = mock.Mock()
        registry = InteractionRegistry()
        registry.register(
            target_class=SimpleButtonEditor,
            interaction_class=ManyMouseClick,
            handler=handler,
        )

        # This new registry represents an additional logic in the future
        # that should not break existing test code.
        new_registry = InteractionRegistry()
        new_registry.register_location_solver(
            target_class=SimpleButtonEditor,
            locator_class=locator.DefaultTarget,
            solver=lambda interactor, _: interactor.editor.control,
        )
        tester = UITester([new_registry, registry])
        with tester.create_ui(order, dict(view=view)) as ui:
            tester.find_by_name(ui, "submit_button").perform(ManyMouseClick(1))

        self.assertEqual(handler.call_count, 1)


@requires_toolkit([ToolkitName.qt, ToolkitName.wx])
class TestUITesterCreateUI(unittest.TestCase):
    """ Test UITester.create_ui
    """

    def test_ui_disposed(self):
        tester = UITester([])
        order = Order()
        view = View(
            Item("submit_button", enabled_when="submit_n_events < 1"),
        )
        with tester.create_ui(order, dict(view=view)) as ui:
            order.submit_n_events = 2
        self.assertTrue(ui.destroyed)


class TestUITesterFind(unittest.TestCase):
    """ Test find_by functionality."""

    def test_create_ui_interactor(self):
        tester = UITester(delay=1000)
        with tester.create_ui(Order()) as ui:
            interactor = tester._get_ui_interactor(ui)
            self.assertIs(interactor.editor, ui)
            self.assertEqual(interactor.registries, tester._registries)
            self.assertEqual(interactor.delay, tester.delay)

    def test_ui_interactor_locate_by_name(self):
        tester = UITester()
        with tester.create_ui(Order()) as ui:
            ui_interactor = tester._get_ui_interactor(ui)
            new_interactor = ui_interactor.locate(
                locator.TargetByName("submit_n_events")
            )
            expected, = ui.get_editors("submit_n_events")
            self.assertIs(new_interactor.editor, expected)

    def test_ui_interactor_locate_by_id(self):
        tester = UITester()
        view = View(Item(name="submit_n_events", id="pretty_id"))
        with tester.create_ui(Order(), dict(view=view)) as ui:
            ui_interactor = tester._get_ui_interactor(ui)
            new_interactor = ui_interactor.locate(
                locator.TargetById("pretty_id")
            )
            expected, = ui.get_editors("submit_n_events")
            self.assertIs(new_interactor.editor, expected)

    def test_no_editors_found(self):
        # The view does not have "submit_n_events"
        tester = UITester()
        view = View(Item("submit_button"))
        with tester.create_ui(Order(), dict(view=view)) as ui:
            with self.assertRaises(ValueError) as exception_context:
                tester.find_by_name(ui, "submit_n_events")

        self.assertIn(
            "No editors can be found", str(exception_context.exception),
        )

    def test_multiple_editors_found(self):
        # Repeated names not currently supported.
        tester = UITester()
        view = View(Item("submit_button"), Item("submit_button"))
        with tester.create_ui(Order(), dict(view=view)) as ui:
            with self.assertRaises(ValueError) as exception_context:
                tester.find_by_name(ui, "submit_button")

        self.assertIn(
            "Found multiple editors", str(exception_context.exception),
        )

    def test_error_propagated(self):
        # The action raises an error.
        # That error should be propagated.
        order = Order()
        view = get_view_with_instance_editor("simple", enabled_when="False")
        app = SimpleApplication(model=Model(order=order))
        tester = UITester()
        tester.add_registry(get_local_registry())
        with tester.create_ui(app, dict(view=view)) as ui:
            order = tester.find_by_name(ui, "order")
            submit_button = order.find_by_name("submit_button")
            with self.assertRaises(ZeroDivisionError):
                submit_button.perform(BadAction())

    def test_find_by_id(self):
        tester = UITester(delay=123)
        item1 = Item("submit_button", id="item1")
        item2 = Item("submit_button", id="item2")
        view = View(item1, item2)
        with tester.create_ui(Order(), dict(view=view)) as ui:
            interactor = tester.find_by_id(ui, "item2")
            self.assertIs(interactor.editor.item, item2)
            self.assertEqual(interactor.registries, tester._registries)
            self.assertEqual(interactor.delay, tester.delay)

    def test_find_by_id_multiple(self):
        # The uniqueness is not enforced. The first one is returned.
        tester = UITester()
        item1 = Item("submit_button", id="item1")
        item2 = Item("submit_button", id="item2")
        item3 = Item("submit_button", id="item2")
        view = View(item1, item2, item3)
        with tester.create_ui(Order(), dict(view=view)) as ui:
            interactor = tester.find_by_id(ui, "item2")
            self.assertIs(interactor.editor.item, item2)

    def test_find_by_id_in_nested(self):
        order = Order()
        view = get_view_with_instance_editor(style="custom")
        app = SimpleApplication(model=Model(order=order))
        tester = UITester()
        with tester.create_ui(app, dict(view=view)) as ui:
            order_interactor = tester.find_by_id(ui, "model_order_id")
            submit_button = order_interactor.find_by_id("submit_button_id")

            self.assertEqual(
                submit_button.editor.name, "submit_button")
            self.assertEqual(
                submit_button.editor.item.id, "submit_button_id")
            self.assertEqual(
                submit_button.editor.object, order)

    def test_find_by_name(self):
        tester = UITester(delay=123)
        item1 = Item("submit_button", id="item1")
        item2 = Item("submit_n_events", id="item2")
        view = View(item1, item2)
        with tester.create_ui(Order(), dict(view=view)) as ui:
            interactor = tester.find_by_name(ui, "submit_n_events")
            self.assertIs(interactor.editor.item, item2)
            self.assertEqual(interactor.registries, tester._registries)
            self.assertEqual(interactor.delay, tester.delay)

    def test_find_by_name_in_nested(self):
        order = Order()
        view = get_view_with_instance_editor(style="custom")
        app = SimpleApplication(model=Model(order=order))
        tester = UITester()
        with tester.create_ui(app, dict(view=view)) as ui:
            order_interactor = tester.find_by_name(ui, "order")
            submit_button = order_interactor.find_by_name("submit_button")

            self.assertEqual(
                submit_button.editor.name, "submit_button")
            self.assertEqual(
                submit_button.editor.object, order)


class FakeTarget:
    pass


class TestUITesterLocate(unittest.TestCase):

    def setUp(self):
        self.target_class = FakeTarget
        self.registry = InteractionRegistry()
        self.interactor = UIWrapper(
            editor=FakeTarget(),
            registries=[self.registry],
        )

    def test_locate_with_resolved_target(self):

        target = (1, 2, 3)

        def resolve_target(interactor, location):
            return target

        self.registry.register_location_solver(
            target_class=self.target_class,
            locator_class=int,
            solver=resolve_target,
        )

        new_location = self.interactor.locate(0)
        self.assertIs(new_location.editor, target)

    def test_locate_with_unknown_location(self):

        self.registry.register_location_solver(
            target_class=self.target_class,
            locator_class=int,
            solver=mock.Mock(),
        )
        with self.assertRaises(LocationNotSupported):
            self.interactor.locate("123")
