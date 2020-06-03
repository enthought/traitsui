import datetime
import unittest

from traits.api import (
    Bool, Button, Date, Enum, Instance, HasTraits, List, Str, Int,
    on_trait_change, Property
)
from traitsui.api import EnumEditor, Item, ModelView, TextEditor, View
from traitsui.testing.api import (
    BaseSimulator, Disabled, simulate, SimulatorRegistry, UITester,
)
from traitsui.tests._tools import (
    is_current_backend_qt4,
    is_current_backend_wx,
    requires_one_of,
    QT,
    WX,
)


class Parent(HasTraits):

    first_name = Str()
    last_name = Str()
    age = Int()
    employment_status = Enum(["employed", "unemployed"])

    def default_traits_view(self):
        return View(
            Item("first_name"),
            Item("last_name"),
            Item("age"),
            Item(
                "employment_status",
                editor=EnumEditor(
                    values=["employed", "unemployed"],
                    evaluate=True,
                    auto_set=False,
                )
            ),
        )


class Child(HasTraits):

    mother = Instance(Parent)
    father = Instance(Parent)
    first_name = Str()
    last_name = Property(depends_on="father,father.last_name")

    def _get_last_name(self):
        if self.father is None:
            return None
        return self.father.last_name


class SimpleApplication(ModelView):

    model = Instance(Child)


@requires_one_of([QT, WX])
class TestUITesterIntegration(unittest.TestCase):
    """ Integration tests for UITester.

    These tests are close imitations for how UITester is expected to be used.
    """

    def setUp(self):
        # UITest can also be used as a context manager
        self.tester = UITester()
        self.tester.start()

    def tearDown(self):
        self.tester.stop()

    def test_instance_text_editor_from_view(self):
        # Test popagating commands to instance simple/custom editors
        father = Parent(first_name="M", last_name="C")
        mother = Parent(first_name="J", last_name="E", age=50)
        child = Child(mother=mother, father=father)
        view = View(
            Item("model.father", style="simple"),
            Item("model.mother", style="custom"),
        )
        app = SimpleApplication(model=child)
        with self.tester.create_ui(app, dict(view=view)) as ui:
            self.tester.set_text(ui, "father.first_name", "B")
            self.assertEqual(app.model.father.first_name, "B")

            self.tester.set_text(ui, "mother.age", "A")  # invalid
            self.assertEqual(app.model.mother.age, 50)

            self.tester.set_text(ui, "mother.age", "60")  # valid
            self.assertEqual(app.model.mother.age, 60)

            self.tester.set_text(ui, "father.employment_status", "unemployed")
            self.assertEqual(app.model.father.employment_status, "unemployed")

    def test_instance_text_editor_query(self):
        # Test popagating queries to instance simple/custom editors
        father = Parent(first_name="M", last_name="C")
        mother = Parent(first_name="J", last_name="E", age=50)
        child = Child(mother=mother, father=father)
        app = SimpleApplication(model=child)
        view = View(
            Item("model.father", style="simple"),
            Item("model.mother", style="custom"),
        )
        with self.tester.create_ui(app, dict(view=view)) as ui:
            app.model.father.first_name = "B"
            actual = self.tester.get_text(ui, "father.first_name")
            self.assertEqual(actual, "B")

            app.model.mother.age = 60
            actual = self.tester.get_text(ui, "mother.age")
            self.assertEqual(actual, "60")

            app.model.father.employment_status = "unemployed"
            actual = self.tester.get_text(ui, "father.employment_status")
            self.assertEqual(actual, "unemployed")


# Test contributing custom simulator methods
LOCAL_REGISTRY = SimulatorRegistry()

if is_current_backend_qt4():

    from traitsui.qt4.enum_editor import SimpleEditor as QtEnumEditor

    @simulate(QtEnumEditor, LOCAL_REGISTRY)
    class QtCustomSimulator(BaseSimulator):

        def click_some_index(self, index):
            self.editor.control.setCurrentIndex(index)


if is_current_backend_wx():

    from traitsui.wx.enum_editor import SimpleEditor as WxEnumEditor

    @simulate(WxEnumEditor, LOCAL_REGISTRY)
    class WxCustomSimulator(BaseSimulator):

        def click_some_index(self, index):
            control = self.editor.control
            control.SetSelection(index)

            # SetSelection does not emit events.
            if self.editor.factory.evaluate is None:
                event_type = wx.EVT_CHOICE.typeId
            else:
                event_type = wx.EVT_COMBOBOX.typeId
            event = wx.CommandEvent(event_type, control.GetId())
            text = control.GetString(index)
            event.SetString(text)
            event.SetInt(index)
            wx.PostEvent(control.GetParent(), event)


@requires_one_of([QT, WX])
class TestUITesterSimulateExtension(unittest.TestCase):
    """ Test when the existing simulators are not enough, it is easy to
    contribute new ones.
    """

    def test_custom_simulator_used(self):
        tester = UITester()
        tester.add_registry(LOCAL_REGISTRY)

        parent = Parent()
        with tester, tester.create_ui(parent) as ui:

            self.assertEqual(parent.employment_status, "employed")
            tester.set_editor_value(
                ui, "employment_status", lambda s: s.click_some_index(1)
            )
            self.assertEqual(parent.employment_status, "unemployed")

            # the default simulator from TraitsUI is still accessible.
            tester.set_text(ui, "employment_status", "employed")
            self.assertEqual(parent.employment_status, "employed")
