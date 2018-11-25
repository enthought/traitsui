from __future__ import absolute_import
import unittest

from traits.api import HasTraits, Int, Str, Instance
from traitsui.api import View, Item, Group
from traitsui.menu import ToolBar, Action

from traitsui.tests._tools import skip_if_not_qt4


class FooPanel(HasTraits):

    my_int = Int(2)
    my_str = Str("I am a panel/subpanel")
    toolbar = Instance(ToolBar)

    def default_traits_view(self):
        view = View(
            Item(name='my_int'),
            Item(name='my_str'),
            title="FooPanel",
            buttons=["OK", "Cancel"],
            toolbar=self.toolbar)
        return view

    def _toolbar_default(self):
        return ToolBar(Action(name="Open file"))


class FooDialog(HasTraits):

    panel1 = Instance(FooPanel)
    panel2 = Instance(FooPanel)

    view = View(
        Group(Item("panel1"),
              Item("panel2"),
              layout="split",
              style="custom"))

    def _panel1_default(self):
        return FooPanel()

    def _panel2_default(self):
        return FooPanel()


@skip_if_not_qt4
class TestUIPanel(unittest.TestCase):

    def setup_qt4_dock_window(self):
        from pyface.qt import QtGui

        # set up the dock window for qt
        main_window = QtGui.QMainWindow()
        dock = QtGui.QDockWidget("testing", main_window)
        dock.setWidget(QtGui.QMainWindow())
        return main_window, dock

    def test_panel_has_toolbar_buttons_qt4(self):
        from pyface.qt import QtGui

        _, dock = self.setup_qt4_dock_window()

        # add panel
        panel = FooPanel()
        ui = panel.edit_traits(parent=dock.widget(), kind="panel")
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
        ui = panel.edit_traits(parent=dock.widget(), kind="subpanel")
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
        ui = foo_window.edit_traits()

        # No toolbar for the dialog
        self.assertIsNone(ui.control.findChild(QtGui.QToolBar))

        # No button
        self.assertIsNone(ui.control.findChild(QtGui.QPushButton))
