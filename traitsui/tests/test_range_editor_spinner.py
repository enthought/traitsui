from contextlib import contextmanager
from traits.has_traits import HasTraits
from traits.trait_types import Int
from traitsui.item import Item
from traitsui.view import View
from traitsui.editors.range_editor import RangeEditor

from functools import partial
import wx
import nose


class NumberWithSpinnerEditor(HasTraits):
    """Dialog containing a RangeEditor in 'spinner' mode for an Int.
    """

    number = Int

    traits_view = View(
        Item('number', editor=RangeEditor(low=3, high=8, mode='spinner')),
        buttons = ['OK']
    )


@contextmanager
def store_exceptions_on_all_threads():
    """Context manager that captures all exceptions, even those coming from
    the UI thread. On exit, the first exception is raised (if any).
    """

    import sys
    import traceback

    exceptions = []

    def excepthook(type, value, tb):
        exceptions.append(value)
        message = 'Uncaught exception:\n'
        message += ''.join(traceback.format_exception(type, value, tb))
        print message

    try:
        sys.excepthook = excepthook
        yield
    finally:
        if len(exceptions) > 0:
            raise exceptions[0]
        sys.excepthook = sys.__excepthook__


def skip_if_not_backend(test_func, backend_name=''):
    """Decorator that skip tests if the backend is not the desired one."""
    from traits.etsconfig.api import ETSConfig
    if ETSConfig.toolkit != backend_name:
        def test_func():
            raise nose.SkipTest
    return test_func

skip_if_not_wx = partial(skip_if_not_backend, backend_name='wx')
skip_if_not_qt4 = partial(skip_if_not_backend, backend_name='qt4')


@skip_if_not_wx
def test_wx_spin_control_editing():
    # behavior: when editing the text part of a spin control box, pressing
    # the OK button should update the value of the HasTraits class
    # (tests a bug where this fails with an AttributeError

    with store_exceptions_on_all_threads():
        num = NumberWithSpinnerEditor()
        ui = num.edit_traits()

        # the following is equivalent to clicking in the text control of the
        # range editor, enter a number, and clicking ok without defocusing

        # SpinCtrl object
        spin = ui.control.FindWindowByName('wxSpinCtrl')
        spin.SetFocusFromKbd()

        # TextCtrl object of the spin control
        spintxt = spin.FindWindowByName('text')
        # unlike spintxt.SetValue, this method does not fire a
        # wxEVT_COMMAND_TEXT_UPDATED event
        spintxt.ChangeValue('4')

        # make sure that the change in text has not been notified
        assert spin.GetValue() == 3

        # press the OK button and close the dialog
        okbutton = ui.control.FindWindowByName('button')
        click_event = wx.CommandEvent(wx.wxEVT_COMMAND_BUTTON_CLICKED,
                                      okbutton.GetId())
        okbutton.ProcessEvent(click_event)

    # if all went well, the number traits has been updated and its value is 4
    assert num.number == 4


@skip_if_not_qt4
def test_qt_spin_control_editing():
    # behavior: when editing the text part of a spin control box, pressing
    # the OK button should update the value of the HasTraits class

    from pyface import qt

    with store_exceptions_on_all_threads():
        num = NumberWithSpinnerEditor()
        ui = num.edit_traits()

        # the following is equivalent to clicking in the text control of the
        # range editor, enter a number, and clicking ok without defocusing

        # text element inside the spin control
        lineedit = ui.control.findChild(qt.QtGui.QLineEdit)
        lineedit.setFocus()

        # NOTE: I'm not sure at the moment that this is the exact equivalent
        # of the wx test
        lineedit.setText('4')

        # press the OK button and close the dialog
        okb = ui.control.findChild(qt.QtGui.QPushButton)
        okb.click()

    # if all went well, the number traits has been updated and its value is 4
    assert num.number == 4


if __name__ == '__main__':
    num = NumberWithSpinnerEditor()
    num.configure_traits()
