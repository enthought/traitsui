#  Copyright (c) 2008-19, Enthought, Inc.
#  All rights reserved.
#
#  This software is provided without warranty under the terms of the BSD
#  license included in enthought/LICENSE.txt and may be redistributed only
#  under the conditions described in the aforementioned license.  The license
#  is also available online at http://www.enthought.com/licenses/BSD.txt
#
#  Thanks for using Enthought open source!
#
#  Author: Corran Webster
#  Date:   August 12, 2019

import unittest

from traits.api import (
    Any, Bool, Event, Float, HasTraits, Int, List, Undefined
)
from traits.trait_base import xgetattr
from traits.testing.unittest_tools import UnittestTools

from traitsui.context_value import ContextValue, CVFloat, CVInt
from traitsui.editor import Editor
from traitsui.editor_factory import EditorFactory
from traitsui.handler import default_handler
from traitsui.ui import UI

from ._tools import is_current_backend_null


class FakeControl(HasTraits):

    #: The value stored in the control.
    control_value = Any

    #: An event which also can be fired.
    control_event = Event


class StubEditorFactory(EditorFactory):

    #: Whether or not the traits are events.
    is_event = Bool()

    #: Whether or not the traits are events.
    auxilliary_value = Any(sync_value=True)

    #: Whether or not the traits are events.
    auxilliary_cv_int = CVInt

    #: Whether or not the traits are events.
    auxilliary_cv_float = CVFloat

    def _auxilliary_cv_int_default(self):
        return 0

    def _auxilliary_cv_float_default(self):
        return 0.0


class StubEditor(Editor):

    #: Whether or not the traits are events.
    is_event = Bool

    #: An auxilliary value we want to synchronize.
    auxilliary_value = Any

    #: An auxilliary list we want to synchronize.
    auxilliary_list = List

    #: An auxilliary event we want to synchronize.
    auxilliary_event = Event

    #: An auxilliary int we want to synchronize with a context value.
    auxilliary_cv_int = Int(sync_value='from')

    #: An auxilliary float we want to synchronize with a context value.
    auxilliary_cv_float = Float

    def init(self, parent):
        self.control = FakeControl()
        self.is_event = self.factory.is_event
        if self.is_event:
            self.control.on_trait_change(self.update_object, 'control_event')
        else:
            self.control.on_trait_change(self.update_object, 'control_value')

    def dispose(self):
        if self.is_event:
            self.control.on_trait_change(self.update_object, 'control_event',
                                         remove=True)
        else:
            self.control.on_trait_change(self.update_object, 'control_value',
                                         remove=True)
        super(StubEditor, self).dispose()

    def update_editor(self):
        if self.is_event:
            self.control.control_event = True
        else:
            self.control.control_value = self.value

    def update_object(self, new):
        if self.control is not None:
            if not self._no_update:
                self._no_update = True
                try:
                    self.value = new
                finally:
                    self._no_update = False

    def set_focus(self, parent):
        pass


class UserObject(HasTraits):

    #: The value being edited.
    user_value = Any('test')

    #: An auxilliary user value
    user_auxilliary = Any(10)

    #: An list user value
    user_list = List(['one', 'two', 'three'])

    #: An event user value
    user_event = Event


@unittest.skipIf(is_current_backend_null(),
                 'Editor tests require non-null backend')
class TestEditor(UnittestTools, unittest.TestCase):

    def create_editor(self, context=None, object_name='object',
                      name='user_value', factory=None, is_event=False):
        if context is None:
            user_object = UserObject()
            context = {'object': user_object}
        elif '.' in object_name:
            context_name, xname = object_name.split('.', 1)
            context_object = context[context_name]
            user_object = xgetattr(context_object, xname)
        else:
            user_object = context[object_name]
        ui = UI(
            context=context,
            handler=default_handler(),
        )

        if factory is None:
            factory = StubEditorFactory()
        factory.is_event = is_event

        editor = StubEditor(
            parent=None,
            ui=ui,
            object_name=object_name,
            name=name,
            factory=factory,
            object=user_object,
        )
        return editor

    def test_lifecycle(self):
        editor = self.create_editor()

        self.assertEqual(editor.old_value, 'test')
        self.assertEqual(editor.name, 'user_value')
        self.assertEqual(editor.extended_name, 'user_value')
        self.assertEqual(editor.value, 'test')
        self.assertEqual(editor.str_value, 'test')
        self.assertIs(editor.value_trait, editor.object.trait('user_value'))
        self.assertIs(editor.context_object, editor.ui.context['object'])

        editor.prepare(None)

        # preparation creates the control and sets the control value
        self.assertEqual(editor.value, 'test')
        self.assertEqual(editor.control.control_value, 'test')

        # test changing the value in the control
        with self.assertTraitChanges(editor.control, 'control_value', count=1):
            with self.assertTraitChanges(editor.ui, 'modified', count=1):
                editor.object.user_value = 'new test'

        self.assertEqual(editor.value, 'new test')
        self.assertEqual(editor.control.control_value, 'new test')
        self.assertTrue(editor.ui.modified)

        # test changing the value in the user object
        with self.assertTraitChanges(editor.object, 'user_value', count=1):
            editor.control.control_value = 'even newer test'

        self.assertEqual(editor.value, 'even newer test')
        self.assertEqual(editor.object.user_value, 'even newer test')

        editor.dispose()

        self.assertIsNone(editor.object)
        self.assertIsNone(editor.factory)
        self.assertIsNone(editor.control)

    def test_context_object(self):
        user_object = UserObject(user_value='other_test')
        context = {'object': UserObject(), 'other_object': user_object}
        editor = self.create_editor(
            context=context,
            object_name='other_object',
        )

        self.assertEqual(editor.old_value, 'other_test')
        self.assertEqual(editor.name, 'user_value')
        self.assertEqual(editor.extended_name, 'user_value')
        self.assertIs(editor.context_object, editor.ui.context['other_object'])

        editor.prepare(None)

        # preparation creates the control and sets the control value
        self.assertEqual(editor.value, 'other_test')
        self.assertEqual(editor.control.control_value, 'other_test')

        # test the value in the control changes
        with self.assertTraitChanges(editor.control, 'control_value', count=1):
            user_object.user_value = 'new test'

        self.assertEqual(editor.value, 'new test')
        self.assertEqual(editor.control.control_value, 'new test')

        # test the value in the user object changes
        with self.assertTraitChanges(user_object, 'user_value', count=1):
            editor.control.control_value = 'even newer test'

        self.assertEqual(editor.value, 'even newer test')
        self.assertEqual(editor.object.user_value, 'even newer test')

        editor.dispose()

    def test_event_trait(self):
        editor = self.create_editor(name='user_event', is_event=True)
        user_object = editor.object

        self.assertEqual(editor.name, 'user_event')
        self.assertEqual(editor.extended_name, 'user_event')
        self.assertIs(editor.context_object, editor.ui.context['object'])

        editor.prepare(None)

        # preparation creates the control and sets the control value
        self.assertIs(editor.value, Undefined)

        # test changing the value in the control
        with self.assertTraitChanges(editor.control, 'control_event', count=1):
            user_object.user_event = True

        # test the value in the user object changes
        with self.assertTraitChanges(user_object, 'user_event', count=1):
            editor.control.control_event = True

        editor.dispose()

    def test_chained_object(self):
        context = {
            'object': UserObject(
                user_auxilliary=UserObject(user_value='other_test'),
            )
        }
        user_object = context['object'].user_auxilliary
        editor = self.create_editor(
            context=context,
            object_name='object.user_auxilliary',
        )

        self.assertEqual(editor.old_value, 'other_test')
        self.assertEqual(editor.name, 'user_value')
        self.assertEqual(editor.extended_name, 'user_auxilliary.user_value')
        self.assertIs(editor.context_object, editor.ui.context['object'])

        editor.prepare(None)

        # preparation creates the control and sets the control value
        self.assertEqual(editor.value, 'other_test')
        self.assertEqual(editor.control.control_value, 'other_test')

        # test changing the value in the control
        with self.assertTraitChanges(editor.control, 'control_value', count=1):
            user_object.user_value = 'new test'

        self.assertEqual(editor.value, 'new test')
        self.assertEqual(editor.control.control_value, 'new test')

        # test changing the value in the user object
        with self.assertTraitChanges(user_object, 'user_value', count=1):
            editor.control.control_value = 'even newer test'

        self.assertEqual(editor.value, 'even newer test')
        self.assertEqual(editor.object.user_value, 'even newer test')

        # test changing the chained object
        new_user_object = UserObject(user_value='new object')
        with self.assertTraitChanges(editor.control, 'control_value', count=1):
            with self.assertTraitChanges(editor, 'object', count=1):
                context['object'].user_auxilliary = new_user_object

        self.assertEqual(editor.value, 'new object')
        self.assertIs(editor.object, new_user_object)
        self.assertEqual(editor.object.user_value, 'new object')

        editor.dispose()

    def test_factory_sync_simple(self):
        factory = StubEditorFactory(auxilliary_value='test')
        editor = self.create_editor(factory=factory)
        editor.prepare(None)

        # preparation copies the auxilliary value from the factory
        self.assertIs(editor.auxilliary_value, 'test')

        editor.dispose()

    def test_factory_sync_cv_simple(self):
        factory = StubEditorFactory()
        editor = self.create_editor(factory=factory)
        editor.prepare(None)

        # preparation copies the auxilliary CV int value from the factory
        self.assertIs(editor.auxilliary_cv_int, 0)

        editor.dispose()

    def test_parse_extended_name(self):
        context = {
            'object': UserObject(
                user_auxilliary=UserObject(user_value='other_test'),
            ),
            'other_object': UserObject(user_value='another_test'),
        }
        editor = self.create_editor(context=context)
        editor.prepare(None)

        # test simple name
        object, name, getter = editor.parse_extended_name('user_value')
        value = getter()

        self.assertIs(object, context['object'])
        self.assertEqual(name, 'user_value')
        self.assertEqual(value, 'test')

        # test different context object name
        object, name, getter = editor.parse_extended_name(
                'other_object.user_value')
        value = getter()

        self.assertIs(object, context['other_object'])
        self.assertEqual(name, 'user_value')
        self.assertEqual(value, 'another_test')

        # test chained name
        object, name, getter = editor.parse_extended_name(
                'object.user_auxilliary.user_value')
        value = getter()

        self.assertIs(object, context['object'])
        self.assertEqual(name, 'user_auxilliary.user_value')
        self.assertEqual(value, 'other_test')

        editor.dispose()

    # Testing sync_value "from" ---------------------------------------------

    def test_sync_value_from(self):
        editor = self.create_editor()
        user_object = editor.object
        editor.prepare(None)

        with self.assertTraitChanges(editor, 'auxilliary_value', count=1):
            editor.sync_value(
                'object.user_auxilliary', 'auxilliary_value', 'from')

        self.assertEqual(editor.auxilliary_value, 10)

        with self.assertTraitChanges(editor, 'auxilliary_value', count=1):
            user_object.user_auxilliary = 11

        self.assertEqual(editor.auxilliary_value, 11)

        editor.dispose()

        with self.assertTraitDoesNotChange(editor, 'auxilliary_value'):
            user_object.user_auxilliary = 12

    def test_sync_value_from_object(self):
        editor = self.create_editor()
        user_object = editor.object
        editor.prepare(None)

        with self.assertTraitChanges(editor, 'auxilliary_value', count=1):
            editor.sync_value(
                'user_auxilliary', 'auxilliary_value', 'from')

        self.assertEqual(editor.auxilliary_value, 10)

        with self.assertTraitChanges(editor, 'auxilliary_value', count=1):
            user_object.user_auxilliary = 11

        self.assertEqual(editor.auxilliary_value, 11)

        editor.dispose()

        with self.assertTraitDoesNotChange(editor, 'auxilliary_value'):
            user_object.user_auxilliary = 12

    def test_sync_value_from_context(self):
        # set up the editor
        user_object = UserObject()
        other_object = UserObject(user_auxilliary=20)
        context = {
            'object': user_object,
            'other_object': other_object,
        }
        editor = self.create_editor(context=context)
        editor.prepare(None)

        with self.assertTraitChanges(editor, 'auxilliary_value', count=1):
            editor.sync_value(
                'other_object.user_auxilliary', 'auxilliary_value', 'from')

        self.assertEqual(editor.auxilliary_value, 20)

        with self.assertTraitChanges(editor, 'auxilliary_value', count=1):
            other_object.user_auxilliary = 11

        self.assertEqual(editor.auxilliary_value, 11)

        editor.dispose()

        with self.assertTraitDoesNotChange(editor, 'auxilliary_value'):
            other_object.user_auxilliary = 12

    def test_sync_value_from_chained(self):
        # set up the editor
        user_object = UserObject(
            user_auxilliary=UserObject(user_value=20),
        )
        context = {'object': user_object}
        editor = self.create_editor(context=context)
        editor.prepare(None)

        with self.assertTraitChanges(editor, 'auxilliary_value', count=1):
            editor.sync_value(
                'object.user_auxilliary.user_value', 'auxilliary_value', 'from'
            )

        self.assertEqual(editor.auxilliary_value, 20)

        with self.assertTraitChanges(editor, 'auxilliary_value', count=1):
            user_object.user_auxilliary.user_value = 11

        self.assertEqual(editor.auxilliary_value, 11)

        with self.assertTraitChanges(editor, 'auxilliary_value', count=1):
            user_object.user_auxilliary = UserObject(user_value=12)

        self.assertEqual(editor.auxilliary_value, 12)

        editor.dispose()

        with self.assertTraitDoesNotChange(editor, 'auxilliary_value'):
            user_object.user_auxilliary.user_value = 13

    def test_sync_value_from_list(self):
        editor = self.create_editor()
        user_object = editor.object
        editor.prepare(None)

        with self.assertTraitChanges(editor, 'auxilliary_list', count=1):
            editor.sync_value(
                'object.user_list', 'auxilliary_list', 'from', is_list=True)

        self.assertEqual(editor.auxilliary_list, ['one', 'two', 'three'])

        with self.assertTraitChanges(editor, 'auxilliary_list', count=1):
            user_object.user_list = ['one', 'two']

        self.assertEqual(editor.auxilliary_list, ['one', 'two'])

        with self.assertTraitChanges(editor, 'auxilliary_list_items', count=1):
            user_object.user_list[1:] = ['four', 'five']

        self.assertEqual(editor.auxilliary_list, ['one', 'four', 'five'])

        editor.dispose()

        with self.assertTraitDoesNotChange(editor, 'auxilliary_list'):
            user_object.user_list = ['one', 'two', 'three']

    def test_sync_value_from_event(self):
        editor = self.create_editor()
        user_object = editor.object
        editor.prepare(None)

        with self.assertTraitDoesNotChange(editor, 'auxilliary_event'):
            editor.sync_value(
                'object.user_event', 'auxilliary_event', 'from', is_event=True)

        with self.assertTraitChanges(editor, 'auxilliary_event', count=1):
            user_object.user_event = True

        editor.dispose()

        with self.assertTraitDoesNotChange(editor, 'auxilliary_event'):
            user_object.user_event = True

    def test_sync_value_from_cv(self):
        factory = StubEditorFactory(
            auxilliary_cv_int=ContextValue('object.user_auxilliary')
        )
        editor = self.create_editor(factory=factory)
        user_object = editor.object

        with self.assertTraitChanges(editor, 'auxilliary_cv_int', count=1):
            editor.prepare(None)

        self.assertEqual(editor.auxilliary_cv_int, 10)

        with self.assertTraitChanges(editor, 'auxilliary_cv_int', count=1):
            user_object.user_auxilliary = 11

        self.assertEqual(editor.auxilliary_cv_int, 11)

        editor.dispose()

        with self.assertTraitDoesNotChange(editor, 'auxilliary_cv_int'):
            user_object.user_auxilliary = 12

    # Testing sync_value "to" -----------------------------------------------

    def test_sync_value_to(self):
        editor = self.create_editor()
        user_object = editor.object
        editor.prepare(None)
        editor.auxilliary_value = 20

        with self.assertTraitChanges(user_object, 'user_auxilliary', count=1):
            editor.sync_value(
                'object.user_auxilliary', 'auxilliary_value', 'to')

        self.assertEqual(user_object.user_auxilliary, 20)

        with self.assertTraitChanges(user_object, 'user_auxilliary', count=1):
            editor.auxilliary_value = 11

        self.assertEqual(user_object.user_auxilliary, 11)

        editor.dispose()

        with self.assertTraitDoesNotChange(user_object, 'user_auxilliary'):
            editor.auxilliary_value = 12

    def test_sync_value_to_object(self):
        editor = self.create_editor()
        user_object = editor.object
        editor.prepare(None)
        editor.auxilliary_value = 20

        with self.assertTraitChanges(user_object, 'user_auxilliary', count=1):
            editor.sync_value(
                'user_auxilliary', 'auxilliary_value', 'to')

        self.assertEqual(user_object.user_auxilliary, 20)

        with self.assertTraitChanges(user_object, 'user_auxilliary', count=1):
            editor.auxilliary_value = 11

        self.assertEqual(user_object.user_auxilliary, 11)

        editor.dispose()

        with self.assertTraitDoesNotChange(user_object, 'user_auxilliary'):
            editor.auxilliary_value = 12

    def test_sync_value_to_context(self):
        # set up the editor
        user_object = UserObject()
        other_object = UserObject()
        context = {
            'object': user_object,
            'other_object': other_object,
        }
        editor = self.create_editor(context=context)
        editor.prepare(None)
        editor.auxilliary_value = 20

        with self.assertTraitChanges(other_object, 'user_auxilliary', count=1):
            editor.sync_value(
                'other_object.user_auxilliary', 'auxilliary_value', 'to')

        self.assertEqual(other_object.user_auxilliary, 20)

        with self.assertTraitChanges(other_object, 'user_auxilliary', count=1):
            editor.auxilliary_value = 11

        self.assertEqual(other_object.user_auxilliary, 11)

        editor.dispose()

        with self.assertTraitDoesNotChange(other_object, 'user_auxilliary'):
            editor.auxilliary_value = 12

    def test_sync_value_to_chained(self):
        user_object = UserObject(
            user_auxilliary=UserObject(),
        )
        context = {'object': user_object}
        editor = self.create_editor(context=context)
        editor.prepare(None)
        editor.auxilliary_value = 20

        with self.assertTraitChanges(user_object.user_auxilliary, 'user_value', count=1):
            editor.sync_value(
                'object.user_auxilliary.user_value', 'auxilliary_value', 'to')

        self.assertEqual(user_object.user_auxilliary.user_value, 20)

        with self.assertTraitChanges(user_object.user_auxilliary, 'user_value',
                                     count=1):
            editor.auxilliary_value = 11

        self.assertEqual(user_object.user_auxilliary.user_value, 11)

        editor.dispose()

        with self.assertTraitDoesNotChange(user_object.user_auxilliary,
                                           'user_value'):
            editor.auxilliary_value = 12

    def test_sync_value_to_list(self):
        editor = self.create_editor()
        user_object = editor.object
        editor.prepare(None)

        with self.assertTraitChanges(user_object, 'user_list', count=1):
            editor.sync_value(
                'object.user_list', 'auxilliary_list', 'to', is_list=True)

        self.assertEqual(user_object.user_list, [])

        with self.assertTraitChanges(user_object, 'user_list', count=1):
            editor.auxilliary_list = ['one', 'two']

        self.assertEqual(user_object.user_list, ['one', 'two'])

        with self.assertTraitChanges(user_object, 'user_list_items', count=1):
            editor.auxilliary_list[1:] = ['four', 'five']

        self.assertEqual(user_object.user_list, ['one', 'four', 'five'])

        editor.dispose()

        with self.assertTraitDoesNotChange(user_object, 'user_list'):
            editor.auxilliary_list = ['one', 'two', 'three']

    def test_sync_value_to_event(self):
        editor = self.create_editor()
        user_object = editor.object
        editor.prepare(None)

        with self.assertTraitDoesNotChange(user_object, 'user_event'):
            editor.sync_value(
                'object.user_event', 'auxilliary_event', 'to', is_event=True)

        with self.assertTraitChanges(user_object, 'user_event', count=1):
            editor.auxilliary_event = True

        editor.dispose()

        with self.assertTraitDoesNotChange(user_object, 'user_event'):
            editor.auxilliary_event = True

    def test_sync_value_to_cv(self):
        factory = StubEditorFactory(
            auxilliary_cv_float=ContextValue('object.user_auxilliary')
        )
        editor = self.create_editor(factory=factory)
        user_object = editor.object
        editor.auxilliary_cv_float = 20.0

        with self.assertTraitChanges(user_object, 'user_auxilliary', count=1):
            editor.prepare(None)

        self.assertEqual(user_object.user_auxilliary, 20)

        with self.assertTraitChanges(user_object, 'user_auxilliary', count=1):
            editor.auxilliary_cv_float = 11.0

        self.assertEqual(user_object.user_auxilliary, 11)

        editor.dispose()

        with self.assertTraitDoesNotChange(user_object, 'user_auxilliary'):
            editor.auxilliary_cv_float = 12.0

    # Testing sync_value "both" -----------------------------------------------

    def test_sync_value_both(self):
        editor = self.create_editor()
        user_object = editor.object
        editor.prepare(None)

        with self.assertTraitChanges(editor, 'auxilliary_value', count=1):
            editor.sync_value(
                'object.user_auxilliary', 'auxilliary_value', 'both')

        self.assertEqual(editor.auxilliary_value, 10)

        with self.assertTraitChanges(editor, 'auxilliary_value', count=1):
            user_object.user_auxilliary = 11

        self.assertEqual(editor.auxilliary_value, 11)

        with self.assertTraitChanges(user_object, 'user_auxilliary', count=1):
            editor.auxilliary_value = 12

        self.assertEqual(user_object.user_auxilliary, 12)

        editor.dispose()

        with self.assertTraitDoesNotChange(editor, 'auxilliary_value'):
            user_object.user_auxilliary = 13

        with self.assertTraitDoesNotChange(user_object, 'user_auxilliary'):
            editor.auxilliary_value = 14
