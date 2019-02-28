
from __future__ import absolute_import
from nose.tools import assert_raises

from traits.api import HasTraits, Int
from traitsui.tests._tools import skip_if_not_null


@skip_if_not_null
def test_configure_traits_error():
    """ Verify that configure_traits fails with NotImplementedError. """
    class Test(HasTraits):
        x = Int

    t = Test()

    with assert_raises(NotImplementedError):
        t.configure_traits()
