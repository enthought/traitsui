import datetime
import unittest

from traits.api import (
    Bool, Button, Date, Enum, Instance, HasTraits, List, Str, Int,
    on_trait_change, Property
)
from traitsui.api import EnumEditor, Item, ModelView, View
from traitsui.testing.api import Disabled, UITester
from traitsui.tests._tools import (
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

            self.tester.click_index(ui, "mother.employment_status", 1)
            self.assertEqual(app.model.mother.employment_status, "unemployed")

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
