#------------------------------------------------------------------------------
#
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#
#  This software is provided without warranty under the terms of the BSD
#  license included in enthought/LICENSE.txt and may be redistributed only
#  under the conditions described in the aforementioned license.  The license
#  is also available online at http://www.enthought.com/licenses/BSD.txt
#
#  Author: Pietro Berkes
#  Date:   Feb 2012
#
#------------------------------------------------------------------------------

"""
Test cases for the UI object.
"""

from __future__ import absolute_import
import nose

from traits.has_traits import HasTraits, HasStrictTraits
from traits.trait_types import Str, Int
import traitsui
from traitsui.item import Item, spring
from traitsui.view import View

from traitsui.tests._tools import *


class FooDialog(HasTraits):
    """Test dialog that does nothing useful."""

    my_int = Int(2)
    my_str = Str('hallo')

    traits_view = View(
        Item('my_int'),
        Item('my_str'),
        buttons=['OK']
    )


class DisallowNewTraits(HasStrictTraits):
    """ Make sure no extra traits are added.
    """
    x = Int(10)

    traits_view = View(
        Item('x'),
        spring,
    )


@skip_if_not_wx
def test_reset_with_destroy_wx():
    # Characterization test:
    # UI.reset(destroy=True) destroys all ui children of the top control

    foo = FooDialog()
    ui = foo.edit_traits()

    ui.reset(destroy=True)

    # the top control is still there
    nose.tools.assert_is_not_none(ui.control)
    # but its children are gone
    nose.tools.assert_equal(len(ui.control.GetChildren()), 0)


@skip_if_not_qt4
def test_reset_with_destroy_qt():
    # Characterization test:
    # UI.reset(destroy=True) destroys all ui children of the top control

    from pyface import qt

    foo = FooDialog()
    ui = foo.edit_traits()

    # decorate children's `deleteLater` function to check that it is called
    # on `reset`. check only with the editor parts (only widgets are scheduled,
    # see traitsui.qt4.toolkit.GUIToolkit.destroy_children)
    for c in ui.control.children():
        c.deleteLater = count_calls(c.deleteLater)

    ui.reset(destroy=True)

    # the top control is still there
    nose.tools.assert_is_not_none(ui.control)

    # but its children are scheduled for removal
    for c in ui.control.children():
        if isinstance(c, qt.QtGui.QWidget):
            nose.tools.assert_equal(c.deleteLater._n_calls, 1)


@skip_if_not_wx
def test_reset_without_destroy_wx():
    # Characterization test:
    # UI.reset(destroy=False) destroys all editor controls, but leaves editors
    # and ui children intact

    import wx

    foo = FooDialog()
    ui = foo.edit_traits()

    nose.tools.assert_equal(len(ui._editors), 2)
    nose.tools.assert_is_instance(ui._editors[0],
                                  traitsui.wx.text_editor.SimpleEditor)
    nose.tools.assert_is_instance(ui._editors[0].control,
                                  wx._controls.TextCtrl)

    ui.reset(destroy=False)

    nose.tools.assert_equal(len(ui._editors), 2)
    nose.tools.assert_is_instance(ui._editors[0],
                                  traitsui.wx.text_editor.SimpleEditor)
    nose.tools.assert_is_none(ui._editors[0].control)

    # children are still there: check first text control
    text_ctrl = ui.control.FindWindowByName('text')
    nose.tools.assert_is_not_none(text_ctrl)


@skip_if_not_qt4
def test_reset_without_destroy_qt():
    # Characterization test:
    # UI.reset(destroy=False) destroys all editor controls, but leaves editors
    # and ui children intact

    from pyface import qt

    foo = FooDialog()
    ui = foo.edit_traits()

    nose.tools.assert_equal(len(ui._editors), 2)
    nose.tools.assert_is_instance(ui._editors[0],
                                  traitsui.qt4.text_editor.SimpleEditor)
    nose.tools.assert_is_instance(ui._editors[0].control,
                                  qt.QtGui.QLineEdit)

    ui.reset(destroy=False)

    nose.tools.assert_equal(len(ui._editors), 2)
    nose.tools.assert_is_instance(ui._editors[0],
                                  traitsui.qt4.text_editor.SimpleEditor)
    nose.tools.assert_is_none(ui._editors[0].control)

    # children are still there: check first text control
    text_ctrl = ui.control.findChild(qt.QtGui.QLineEdit)
    nose.tools.assert_is_not_none(text_ctrl)


@skip_if_not_wx
def test_destroy_after_ok_wx():
    # Behavior: after pressing 'OK' in a dialog, the method UI.finish is
    # called and the view control and its children are destroyed

    import wx

    foo = FooDialog()
    ui = foo.edit_traits()

    # keep reference to the control to check that it was destroyed
    control = ui.control

    # decorate control's `Destroy` function to check that it is called
    control.Destroy = count_calls(control.Destroy)

    # press the OK button and close the dialog
    okbutton = ui.control.FindWindowByName('button')
    click_event = wx.CommandEvent(wx.wxEVT_COMMAND_BUTTON_CLICKED,
                                  okbutton.GetId())
    okbutton.ProcessEvent(click_event)

    nose.tools.assert_is_none(ui.control)
    nose.tools.assert_equal(control.Destroy._n_calls, 1)


@skip_if_not_qt4
def test_destroy_after_ok_qt():
    # Behavior: after pressing 'OK' in a dialog, the method UI.finish is
    # called and the view control and its children are destroyed

    from pyface import qt

    foo = FooDialog()
    ui = foo.edit_traits()

    # keep reference to the control to check that it was deleted
    control = ui.control

    # decorate control's `deleteLater` function to check that it is called
    control.deleteLater = count_calls(control.deleteLater)

    # press the OK button and close the dialog
    okb = control.findChild(qt.QtGui.QPushButton)
    okb.click()

    nose.tools.assert_is_none(ui.control)
    nose.tools.assert_equal(control.deleteLater._n_calls, 1)


@skip_if_null
def test_no_spring_trait():
    obj = DisallowNewTraits()
    ui = obj.edit_traits()
    ui.dispose()

    nose.tools.assert_true('spring' not in obj.traits())
