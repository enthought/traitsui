import unittest

from traits.api import HasTraits, Int, Str, Instance
from traitsui.api import View, Item
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


@skip_if_not_qt4
class TestUIPanel_Qt4(unittest.TestCase):

    def setup_qt4_dock_window(self):
        from pyface.qt import QtGui

        # set up the dock window for qt
        main_window = QtGui.QMainWindow()
        dock = QtGui.QDockWidget("testing", main_window)
        dock.setWidget(QtGui.QMainWindow())
        return main_window, dock

    def test_panel_has_toolbar_buttons_qt4(self):
        from pyface.qt import QtGui

        main_window, dock = self.setup_qt4_dock_window()

        # add panel
        panel = FooPanel()
        ui = panel.edit_traits(parent=dock.widget(), kind="panel")
        dock.widget().setCentralWidget(ui.control)

        # There should be a toolbar for the panel
        self.assertIsNotNone(dock.findChild(QtGui.QToolBar))
        # There should be buttons too
        self.assertIsNotNone(dock.findChild(QtGui.QPushButton))

    def test_subpanel_has_toolbar_no_buttons_qt4(self):
        from pyface.qt import QtGui

        main_window, dock = self.setup_qt4_dock_window()

        # add panel
        panel = FooPanel()
        ui = panel.edit_traits(parent=dock.widget(), kind="subpanel")
        dock.widget().setCentralWidget(ui.control)

        # There should be a toolbar for the panel
        self.assertIsNotNone(dock.findChild(QtGui.QToolBar))
        # Buttons should not be shown for subpanel
        self.assertIsNone(dock.findChild(QtGui.QPushButton))
