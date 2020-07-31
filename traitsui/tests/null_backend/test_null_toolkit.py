import unittest

from traits.api import HasTraits, Int
from traitsui.tests._tools import requires_toolkit, ToolkitName


class TestNullToolkit(unittest.TestCase):

    @requires_toolkit([ToolkitName.null])
    def test_configure_traits_error(self):
        """ Verify that configure_traits fails with NotImplementedError. """

        class Test(HasTraits):
            x = Int()

        t = Test()

        with self.assertRaises(NotImplementedError):
            t.configure_traits()
