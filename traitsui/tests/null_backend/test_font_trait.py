
from __future__ import absolute_import
from nose.tools import assert_equals

from traits.api import HasTraits, Font

from traitsui.tests._tools import *


@skip_if_not_null
def test_font_trait_default():
    class Foo(HasTraits):
        font = Font()
    f = Foo()
    assert_equals(f.font, '10 pt Arial')


@skip_if_not_null
def test_font_trait_examples():
    """
    An assigned font string is parsed, and the substrings are
    put in the order: point size, family, style, weight, underline, facename

    The words 'pt, 'point' and 'family' are ignored.

    """
    class Foo(HasTraits):
        font = Font

    f = Foo(font='Qwerty 10')
    assert_equals(f.font, '10 pt Qwerty')

    f = Foo(font='nothing')
    assert_equals(f.font, 'nothing')

    f = Foo(font='swiss family arial')
    assert_equals(f.font, 'swiss arial')

    f = Foo(font='12 pt bold italic')
    assert_equals(f.font, '12 pt italic bold')

    f = Foo(font='123 Foo bar slant')
    assert_equals(f.font, '123 pt slant Foo bar')

    f = Foo(font='123 point Foo family bar slant')
    assert_equals(f.font, '123 pt slant Foo bar')

    f = Foo(font='16 xyzzy underline slant')
    assert_equals(f.font, '16 pt slant underline xyzzy')
