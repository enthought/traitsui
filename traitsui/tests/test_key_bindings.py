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
from unittest.mock import Mock

from traits.testing.api import UnittestTools


from traitsui.key_bindings import KeyBinding, KeyBindings, KeyBindingsHandler


class Controller1:

    def __init__(self):
        self.called = None

    def m1(self, *args):
        self.called = ("m1", args)


class Controller2(Controller1):

    def m2(self, *args):
        self.called = ("m2", args)


class TestKeyBinding(UnittestTools, unittest.TestCase):

    def test_clear_binding_no_match(self):
        key_binding = KeyBinding(binding1="Ctrl-S", binding2="Ctrl-T")

        with self.assertTraitDoesNotChange(key_binding, "binding1"):
            with self.assertTraitDoesNotChange(key_binding, "binding2"):
                key_binding.clear_binding("Ctrl-U")

    def test_clear_binding_match_binding2(self):
        key_binding = KeyBinding(binding1="Ctrl-S", binding2="Ctrl-T")

        with self.assertTraitDoesNotChange(key_binding, "binding1"):
            with self.assertTraitChanges(key_binding, "binding2"):
                key_binding.clear_binding("Ctrl-T")

        self.assertEqual(key_binding.binding2, "")

    def test_clear_binding_match_binding1(self):
        key_binding = KeyBinding(binding1="Ctrl-S", binding2="Ctrl-T")

        with self.assertTraitChanges(key_binding, "binding1"):
            with self.assertTraitChanges(key_binding, "binding2"):
                key_binding.clear_binding("Ctrl-S")

        self.assertEqual(key_binding.binding1, "Ctrl-T")
        self.assertEqual(key_binding.binding2, "")

    def test_match(self):
        key_binding = KeyBinding(binding1="Ctrl-S", binding2="Ctrl-T")

        self.assertTrue(key_binding.match("Ctrl-S"))
        self.assertTrue(key_binding.match("Ctrl-T"))
        self.assertFalse(key_binding.match("Ctrl-U"))


class TestKeyBindings(UnittestTools, unittest.TestCase):

    def test_init(self):
        bindings = [
            KeyBinding(binding1="Ctrl-S", binding2="Ctrl-T"),
            KeyBinding(binding1="Ctrl-U", binding2=""),
        ]
        key_bindings = KeyBindings(bindings)

        self.assertEqual(key_bindings.bindings, bindings)

    def test_init_args(self):
        bindings = [
            KeyBinding(binding1="Ctrl-S", binding2="Ctrl-T"),
            KeyBinding(binding1="Ctrl-U", binding2=""),
        ]
        key_bindings = KeyBindings(*bindings)

        self.assertEqual(key_bindings.bindings, bindings)

    def test_init_kwargs(self):
        bindings = [
            KeyBinding(binding1="Ctrl-S", binding2="Ctrl-T"),
            KeyBinding(binding1="Ctrl-U", binding2=""),
        ]
        key_bindings = KeyBindings(bindings=bindings)

        self.assertEqual(key_bindings.bindings, bindings)

    def test_merge(self):
        bindings = [
            KeyBinding(binding1="Ctrl-S", binding2="Ctrl-T", method_name="m1"),
            KeyBinding(binding1="Ctrl-U", binding2="", method_name="m2"),
        ]
        key_bindings_1 = KeyBindings(*bindings)

        key_bindings_2 = KeyBindings(
            KeyBinding(binding1="Ctrl-V", binding2="Ctrl-W", method_name="m2"),
            KeyBinding(binding1="Ctrl-S", binding2="", method_name="m3"),
        )

        key_bindings_1.merge(key_bindings_2)

        self.assertEqual(key_bindings_1.bindings, bindings)
        key_binding = bindings[1]
        self.assertEqual(key_binding.binding1, "Ctrl-V")
        self.assertEqual(key_binding.binding2, "Ctrl-W")

    def test_clear_bindings_match(self):
        bindings = [
            KeyBinding(binding1="Ctrl-S", binding2="Ctrl-T", method_name="m1"),
            KeyBinding(binding1="Ctrl-U", binding2="", method_name="m2"),
        ]
        key_bindings = KeyBindings(bindings=bindings)

        with self.assertTraitChanges(bindings[0], "binding2"):
            bindings[1].binding2 = "Ctrl-T"

        self.assertIs(bindings[0].binding2, "")

    def test_clear_bindings_no_match(self):
        bindings = [
            KeyBinding(binding1="Ctrl-S", binding2="Ctrl-T", method_name="m1"),
            KeyBinding(binding1="Ctrl-U", binding2="", method_name="m2"),
        ]
        key_bindings = KeyBindings(bindings=bindings)

        with self.assertTraitDoesNotChange(bindings[0], "binding1"):
            with self.assertTraitDoesNotChange(bindings[0], "binding2"):
                bindings[1].binding2 = "Ctrl-V"

    def test_do_match(self):
        bindings = [
            KeyBinding(binding1="Ctrl-S", binding2="Ctrl-T", method_name="m1"),
            KeyBinding(binding1="Ctrl-U", binding2="", method_name="m2"),
        ]
        key_bindings = KeyBindings(bindings=bindings)

        controller = Controller1()

        # test _do rather than do since it doesn't need a toolkit event
        result = key_bindings._do("Ctrl-T", [controller], ("args",), False)

        self.assertTrue(result)
        self.assertEqual(controller.called, ("m1", ("args",)))

    def test_do_match_first(self):
        bindings = [
            KeyBinding(binding1="Ctrl-S", binding2="Ctrl-T", method_name="m1"),
            KeyBinding(binding1="Ctrl-U", binding2="", method_name="m2"),
        ]
        key_bindings = KeyBindings(bindings=bindings)

        controller_1 = Controller1()
        controller_2 = Controller2()

        # test _do rather than do since it doesn't need a toolkit event
        result = key_bindings._do(
            "Ctrl-T",
            [controller_1, controller_2],
            ("args",),
            False,
        )

        self.assertTrue(result)
        self.assertEqual(controller_1.called, ("m1", ("args",)))

    def test_do_match_second(self):
        bindings = [
            KeyBinding(binding1="Ctrl-S", binding2="Ctrl-T", method_name="m1"),
            KeyBinding(binding1="Ctrl-U", binding2="", method_name="m2"),
        ]
        key_bindings = KeyBindings(bindings=bindings)

        controller_1 = Controller1()
        controller_2 = Controller2()

        # test _do rather than do since it doesn't need a toolkit event
        result = key_bindings._do(
            "Ctrl-U",
            [controller_1, controller_2],
            ("args",),
            False,
        )

        self.assertTrue(result)
        self.assertEqual(controller_2.called, ("m2", ("args",)))

    def test_do_no_match(self):
        bindings = [
            KeyBinding(binding1="Ctrl-S", binding2="Ctrl-T", method_name="m1"),
            KeyBinding(binding1="Ctrl-U", binding2="", method_name="m2"),
        ]
        key_bindings = KeyBindings(bindings=bindings)

        controller = Controller1()

        # test _do rather than do since it doesn't need a toolkit event
        result = key_bindings._do("Ctrl-U", [controller], ("args",), False)

        self.assertFalse(result)
        self.assertIsNone(controller.called)

    def test_do_no_match_complete(self):
        bindings = [
            KeyBinding(binding1="Ctrl-S", binding2="Ctrl-T", method_name="m1"),
            KeyBinding(binding1="Ctrl-U", binding2="", method_name="m2"),
        ]
        key_bindings = KeyBindings(bindings=bindings)

        controller = Controller1()

        # test _do rather than do since it doesn't need a toolkit event
        result = key_bindings._do("Ctrl-V", [controller], ("args",), False)

        self.assertFalse(result)
        self.assertIsNone(controller.called)


class TestKeyBindingsHandler(unittest.TestCase):

    def test_key_binding_for_match(self):
        bindings = [
            KeyBinding(binding1="Ctrl-S", binding2="Ctrl-T", method_name="m1"),
            KeyBinding(binding1="Ctrl-U", binding2="", method_name="m2"),
        ]
        key_bindings = KeyBindings(bindings=bindings)
        handler = KeyBindingsHandler(model=key_bindings)

        binding = handler.key_binding_for(bindings[0], "Ctrl-U")

        self.assertIs(binding, bindings[1])

    def test_key_binding_for_no_match(self):
        bindings = [
            KeyBinding(binding1="Ctrl-S", binding2="Ctrl-T", method_name="m1"),
            KeyBinding(binding1="Ctrl-U", binding2="", method_name="m2"),
        ]
        key_bindings = KeyBindings(bindings=bindings)
        handler = KeyBindingsHandler(model=key_bindings)

        binding = handler.key_binding_for(bindings[0], "Ctrl-V")

        self.assertIsNone(binding)

    def test_key_binding_for_match_self(self):
        bindings = [
            KeyBinding(binding1="Ctrl-S", binding2="Ctrl-T", method_name="m1"),
            KeyBinding(binding1="Ctrl-U", binding2="", method_name="m2"),
        ]
        key_bindings = KeyBindings(bindings=bindings)
        handler = KeyBindingsHandler(model=key_bindings)

        binding = handler.key_binding_for(bindings[0], "Ctrl-S")

        self.assertIsNone(binding)

    def test_key_binding_for_match_empty(self):
        bindings = [
            KeyBinding(binding1="Ctrl-S", binding2="Ctrl-T", method_name="m1"),
            KeyBinding(binding1="Ctrl-U", binding2="", method_name="m2"),
        ]
        key_bindings = KeyBindings(bindings=bindings)
        handler = KeyBindingsHandler(model=key_bindings)

        binding = handler.key_binding_for(bindings[0], "")

        self.assertIsNone(binding)
