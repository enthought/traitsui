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
Test case for bug (wx, Mac OS X)

A ListStrEditor was not checking for valid item indexes under Wx.  This was
most noticeable when the selected_index was set in the editor factory.
"""
import contextlib
import platform
import unittest

from traits.has_traits import HasTraits
from traits.trait_types import List, Int, Str
from traitsui.item import Item
from traitsui.view import View
from traitsui.editors.list_str_editor import ListStrEditor

from traitsui.tests._tools import (
    BaseTestMixin,
    create_ui,
    is_wx,
    is_qt,
    process_cascade_events,
    requires_toolkit,
    reraise_exceptions,
    ToolkitName,
)

is_windows = platform.system() == "Windows"


class ListStrModel(HasTraits):
    value = List(["one", "two", "three"])


class ListStrEditorWithSelectedIndex(HasTraits):
    values = List(Str())
    selected_index = Int()
    selected_indices = List(Int())
    selected = Str()


def get_view(**kwargs):
    return View(
        Item(
            "value",
            editor=ListStrEditor(**kwargs),
        )
    )


single_select_view = View(
    Item(
        "values",
        show_label=False,
        editor=ListStrEditor(selected_index="selected_index", editable=False),
    ),
    buttons=["OK"],
)

multi_select_view = View(
    Item(
        "values",
        show_label=False,
        editor=ListStrEditor(
            multi_select=True,
            selected_index="selected_indices",
            editable=False,
        ),
    ),
    buttons=["OK"],
)

single_select_item_view = View(
    Item(
        "values",
        show_label=False,
        editor=ListStrEditor(selected="selected", editable=False),
    ),
    buttons=["OK"],
)


def get_selected_indices(editor):
    """Returns a list of the indices of all currently selected list items."""
    if is_wx():
        import wx

        # "item" in this context means "index of the item"
        item = -1
        selected = []
        while True:
            item = editor.control.GetNextItem(
                item, wx.LIST_NEXT_ALL, wx.LIST_STATE_SELECTED
            )
            if item == -1:
                break
            selected.append(item)
        return selected

    elif is_qt():
        indices = editor.list_view.selectionModel().selectedRows()
        return [i.row() for i in indices]

    else:
        raise unittest.SkipTest("Test not implemented for this toolkit")


def set_selected_single(editor, index):
    """Selects a specified item in an editor with multi_select=False."""
    if is_wx():
        editor.control.Select(index)

    elif is_qt():
        from pyface.qt.QtGui import QItemSelectionModel

        smodel = editor.list_view.selectionModel()
        mi = editor.model.index(index)
        smodel.select(mi, QItemSelectionModel.SelectionFlag.ClearAndSelect)

    else:
        raise unittest.SkipTest("Test not implemented for this toolkit")


def set_selected_multiple(editor, indices):
    """Clears old selection and selects specified items in an editor with
    multi_select=True.
    """
    if is_wx():
        clear_selection(editor)
        for index in indices:
            editor.control.Select(index)

    elif is_qt():
        from pyface.qt.QtGui import QItemSelectionModel

        clear_selection(editor)
        smodel = editor.list_view.selectionModel()
        for index in indices:
            mi = editor.model.index(index)
            smodel.select(mi, QItemSelectionModel.SelectionFlag.Select)

    else:
        raise unittest.SkipTest("Test not implemented for this toolkit")


def clear_selection(editor):
    """Clears existing selection."""
    if is_wx():
        import wx

        currently_selected = get_selected_indices(editor)
        # Deselect all currently selected items
        for selected_index in currently_selected:
            editor.control.SetItemState(
                selected_index, 0, wx.LIST_STATE_SELECTED
            )

    elif is_qt():
        editor.list_view.selectionModel().clearSelection()

    else:
        raise unittest.SkipTest("Test not implemented for this toolkit")


def right_click_item(editor, index):
    """Right clicks on the specified item."""

    if is_wx():
        import wx

        control = editor.control
        event = wx.ListEvent(
            wx.EVT_LIST_ITEM_RIGHT_CLICK.typeId, control.GetId()
        )
        event.SetIndex(index)
        wx.PostEvent(control, event)

    elif is_qt():
        from pyface.qt import QtCore
        from pyface.qt.QtTest import QTest

        view = editor.list_view
        q_model_index = view.model().index(index, 0)
        view.scrollTo(q_model_index)
        rect = view.visualRect(q_model_index)
        QTest.mouseClick(
            view.viewport(),
            QtCore.Qt.MouseButton.RightButton,
            QtCore.Qt.KeyboardModifier.NoModifier,
            rect.center(),
        )
    else:
        raise unittest.SkipTest("Test not implemented for this toolkit")


def right_click_center(editor):
    """Right click the middle of the widget."""

    if is_wx():
        import wx

        control = editor.control
        event = wx.ListEvent(
            wx.EVT_LIST_ITEM_RIGHT_CLICK.typeId, control.GetId()
        )
        wx.PostEvent(control, event)

    elif is_qt():
        from pyface.qt import QtCore
        from pyface.qt.QtTest import QTest

        view = editor.list_view
        rect = view.rect()
        QTest.mouseClick(
            view.viewport(),
            QtCore.Qt.MouseButton.RightButton,
            QtCore.Qt.KeyboardModifier.NoModifier,
            rect.center(),
        )
    else:
        raise unittest.SkipTest("Test not implemented for this toolkit")


@unittest.skipIf(is_wx(), "Issue enthought/traitsui#752")
@requires_toolkit([ToolkitName.qt, ToolkitName.wx])
class TestListStrEditor(BaseTestMixin, unittest.TestCase):
    def setUp(self):
        BaseTestMixin.setUp(self)

    def tearDown(self):
        BaseTestMixin.tearDown(self)

    @contextlib.contextmanager
    def setup_gui(self, model, view):
        with create_ui(model, dict(view=view)) as ui:
            process_cascade_events()
            editor = ui.get_editors("value")[0]
            yield editor

    def test_list_str_editor_single_selection(self):
        with reraise_exceptions(), self.setup_gui(
            ListStrModel(), get_view()
        ) as editor:

            if is_qt():  # No initial selection
                self.assertEqual(editor.selected_index, -1)
                self.assertEqual(editor.selected, None)
            elif is_wx():  # First element selected initially
                self.assertEqual(editor.selected_index, 0)
                self.assertEqual(editor.selected, "one")

            set_selected_single(editor, 1)
            process_cascade_events()

            self.assertEqual(editor.selected_index, 1)
            self.assertEqual(editor.selected, "two")

            set_selected_single(editor, 2)
            process_cascade_events()

            self.assertEqual(editor.selected_index, 2)
            self.assertEqual(editor.selected, "three")

            clear_selection(editor)
            process_cascade_events()

            self.assertEqual(editor.selected_index, -1)
            self.assertEqual(editor.selected, None)

    def test_list_str_editor_multi_selection(self):
        view = get_view(multi_select=True)

        with reraise_exceptions(), self.setup_gui(
            ListStrModel(), view
        ) as editor:

            self.assertEqual(editor.multi_selected_indices, [])
            self.assertEqual(editor.multi_selected, [])

            set_selected_multiple(editor, [0, 1])
            process_cascade_events()

            self.assertEqual(editor.multi_selected_indices, [0, 1])
            self.assertEqual(editor.multi_selected, ["one", "two"])

            set_selected_multiple(editor, [2])
            process_cascade_events()

            self.assertEqual(editor.multi_selected_indices, [2])
            self.assertEqual(editor.multi_selected, ["three"])

            clear_selection(editor)
            process_cascade_events()

            self.assertEqual(editor.multi_selected_indices, [])
            self.assertEqual(editor.multi_selected, [])

    def test_list_str_editor_single_selection_changed(self):
        with reraise_exceptions(), self.setup_gui(
            ListStrModel(), get_view()
        ) as editor:

            if is_qt():  # No initial selection
                self.assertEqual(get_selected_indices(editor), [])
            elif is_wx():  # First element selected initially
                self.assertEqual(get_selected_indices(editor), [0])

            editor.selected_index = 1
            process_cascade_events()

            self.assertEqual(get_selected_indices(editor), [1])
            self.assertEqual(editor.selected, "two")

            editor.selected = "three"
            process_cascade_events()

            self.assertEqual(get_selected_indices(editor), [2])
            self.assertEqual(editor.selected_index, 2)

            # Selected set to invalid value doesn't change anything
            editor.selected = "four"
            process_cascade_events()

            self.assertEqual(get_selected_indices(editor), [2])
            self.assertEqual(editor.selected_index, 2)

            # Selected index changed to
            editor.selected_index = -1
            process_cascade_events()

            if is_qt():
                # -1 clears selection
                self.assertEqual(get_selected_indices(editor), [])
                self.assertEqual(editor.selected, None)
            elif is_wx():
                # Visually selects everything but doesn't update `selected`
                self.assertEqual(editor.selected, "four")
                self.assertEqual(get_selected_indices(editor), [0, 1, 2])

    def test_list_str_editor_multi_selection_changed(self):
        view = get_view(multi_select=True)

        with reraise_exceptions(), self.setup_gui(
            ListStrModel(), view
        ) as editor:

            self.assertEqual(get_selected_indices(editor), [])

            editor.multi_selected_indices = [0, 1]
            process_cascade_events()

            self.assertEqual(get_selected_indices(editor), [0, 1])
            self.assertEqual(editor.multi_selected, ["one", "two"])

            editor.multi_selected = ["three", "one"]
            process_cascade_events()

            self.assertEqual(sorted(get_selected_indices(editor)), [0, 2])
            self.assertEqual(sorted(editor.multi_selected_indices), [0, 2])

            editor.multi_selected = ["three", "four"]
            process_cascade_events()

            if is_qt():
                # Invalid values assigned to multi_selected are ignored
                self.assertEqual(get_selected_indices(editor), [2])
                self.assertEqual(editor.multi_selected_indices, [2])
            elif is_wx():
                # Selection indices are not updated at all
                self.assertEqual(get_selected_indices(editor), [0, 2])
                self.assertEqual(editor.multi_selected_indices, [0, 2])

            # Setting selected indices to an empty list clears selection
            editor.multi_selected_indices = []
            process_cascade_events()

            self.assertEqual(get_selected_indices(editor), [])
            self.assertEqual(editor.multi_selected, [])

    def test_list_str_editor_multi_selection_items_changed(self):
        view = get_view(multi_select=True)

        with reraise_exceptions(), self.setup_gui(
            ListStrModel(), view
        ) as editor:

            self.assertEqual(get_selected_indices(editor), [])

            editor.multi_selected_indices.extend([0, 1])
            process_cascade_events()

            self.assertEqual(get_selected_indices(editor), [0, 1])
            self.assertEqual(editor.multi_selected, ["one", "two"])

            editor.multi_selected_indices[1] = 2
            process_cascade_events()

            self.assertEqual(get_selected_indices(editor), [0, 2])
            self.assertEqual(editor.multi_selected, ["one", "three"])

            editor.multi_selected[0] = "two"
            process_cascade_events()

            self.assertEqual(sorted(get_selected_indices(editor)), [1, 2])
            self.assertEqual(sorted(editor.multi_selected_indices), [1, 2])

            # If a change in multi_selected involves an invalid value, nothing
            # is changed
            editor.multi_selected[0] = "four"
            process_cascade_events()

            self.assertEqual(sorted(get_selected_indices(editor)), [1, 2])
            self.assertEqual(sorted(editor.multi_selected_indices), [1, 2])

    def test_list_str_editor_item_count(self):
        model = ListStrModel()

        # Without auto_add
        with reraise_exceptions(), create_ui(
            model, dict(view=get_view())
        ) as ui:
            process_cascade_events()
            editor = ui.get_editors("value")[0]
            self.assertEqual(editor.item_count, 3)

        # With auto_add
        with reraise_exceptions(), create_ui(
            model, dict(view=get_view(auto_add=True))
        ) as ui:
            process_cascade_events()
            editor = ui.get_editors("value")[0]
            self.assertEqual(editor.item_count, 3)

    def test_list_str_editor_refresh_editor(self):
        # Smoke test for refresh_editor/refresh_
        with reraise_exceptions(), self.setup_gui(
            ListStrModel(), get_view()
        ) as editor:
            if is_qt():
                editor.refresh_editor()
            elif is_wx():
                editor._refresh()
            process_cascade_events()

    @requires_toolkit([ToolkitName.qt])
    def test_list_str_editor_update_editor_single_qt(self):
        # QT editor uses selected items as the source of truth when updating
        model = ListStrModel()

        with reraise_exceptions(), self.setup_gui(model, get_view()) as editor:

            set_selected_single(editor, 0)
            process_cascade_events()
            # Sanity check
            self.assertEqual(editor.selected_index, 0)
            self.assertEqual(editor.selected, "one")

            model.value = ["two", "one"]
            process_cascade_events()

            # Selected remains "one" and indices are updated accordingly
            self.assertEqual(get_selected_indices(editor), [1])
            self.assertEqual(editor.selected_index, 1)
            self.assertEqual(editor.selected, "one")

            # Removing "one" creates a case of no longer valid selection
            model.value = ["two", "three"]
            process_cascade_events()

            # Internal view model selection is reset, but editor selection
            # values are not (see issue enthought/traitsui#872)
            self.assertEqual(get_selected_indices(editor), [])
            self.assertEqual(editor.selected_index, 1)
            self.assertEqual(editor.selected, "one")

    @requires_toolkit([ToolkitName.wx])
    def test_list_str_editor_update_editor_single_wx(self):
        # WX editor uses selected indices as the source of truth when updating
        model = ListStrModel()

        with reraise_exceptions(), self.setup_gui(model, get_view()) as editor:

            set_selected_single(editor, 0)
            process_cascade_events()
            # Sanity check
            self.assertEqual(editor.selected_index, 0)
            self.assertEqual(editor.selected, "one")

            model.value = ["two", "one"]
            process_cascade_events()

            # Selected_index remains 0 and selected is updated accordingly
            self.assertEqual(get_selected_indices(editor), [0])
            self.assertEqual(editor.selected_index, 0)
            self.assertEqual(editor.selected, "two")

            # Empty list creates a case of no longer valid selection
            model.value = []
            process_cascade_events()

            # Internal view model selection is reset, but editor selection
            # values are not (see issue enthought/traitsui#872)
            self.assertEqual(get_selected_indices(editor), [])
            self.assertEqual(editor.selected_index, 0)
            self.assertEqual(editor.selected, "two")

    @requires_toolkit([ToolkitName.qt])
    def test_list_str_editor_update_editor_multi_qt(self):
        # QT editor uses selected items as the source of truth when updating
        model = ListStrModel()
        view = get_view(multi_select=True)

        with reraise_exceptions(), self.setup_gui(model, view) as editor:

            set_selected_multiple(editor, [0])
            process_cascade_events()
            # Sanity check
            self.assertEqual(editor.multi_selected_indices, [0])
            self.assertEqual(editor.multi_selected, ["one"])

            model.value = ["two", "one"]
            process_cascade_events()

            # Selected remains "one" and indices are updated accordingly
            self.assertEqual(get_selected_indices(editor), [1])
            self.assertEqual(editor.multi_selected_indices, [1])
            self.assertEqual(editor.multi_selected, ["one"])

            # Removing "one" creates a case of no longer valid selection.
            model.value = ["two", "three"]
            process_cascade_events()

            # Internal view model selection is reset, but editor selection
            # values are not (see issue enthought/traitsui#872)
            self.assertEqual(get_selected_indices(editor), [])
            self.assertEqual(editor.multi_selected_indices, [1])
            self.assertEqual(editor.multi_selected, ["one"])

    @requires_toolkit([ToolkitName.wx])
    def test_list_str_editor_update_editor_multi_wx(self):
        # WX editor uses selected indices as the source of truth when updating
        model = ListStrModel()
        view = get_view(multi_select=True)

        with reraise_exceptions(), self.setup_gui(model, view) as editor:

            set_selected_multiple(editor, [0])
            process_cascade_events()
            # Sanity check
            self.assertEqual(editor.multi_selected_indices, [0])
            self.assertEqual(editor.multi_selected, ["one"])

            model.value = ["two", "one"]
            process_cascade_events()

            # Selected_index remains 0 and selected is updated accordingly
            self.assertEqual(get_selected_indices(editor), [0])
            self.assertEqual(editor.multi_selected_indices, [0])
            self.assertEqual(editor.multi_selected, ["two"])

            # Empty list creates a case of no longer valid selection
            model.value = []
            process_cascade_events()

            # Internal view model selection is reset, but editor selection
            # values are not (see issue enthought/traitsui#872)
            self.assertEqual(get_selected_indices(editor), [])
            self.assertEqual(editor.multi_selected_indices, [0])
            self.assertEqual(editor.multi_selected, ["two"])

    # wx editor doesn't have a `callx` method
    @requires_toolkit([ToolkitName.qt])
    def test_list_str_editor_callx(self):
        model = ListStrModel()

        def change_value(model, value):
            model.value = value

        with reraise_exceptions(), self.setup_gui(model, get_view()) as editor:

            set_selected_single(editor, 0)
            process_cascade_events()
            # Sanity check
            self.assertEqual(editor.selected_index, 0)
            self.assertEqual(editor.selected, "one")

            editor.callx(change_value, model, ["two", "one"])
            process_cascade_events()

            # Nothing is updated
            self.assertEqual(get_selected_indices(editor), [0])
            self.assertEqual(editor.selected_index, 0)
            self.assertEqual(editor.selected, "one")

    # wx editor doesn't have a `setx` method
    @requires_toolkit([ToolkitName.qt])
    def test_list_str_editor_setx(self):
        with reraise_exceptions(), self.setup_gui(
            ListStrModel(), get_view()
        ) as editor:

            set_selected_single(editor, 0)
            process_cascade_events()
            # Sanity check
            self.assertEqual(editor.selected_index, 0)
            self.assertEqual(editor.selected, "one")

            editor.setx(selected="two")
            process_cascade_events()

            # Specified attribute is modified
            self.assertEqual(editor.selected, "two")
            # But nothing else is updated
            # FIXME issue enthought/traitsui#867
            with self.assertRaises(AssertionError):
                self.assertEqual(get_selected_indices(editor), [0])
                self.assertEqual(editor.selected_index, 0)
            self.assertEqual(get_selected_indices(editor), [1])
            self.assertEqual(editor.selected_index, 1)

    def test_list_str_editor_horizontal_lines(self):
        # Smoke test for painting horizontal lines
        view = get_view(horizontal_lines=True)
        with reraise_exceptions(), self.setup_gui(ListStrModel(), view):
            pass

    def test_list_str_editor_title(self):
        # Smoke test for adding a title
        with reraise_exceptions(), self.setup_gui(
            ListStrModel(), get_view(title="testing")
        ):
            pass

    def test_list_str_editor_right_click(self):
        class ListStrModelRightClick(HasTraits):
            value = List(["one", "two", "three"])
            right_clicked = Str()
            right_clicked_index = Int()

        model = ListStrModelRightClick()
        view = get_view(
            right_clicked="object.right_clicked",
            right_clicked_index="object.right_clicked_index",
        )

        with reraise_exceptions(), self.setup_gui(model, view) as editor:

            self.assertEqual(model.right_clicked, "")
            self.assertEqual(model.right_clicked_index, 0)

            right_click_item(editor, 1)
            process_cascade_events()

            self.assertEqual(model.right_clicked, "two")
            self.assertEqual(model.right_clicked_index, 1)

    def test_list_str_editor_right_click_out_of_bound(self):
        class ListStrModelRightClick(HasTraits):
            value = List([])
            right_clicked = Str()
            right_clicked_index = Int()

        model = ListStrModelRightClick()
        view = get_view(
            right_clicked="object.right_clicked",
            right_clicked_index="object.right_clicked_index",
        )
        with reraise_exceptions(), self.setup_gui(model, view) as editor:

            self.assertEqual(model.right_clicked, "")
            self.assertEqual(model.right_clicked_index, 0)

            right_click_center(editor)
            process_cascade_events()

            self.assertEqual(model.right_clicked, "")
            self.assertEqual(model.right_clicked_index, 0)


class TestListStrEditorSelection(BaseTestMixin, unittest.TestCase):
    def setUp(self):
        BaseTestMixin.setUp(self)

    def tearDown(self):
        BaseTestMixin.tearDown(self)

    @requires_toolkit([ToolkitName.wx])
    def test_wx_list_str_selected_index(self):
        # behavior: when starting up, the

        obj = ListStrEditorWithSelectedIndex(
            values=["value1", "value2"], selected_index=1
        )
        with reraise_exceptions(), create_ui(
            obj, dict(view=single_select_view)
        ) as ui:
            editor = ui.get_editors("values")[0]
            # the following is equivalent to setting the text in the text
            # control, then pressing OK

            selected_1 = get_selected_indices(editor)

            obj.selected_index = 0
            selected_2 = get_selected_indices(editor)

        # the number traits should be between 3 and 8
        self.assertEqual(selected_1, [1])
        self.assertEqual(selected_2, [0])

    @requires_toolkit([ToolkitName.wx])
    def test_wx_list_str_multi_selected_index(self):
        # behavior: when starting up, the

        obj = ListStrEditorWithSelectedIndex(
            values=["value1", "value2"], selected_indices=[1]
        )
        with reraise_exceptions(), create_ui(
            obj, dict(view=multi_select_view)
        ) as ui:
            editor = ui.get_editors("values")[0]
            # the following is equivalent to setting the text in the text
            # control, then pressing OK

            selected_1 = get_selected_indices(editor)

            obj.selected_indices = [0]
            selected_2 = get_selected_indices(editor)

        # the number traits should be between 3 and 8
        self.assertEqual(selected_1, [1])
        self.assertEqual(selected_2, [0])

    @requires_toolkit([ToolkitName.qt])
    def test_selection_listener_disconnected(self):
        """Check that selection listeners get correctly disconnected"""
        from pyface.qt.QtGui import QApplication, QItemSelectionModel
        from pyface.ui.qt.util.testing import event_loop

        obj = ListStrEditorWithSelectedIndex(values=["value1", "value2"])

        with reraise_exceptions():
            qt_app = QApplication.instance()
            if qt_app is None:
                qt_app = QApplication([])

            # open the UI and run until the dialog is closed
            with create_ui(obj, dict(view=single_select_item_view)) as ui:
                pass

            # now run again and change the selection
            with create_ui(
                obj, dict(view=single_select_item_view)
            ) as ui, event_loop():
                editor = ui.get_editors("values")[0]

                list_view = editor.list_view
                mi = editor.model.index(1)
                list_view.selectionModel().select(
                    mi, QItemSelectionModel.SelectionFlag.ClearAndSelect
                )

        obj.selected = "value2"


if __name__ == "__main__":
    # Executing the file opens the dialog for manual testing
    editor = ListStrEditorWithSelectedIndex(
        values=["value1", "value2"], selected_index=1
    )
    editor.configure_traits(view=single_select_view)
