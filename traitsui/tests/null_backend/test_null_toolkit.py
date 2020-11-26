import unittest

from traits.api import HasTraits, Int
from traitsui.tests._tools import BaseTestMixin, requires_toolkit, ToolkitName


class TestNullToolkit(BaseTestMixin, unittest.TestCase):

    def setUp(self):
        BaseTestMixin.setUp(self)

    def tearDown(self):
        BaseTestMixin.tearDown(self)

    @requires_toolkit([ToolkitName.null])
    def test_configure_traits_error(self):
        """ Verify that configure_traits fails with NotImplementedError. """

        class Test(HasTraits):
            x = Int()

        t = Test()

        with self.assertRaises(NotImplementedError):
            t.configure_traits()
