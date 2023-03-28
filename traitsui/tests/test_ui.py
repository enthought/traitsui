# (C) Copyright 2004-2023 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

"""
Test cases for the UI object.
"""

import contextlib
import unittest

from pyface.api import GUI
from traits.api import Property
from traits.has_traits import HasTraits, HasStrictTraits
from traits.trait_types import Str, Int

import traitsui
from traitsui.basic_editor_factory import BasicEditorFactory
from traitsui.api import Group, Item, spring, View
from traitsui.testing.api import DisplayedText, IsEnabled, MouseClick, UITester
from traitsui.tests._tools import (
    BaseTestMixin,
    count_calls,
    create_ui,
    is_qt,
    is_wx,
    process_cascade_events,
    requires_toolkit,
    reraise_exceptions,
    ToolkitName,
)
from traitsui.toolkit import toolkit, toolkit_object


class FooDialog(HasTraits):
    """Test dialog that does nothing useful."""

    my_int = Int(2)
    my_str = Str("hallo")

    traits_view = View(Item("my_int"), Item("my_str"), buttons=["OK"])


class DisallowNewTraits(HasStrictTraits):
    """Make sure no extra traits are added."""

    x = Int(10)

    traits_view = View(Item("x"), spring)


class MaybeInvalidTrait(HasTraits):

    name = Str()

    name_is_invalid = Property(observe="name")

    traits_view = View(Item("name", invalid="name_is_invalid"))

    def _get_name_is_invalid(self):
        return len(self.name) < 10


class TestUI(BaseTestMixin, unittest.TestCase):
    def setUp(self):
        BaseTestMixin.setUp(self)

    def tearDown(self):
        BaseTestMixin.tearDown(self)

    @requires_toolkit([ToolkitName.wx])
    def test_reset_with_destroy_wx(self):
        # Characterization test:
        # UI.reset(destroy=True) destroys all ui children of the top control

        foo = FooDialog()
        with create_ui(foo) as ui:

            ui.reset(destroy=True)

            process_cascade_events()
            # the top control is still there
            self.assertIsNotNone(ui.control)
            # but its children are gone
            self.assertEqual(len(ui.control.GetChildren()), 0)

    @requires_toolkit([ToolkitName.qt])
    def test_reset_with_destroy_qt(self):
        # Characterization test:
        # UI.reset(destroy=True) destroys all ui children of the top control

        from pyface import qt

        foo = FooDialog()
        with create_ui(foo) as ui:

            # decorate children's `deleteLater` function to check that it is
            # called on `reset`. check only with the editor parts (only widgets
            # are scheduled.
            # See traitsui.qt.toolkit.GUIToolkit.destroy_children)
            for c in ui.control.children():
                c.deleteLater = count_calls(c.deleteLater)

            ui.reset(destroy=True)

            # the top control is still there
            self.assertIsNotNone(ui.control)

            # but its children are scheduled for removal
            for c in ui.control.children():
                if isinstance(c, qt.QtGui.QWidget):
                    self.assertEqual(c.deleteLater._n_calls, 1)

    @requires_toolkit([ToolkitName.wx])
    def test_reset_without_destroy_wx(self):
        # Characterization test:
        # UI.reset(destroy=False) destroys all editor controls, but leaves
        # editors and ui children intact

        import wx

        foo = FooDialog()
        with create_ui(foo) as ui:

            self.assertEqual(len(ui._editors), 2)
            self.assertIsInstance(
                ui._editors[0], traitsui.wx.text_editor.SimpleEditor
            )
            self.assertIsInstance(ui._editors[0].control, wx.TextCtrl)

            ui.reset(destroy=False)

            self.assertEqual(len(ui._editors), 2)
            self.assertIsInstance(
                ui._editors[0], traitsui.wx.text_editor.SimpleEditor
            )
            self.assertIsNone(ui._editors[0].control)

            # children are still there: check first text control
            text_ctrl = ui.control.FindWindowByName("text")
            self.assertIsNotNone(text_ctrl)

    @requires_toolkit([ToolkitName.qt])
    def test_reset_without_destroy_qt(self):
        # Characterization test:
        # UI.reset(destroy=False) destroys all editor controls, but leaves
        # editors and ui children intact

        from pyface import qt

        foo = FooDialog()
        with create_ui(foo) as ui:

            self.assertEqual(len(ui._editors), 2)
            self.assertIsInstance(
                ui._editors[0], traitsui.qt.text_editor.SimpleEditor
            )
            self.assertIsInstance(ui._editors[0].control, qt.QtGui.QLineEdit)

            ui.reset(destroy=False)

            self.assertEqual(len(ui._editors), 2)
            self.assertIsInstance(
                ui._editors[0], traitsui.qt.text_editor.SimpleEditor
            )
            self.assertIsNone(ui._editors[0].control)

            # children are still there: check first text control
            text_ctrl = ui.control.findChild(qt.QtGui.QLineEdit)
            self.assertIsNotNone(text_ctrl)

    @requires_toolkit([ToolkitName.wx])
    def test_destroy_after_ok_wx(self):
        # Behavior: after pressing 'OK' in a dialog, the method UI.finish is
        # called and the view control and its children are destroyed

        foo = FooDialog()
        tester = UITester()
        with tester.create_ui(foo) as ui:
            # keep reference to the control to check that it was destroyed
            control = ui.control

            # decorate control's `Destroy` function to check that it is called
            control.Destroy = count_calls(control.Destroy)

            # press the OK button and close the dialog
            ok_button = tester.find_by_id(ui, "OK")
            self.assertEqual(ok_button.inspect(DisplayedText()), "OK")
            self.assertTrue(ok_button.inspect(IsEnabled()))
            ok_button.perform(MouseClick())

            self.assertIsNone(ui.control)
            self.assertEqual(control.Destroy._n_calls, 1)

    @requires_toolkit([ToolkitName.qt])
    def test_destroy_after_ok_qt(self):
        # Behavior: after pressing 'OK' in a dialog, the method UI.finish is
        # called and the view control and its children are destroyed

        foo = FooDialog()
        tester = UITester()
        with tester.create_ui(foo) as ui:
            # keep reference to the control to check that it was deleted
            control = ui.control

            # decorate control's `deleteLater` function to check that it is
            # called
            control.deleteLater = count_calls(control.deleteLater)

            # press the OK button and close the dialog
            ok_button = tester.find_by_id(ui, "OK")
            self.assertEqual(ok_button.inspect(DisplayedText()), "OK")
            self.assertTrue(ok_button.inspect(IsEnabled()))
            ok_button.perform(MouseClick())

            self.assertIsNone(ui.control)
            self.assertEqual(control.deleteLater._n_calls, 1)

    @requires_toolkit([ToolkitName.qt, ToolkitName.wx])
    def test_no_spring_trait(self):
        obj = DisallowNewTraits()
        with create_ui(obj):
            pass

        self.assertTrue("spring" not in obj.traits())

    @requires_toolkit([ToolkitName.qt, ToolkitName.wx])
    def test_invalid_state(self):
        # Regression test for enthought/traitsui#983
        obj = MaybeInvalidTrait(name="Name long enough to be valid")
        with create_ui(obj) as ui:
            (editor,) = ui.get_editors("name")
            self.assertFalse(editor.invalid)

            obj.name = "too short"
            self.assertTrue(editor.invalid)


# Regression test on an AttributeError commonly seen (enthought/traitsui#1145)
# Code in ui_panel makes use toolkit specific attributes on the toolkit
# specific Editor
ToolkitSpecificEditor = toolkit_object("editor:Editor")


class DummyObject(HasTraits):

    number = Int()


if is_qt():

    from pyface.qt import QtGui, QtCore

    class CustomWidget(QtGui.QWidget):
        def __init__(self, editor, parent=None):
            super().__init__()
            self._some_editor = editor

        def sizeHint(self):
            # This is called if the sibling widget is destroyed (e.g. the
            # nested UI in EditorWithCustomWidget) while the container
            # (e.g. QSplitter in EditorWithCustomWidget) has not been
            # destroyed. The container will want to ask this widget for its
            # sizeHint in order to resize/repaint the layout.
            assert self._some_editor.factory is not None
            return super().sizeHint()

    class EditorWithCustomWidget(ToolkitSpecificEditor):
        def init(self, parent):
            self.control = QtGui.QSplitter(QtCore.Qt.Orientation.Horizontal)

            widget = CustomWidget(editor=self)
            self.control.addWidget(widget)
            self.control.setStretchFactor(0, 2)

            self._ui = self.edit_traits(
                parent=self.control,
                kind="subpanel",
                view=View(Item("_", label="DUMMY"), width=100, height=100),
            )
            self.control.addWidget(self._ui.control)

        def dispose(self):
            self.dispose_inner_ui()
            super().dispose()

        def dispose_inner_ui(self):
            if self._ui is not None:
                self._ui.dispose()
                self._ui = None

        def update_editor(self):
            pass


if is_wx():

    # The AttributeError is not seen on Wx. But Destroy needs to be made
    # asynchronous.

    import wx
    from traitsui.wx.helper import TraitsUIPanel

    class DummyButtonEditor(ToolkitSpecificEditor):
        def init(self, parent):
            self.control = wx.Button(parent, -1, "Dummy")
            self.control.Bind(wx.EVT_BUTTON, self.update_object)

        def dispose(self):
            # If the object is deleted too soon, we run into a RuntimeError.
            self.control.Unbind(wx.EVT_BUTTON)
            super().dispose()

        def update_object(self, event):
            pass

        def update_editor(self):
            pass

    class EditorWithCustomWidget(ToolkitSpecificEditor):  # noqa: F811
        def init(self, parent):
            self.control = TraitsUIPanel(parent, -1)

            sizer = wx.BoxSizer(wx.HORIZONTAL)
            self._dummy = DummyObject()
            self._ui = self._dummy.edit_traits(
                parent=self.control,
                kind="subpanel",
                view=View(
                    Item(
                        "number",
                        editor=BasicEditorFactory(klass=DummyButtonEditor),
                    ),
                ),
            )
            sizer.Add(self._ui.control, 1, wx.EXPAND)
            self.control.SetSizerAndFit(sizer)

        def update_editor(self):
            pass

        def dispose(self):
            super().dispose()

        def dispose_inner_ui(self):
            if self._ui is not None:
                self._ui.dispose()
                self._ui = None


class TestUIDispose(BaseTestMixin, unittest.TestCase):
    """Test disposal of UI."""

    def setUp(self):
        BaseTestMixin.setUp(self)

    def tearDown(self):
        BaseTestMixin.tearDown(self)

    @requires_toolkit([ToolkitName.qt, ToolkitName.wx])
    def test_close_ui(self):
        # Test closing the main window normally.
        obj = DummyObject()
        view = View(
            Group(
                Item(
                    "number",
                    editor=BasicEditorFactory(klass=EditorWithCustomWidget),
                ),
            ),
        )
        ui = obj.edit_traits(view=view)
        with ensure_destroyed(ui):
            gui = GUI()
            gui.invoke_later(close_control, ui.control)
            with reraise_exceptions():
                process_cascade_events()
            self.assertIsNone(ui.control)

    @requires_toolkit([ToolkitName.qt, ToolkitName.wx])
    def test_dispose_inner_ui(self):
        obj = DummyObject()
        view = View(
            Group(
                Item(
                    "number",
                    editor=BasicEditorFactory(klass=EditorWithCustomWidget),
                ),
            ),
        )
        ui = obj.edit_traits(view=view)
        (editor,) = ui.get_editors("number")

        gui = GUI()
        with ensure_destroyed(ui):
            # This represents an event handler that causes a nested UI to be
            # disposed.
            gui.invoke_later(editor.dispose_inner_ui)

            # Allowing GUI to process the disposal requests is crucial.
            # This requirement should be satisfied in production setting
            # where the dispose method is part of an event handler.
            # Not doing so before disposing the main UI would be a programming
            # error in tests settings.
            with reraise_exceptions():
                process_cascade_events()

            gui.invoke_later(close_control, ui.control)
            with reraise_exceptions():
                process_cascade_events()

            self.assertIsNone(ui.control)


@contextlib.contextmanager
def ensure_destroyed(ui):
    """Ensure the widget is destroyed in the event when test fails."""
    try:
        yield
    finally:
        if ui.control is not None:
            toolkit().destroy_control(ui.control)
        with reraise_exceptions():
            process_cascade_events()


def close_control(control):
    """Close the widget."""
    if is_qt():
        control.close()
    elif is_wx():
        control.Close()
    else:
        raise NotImplementedError("Unexpected toolkit")
