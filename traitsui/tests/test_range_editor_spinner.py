"""
Test case for bug (wx, Max OS X)

Editing the text part of a spin control box and pressing the OK button
without de-focusing raises an AttributeError

Traceback (most recent call last):
  File "ETS/traitsui/traitsui/wx/range_editor.py", line 783, in update_object
    self.value = self.control.GetValue()
AttributeError: 'NoneType' object has no attribute 'GetValue'
"""

from traits.has_traits import HasTraits
from traits.trait_types import Int
from traitsui.item import Item
from traitsui.view import View
from traitsui.editors.range_editor import RangeEditor

from _tools import *


class NumberWithSpinnerEditor(HasTraits):
    """Dialog containing a RangeEditor in 'spinner' mode for an Int.
    """

    number = Int

    traits_view = View(
        Item(label="Enter 4, then press OK without defocusing"),
        Item('number', editor=RangeEditor(low=3, high=8, mode='spinner')),
        buttons = ['OK']
    )


@skip_if_not_wx
def test_wx_spin_control_editing_should_not_crash():
    # Bug: when editing the text part of a spin control box, pressing
    # the OK button raises an AttributeError on Mac OS X

    import wx

    try:
        with store_exceptions_on_all_threads():
            num = NumberWithSpinnerEditor()
            ui = num.edit_traits()

            # the following is equivalent to clicking in the text control of the
            # range editor, enter a number, and clicking ok without defocusing

            # SpinCtrl object
            spin = ui.control.FindWindowByName('wxSpinCtrl')
            spin.SetFocusFromKbd()

            # on Windows, a wxSpinCtrl does not have children, and we cannot do
            # the more fine-grained testing below
            if len(spin.GetChildren()) == 0:
                spin.SetValueString('4')
            else:
                # TextCtrl object of the spin control
                spintxt = spin.FindWindowByName('text')
                spintxt.SetValue('4')

            # press the OK button and close the dialog
            okbutton = ui.control.FindWindowByName('button')
            click_event = wx.CommandEvent(wx.wxEVT_COMMAND_BUTTON_CLICKED,
                                          okbutton.GetId())
            okbutton.ProcessEvent(click_event)
    except AttributeError:
        # if all went well, we should not be here
        assert False, "AttributeError raised"



@skip_if_not_wx
def test_wx_spin_control_editing_does_not_update():
    # Bug: when editing the text part of a spin control box, pressing
    # the OK button does not update the value of the HasTraits class
    # on Mac OS X

    import wx

    with store_exceptions_on_all_threads():
        num = NumberWithSpinnerEditor()
        ui = num.edit_traits()

        # the following is equivalent to clicking in the text control of the
        # range editor, enter a number, and clicking ok without defocusing

        # SpinCtrl object
        spin = ui.control.FindWindowByName('wxSpinCtrl')
        spin.SetFocusFromKbd()

        # on Windows, a wxSpinCtrl does not have children, and we cannot do
        # the more fine-grained testing below
        if len(spin.GetChildren()) == 0:
            spin.SetValueString('4')
        else:
            # TextCtrl object of the spin control
            spintxt = spin.FindWindowByName('text')
            spintxt.SetValue('4')

        # press the OK button and close the dialog
        okbutton = ui.control.FindWindowByName('button')
        click_event = wx.CommandEvent(wx.wxEVT_COMMAND_BUTTON_CLICKED,
                                      okbutton.GetId())
        okbutton.ProcessEvent(click_event)

        # if all went well, the number traits has been updated and its value is 4
        assert num.number == 4


@skip_if_not_qt4
def test_qt_spin_control_editing():
    # Behavior: when editing the text part of a spin control box, pressing
    # the OK button updates the value of the HasTraits class

    from pyface import qt

    with store_exceptions_on_all_threads():
        num = NumberWithSpinnerEditor()
        ui = num.edit_traits()

        # the following is equivalent to clicking in the text control of the
        # range editor, enter a number, and clicking ok without defocusing

        # text element inside the spin control
        lineedit = ui.control.findChild(qt.QtGui.QLineEdit)
        lineedit.setFocus()
        lineedit.setText('4')

        # press the OK button and close the dialog
        okb = ui.control.findChild(qt.QtGui.QPushButton)
        okb.click()

    # if all went well, the number traits has been updated and its value is 4
    assert num.number == 4


if __name__ == '__main__':
    # Executing the file opens the dialog for manual testing
    num = NumberWithSpinnerEditor()
    num.configure_traits()
    print num.number
