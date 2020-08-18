import unittest

from traitsui.testing.default_registry import get_default_registries


class TestDefaultRegistry(unittest.TestCase):

    def test_load_default_registries(self):
        registries = get_default_registries()
        for registry in registries:
            self.assertGreaterEqual(
                len(registry.editor_to_action_to_handler),
                1,
            )
