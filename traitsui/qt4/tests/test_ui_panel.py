import unittest

from traits.api import HasTraits, Int, Str, Instance
from traitsui.api import View, Item, Group
from traitsui.menu import ToolBar, Action

from traitsui.tests._tools import (
    create_ui,
    requires_toolkit,
    process_cascade_events,
    ToolkitName,
)


class FooPanel(HasTraits):

    my_int = Int(2)
    my_str = Str("I am a panel/subpanel")
    toolbar = Instance(ToolBar)

    def default_traits_view(self):
        view = View(
            Item(name="my_int"),
            Item(name="my_str"),
            title="FooPanel",
            buttons=["OK", "Cancel"],
            toolbar=self.toolbar,
        )
        return view

    def _toolbar_default(self):
        return ToolBar(Action(name="Open file"))


class FooDialog(HasTraits):

    panel1 = Instance(FooPanel)
    panel2 = Instance(FooPanel)

    view = View(
        Group(Item("panel1"), Item("panel2"), layout="split", style="custom")
    )

    def _panel1_default(self):
        return FooPanel()

    def _panel2_default(self):
        return FooPanel()


class ScrollableGroupExample(HasTraits):

    my_int = Int(2)

    my_str = Str("The group is scrollable")


scrollable_group_view = View(
    Group(
        Item(name="my_int"),
        Item(name="my_str"),
        scrollable=True,
    ),
    title="FooPanel",
    kind='subpanel',
)

non_scrollable_group_view = View(
    Group(
        Item(name="my_int"),
        Item(name="my_str"),
        scrollable=False,
    ),
    title="FooPanel",
    kind='subpanel',
)

scrollable_group_box_view = View(
    Group(
        Item(name="my_int"),
        Item(name="my_str"),
        scrollable=True,
        label="Scrollable View",
        show_border=True,
    ),
    title="FooPanel",
    kind='subpanel',
)

scrollable_labelled_group_view = View(
    Group(
        Item(name="my_int"),
        Item(name="my_str"),
        scrollable=True,
        label="Scrollable View",
    ),
    title="FooPanel",
    kind='subpanel',
)


@requires_toolkit([ToolkitName.qt])
class TestUIPanel(unittest.TestCase):
    def setup_qt4_dock_window(self):
        from pyface.qt import QtGui

        # set up the dock window for qt
        main_window = QtGui.QMainWindow()
        self.addCleanup(process_cascade_events)
        self.addCleanup(main_window.close)
        dock = QtGui.QDockWidget("testing", main_window)
        dock.setWidget(QtGui.QMainWindow())
        return main_window, dock

    def test_panel_has_toolbar_buttons_qt4(self):
        from pyface.qt import QtGui

        _, dock = self.setup_qt4_dock_window()

        # add panel
        panel = FooPanel()
        with create_ui(panel, dict(parent=dock.widget(), kind="panel")) as ui:
            dock.widget().setCentralWidget(ui.control)

            # There should be a toolbar for the panel
            self.assertIsNotNone(dock.findChild(QtGui.QToolBar))

            # There should be buttons too
            # Not searching from dock because the dock panel has buttons for
            # popping up and closing the panel
            self.assertIsNotNone(ui.control.findChild(QtGui.QPushButton))

    def test_subpanel_has_toolbar_no_buttons_qt4(self):
        from pyface.qt import QtGui

        _, dock = self.setup_qt4_dock_window()

        # add panel
        panel = FooPanel()
        parent = dock.widget()
        with create_ui(panel, dict(parent=parent, kind="subpanel")) as ui:
            dock.widget().setCentralWidget(ui.control)

            # There should be a toolbar for the subpanel
            self.assertIsNotNone(dock.findChild(QtGui.QToolBar))

            # Buttons should not be shown for subpanel
            # Not searching from dock because the dock panel has buttons for
            # popping up and closing the panel
            self.assertIsNone(ui.control.findChild(QtGui.QPushButton))

    def test_subpanel_no_toolbar_nor_button_in_widget(self):
        from pyface.qt import QtGui

        # FooDialog uses a QWidget to contain the panels
        # No attempt should be made for adding the toolbars
        foo_window = FooDialog()
        with create_ui(foo_window) as ui:
            # No toolbar for the dialog
            self.assertIsNone(ui.control.findChild(QtGui.QToolBar))

            # No button
            self.assertIsNone(ui.control.findChild(QtGui.QPushButton))


@requires_toolkit([ToolkitName.qt])
class TestPanelLayout(unittest.TestCase):

    def test_scrollable_group_typical(self):
        from pyface.qt import QtGui

        example = ScrollableGroupExample()

        ui = example.edit_traits(view=scrollable_group_view)
        try:
            mainwindow = ui.control.layout().itemAt(0).widget()
            scroll_area = mainwindow.centralWidget()
            self.assertIsInstance(scroll_area, QtGui.QScrollArea)
            content = scroll_area.widget()
            self.assertEqual(type(content), QtGui.QWidget)
        finally:
            ui.dispose()

    def test_scrollable_group_box(self):
        from pyface.qt import QtGui

        example = ScrollableGroupExample()

        ui = example.edit_traits(view=scrollable_group_box_view)
        try:
            mainwindow = ui.control.layout().itemAt(0).widget()
            scroll_area = mainwindow.centralWidget()
            self.assertIsInstance(scroll_area, QtGui.QScrollArea)
            group_box = scroll_area.widget()
            self.assertIsInstance(group_box, QtGui.QGroupBox)
            self.assertEqual(group_box.title(), "Scrollable View")
        finally:
            ui.dispose()

    def test_scrollable_labelled_group(self):
        from pyface.qt import QtGui

        example = ScrollableGroupExample()

        ui = example.edit_traits(view=scrollable_labelled_group_view)
        try:
            mainwindow = ui.control.layout().itemAt(0).widget()
            scroll_area = mainwindow.centralWidget()
            self.assertIsInstance(scroll_area, QtGui.QScrollArea)
            content = scroll_area.widget()
            self.assertEqual(type(content), QtGui.QWidget)
        finally:
            ui.dispose()

    def test_non_scrollable_group_typical(self):
        from pyface.qt import QtGui

        example = ScrollableGroupExample(my_str="The group is not scrollable")

        ui = example.edit_traits(view=non_scrollable_group_view)
        try:
            mainwindow = ui.control.layout().itemAt(0).widget()
            content = mainwindow.centralWidget()
            self.assertEqual(type(content), QtGui.QWidget)
        finally:
            ui.dispose()
