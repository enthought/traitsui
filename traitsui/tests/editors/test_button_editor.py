# (C) Copyright 2004-2023 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

import unittest

from pyface.api import ImageResource
from pyface.ui_traits import Image
from traits.api import Bool, Button, HasTraits, List, Str
from traits.testing.api import UnittestTools

from traitsui.api import ButtonEditor, Item, UItem, View
import traitsui.extras
from traitsui.tests._tools import (
    BaseTestMixin,
    requires_toolkit,
    reraise_exceptions,
    ToolkitName,
)
from traitsui.testing.api import DisplayedText, IsEnabled, MouseClick, UITester


class ButtonTextEdit(HasTraits):

    play_button = Button("Play")

    play_button_label = Str("I'm a play button")

    play_button_image = Image(ImageResource("run", [traitsui.extras]))

    values = List()

    button_enabled = Bool(True)

    traits_view = View(
        Item("play_button", style="simple"),
        Item("play_button", style="custom"),
        Item("play_button", style="readonly"),
        Item("play_button", style="text"),
    )


simple_view = View(
    UItem("play_button", editor=ButtonEditor(label_value="play_button_label")),
    Item("play_button_label"),
    resizable=True,
)


custom_view = View(
    UItem("play_button", editor=ButtonEditor(label_value="play_button_label")),
    Item("play_button_label"),
    resizable=True,
    style="custom",
)


custom_image_view = View(
    UItem("play_button", editor=ButtonEditor(image_value="play_button_image")),
    resizable=True,
    style="custom",
)


@requires_toolkit([ToolkitName.qt, ToolkitName.wx])
class TestButtonEditor(BaseTestMixin, unittest.TestCase, UnittestTools):
    def setUp(self):
        BaseTestMixin.setUp(self)

    def tearDown(self):
        BaseTestMixin.tearDown(self)

    def check_button_text_update(self, view):
        button_text_edit = ButtonTextEdit()

        tester = UITester()
        with tester.create_ui(button_text_edit, dict(view=view)) as ui:
            button = tester.find_by_name(ui, "play_button")
            actual = button.inspect(DisplayedText())
            self.assertEqual(actual, "I'm a play button")

            button_text_edit.play_button_label = "New Label"
            actual = button.inspect(DisplayedText())
            self.assertEqual(actual, "New Label")

    def test_styles(self):
        # simple smoke test of buttons
        button_text_edit = ButtonTextEdit()
        with UITester().create_ui(button_text_edit):
            pass

    def test_simple_button_editor(self):
        self.check_button_text_update(simple_view)

    # this currently fails on wx, see enthought/traitsui#1654
    @requires_toolkit([ToolkitName.qt])
    def test_custom_button_editor(self):
        self.check_button_text_update(custom_view)

    def check_button_fired_event(self, view):
        button_text_edit = ButtonTextEdit()

        tester = UITester()
        with tester.create_ui(button_text_edit, dict(view=view)) as ui:
            button = tester.find_by_name(ui, "play_button")

            with self.assertTraitChanges(
                button_text_edit, "play_button", count=1
            ):
                button.perform(MouseClick())

    def test_simple_button_editor_clicked(self):
        self.check_button_fired_event(simple_view)

    def test_custom_button_editor_clicked(self):
        self.check_button_fired_event(custom_view)

    def check_button_disabled(self, style):
        button_text_edit = ButtonTextEdit(
            button_enabled=False,
        )

        view = View(
            Item(
                "play_button",
                editor=ButtonEditor(),
                enabled_when="button_enabled",
                style=style,
            ),
        )
        tester = UITester()
        with tester.create_ui(button_text_edit, dict(view=view)) as ui:
            button = tester.find_by_name(ui, "play_button")
            self.assertFalse(button.inspect(IsEnabled()))

            with self.assertTraitDoesNotChange(
                button_text_edit, "play_button"
            ):
                button.perform(MouseClick())

            button_text_edit.button_enabled = True
            self.assertTrue(button.inspect(IsEnabled()))
            with self.assertTraitChanges(
                button_text_edit, "play_button", count=1
            ):
                button.perform(MouseClick())

    def test_simple_button_editor_disabled(self):
        self.check_button_disabled("simple")

    def test_custom_button_editor_disabled(self):
        self.check_button_disabled("custom")

    def test_custom_image_value(self):
        button_text_edit = ButtonTextEdit()

        tester = UITester()
        with tester.create_ui(
            button_text_edit, dict(view=custom_image_view)
        ) as ui:
            button = tester.find_by_name(ui, "play_button")
            default_image = button._target.image
            self.assertIsInstance(default_image, ImageResource)

            button_text_edit.play_button_image = ImageResource(
                'next', [traitsui.extras]
            )
            self.assertIsInstance(button._target.image, ImageResource)
            self.assertIsNot(button._target.image, default_image)


@requires_toolkit([ToolkitName.qt])
class TestButtonEditorValuesTrait(BaseTestMixin, unittest.TestCase):
    """The values_trait is only supported by Qt.

    See discussion enthought/traitsui#879
    """

    def setUp(self):
        BaseTestMixin.setUp(self)

    def tearDown(self):
        BaseTestMixin.tearDown(self)

    def get_view(self, style):
        return View(
            Item(
                "play_button",
                editor=ButtonEditor(values_trait="values"),
                style=style,
            ),
        )

    def check_editor_values_trait_init_and_dispose(self, style):
        # Smoke test to check init and dispose when values_trait is used.
        instance = ButtonTextEdit(values=["Item1", "Item2"])
        view = self.get_view(style=style)
        with reraise_exceptions():
            with UITester().create_ui(instance, dict(view=view)):
                pass

            # It is okay to mutate trait after the GUI is disposed.
            instance.values = ["Item3"]

    def test_simple_editor_values_trait_init_and_dispose(self):
        # Smoke test to check init and dispose when values_trait is used.
        self.check_editor_values_trait_init_and_dispose(style="simple")

    def test_custom_editor_values_trait_init_and_dispose(self):
        # Smoke test to check init and dispose when values_trait is used.
        self.check_editor_values_trait_init_and_dispose(style="custom")
