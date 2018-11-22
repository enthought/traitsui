#------------------------------------------------------------------------------
#
#  Copyright (c) 2013, Enthought, Inc.
#  All rights reserved.
#
#  This software is provided without warranty under the terms of the BSD
#  license included in enthought/LICENSE.txt and may be redistributed only
#  under the conditions described in the aforementioned license.  The license
#  is also available online at http://www.enthought.com/licenses/BSD.txt
#
#------------------------------------------------------------------------------
""" General regression tests for various fixed bugs.
"""

from __future__ import absolute_import
import unittest

from traits.api import DelegatesTo, Event, HasTraits, Instance, Undefined
from traitsui.api import Editor, TextEditor


class Parent(HasTraits):
    button = Event()


class Child(HasTraits):
    parent = Instance(Parent)
    button = DelegatesTo('parent')


class TestRegression(unittest.TestCase):

    def test_editor_on_delegates_to_event(self):
        """ Make sure that DelegatesTo on Events passes Editor creation.
        """
        child = Child(parent=Parent())
        editor = Editor(
            None,
            factory=TextEditor(),
            object=child,
            name='button')
        self.assertIs(editor.old_value, Undefined)

    def test_attribute_error(self):
        """ Make sure genuine AttributeErrors raise on Editor creation.
        """
        self.assertRaises(AttributeError, Editor,
                          None, factory=TextEditor(), object=Parent(),
                          name='not_a_trait')
