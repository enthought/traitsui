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
#  Date:   Jan 2012
#
#------------------------------------------------------------------------------

from functools import partial
from contextlib import contextmanager
import nose

import sys
import traceback

from traits.etsconfig.api import ETSConfig
import traits.trait_notifiers

# ######### Testing tools

@contextmanager
def store_exceptions_on_all_threads():
    """Context manager that captures all exceptions, even those coming from
    the UI thread. On exit, the first exception is raised (if any).

    It also temporarily overwrites the global function
    traits.trait_notifier.handle_exception , which logs exceptions to
    console without re-raising them by default.
    """

    exceptions = []

    def _print_uncaught_exception(type, value, tb):
        message = 'Uncaught exception:\n'
        message += ''.join(traceback.format_exception(type, value, tb))
        print message

    def excepthook(type, value, tb):
        exceptions.append(value)
        _print_uncaught_exception(type, value, tb)

    def handle_exception(object, trait_name, old, new):
        type, value, tb = sys.exc_info()
        exceptions.append(value)
        _print_uncaught_exception(type, value, tb)

    _original_handle_exception = traits.trait_notifiers.handle_exception
    try:
        sys.excepthook = excepthook
        traits.trait_notifiers.handle_exception = handle_exception
        yield
    finally:
        if len(exceptions) > 0:
            raise exceptions[0]
        sys.excepthook = sys.__excepthook__
        traits.trait_notifiers.handle_exception = _original_handle_exception


def _is_current_backend(backend_name=''):
    return ETSConfig.toolkit == backend_name


def skip_if_not_backend(test_func, backend_name=''):
    """Decorator that skip tests if the backend is not the desired one."""

    if not _is_current_backend(backend_name):
        # preserve original name so that it appears in the report
        orig_name = test_func.__name__
        def test_func():
            raise nose.SkipTest
        test_func.__name__ = orig_name

    return test_func


#: Return True if current backend is 'wx'
is_current_backend_wx = partial(_is_current_backend, backend_name='wx')

#: Return True if current backend is 'qt4'
is_current_backend_qt4 = partial(_is_current_backend, backend_name='qt4')

#: Return True if current backend is 'null'
is_current_backend_null = partial(_is_current_backend, backend_name='null')


#: Test decorator: Skip test if backend is not 'wx'
skip_if_not_wx = partial(skip_if_not_backend, backend_name='wx')

#: Test decorator: Skip test if backend is not 'qt4'
skip_if_not_qt4 = partial(skip_if_not_backend, backend_name='qt4')

#: Test decorator: Skip test if backend is not 'null'
skip_if_not_null = partial(skip_if_not_backend, backend_name='null')


def skip_if_null(test_func):
    """Decorator that skip tests if the backend is set to 'null'.

    Some tests handle both wx and Qt in one go, but many things are not
    defined in the null backend. Use this decorator to skip the test.
    """

    if _is_current_backend('null'):
        # preserve original name so that it appears in the report
        orig_name = test_func.__name__
        def test_func():
            raise nose.SkipTest
        test_func.__name__ = orig_name

    return test_func


def count_calls(func):
    """Decorator that stores the number of times a function is called.

    The counter is stored in func._n_counts.
    """

    def wrapped(*args, **kwargs):
        wrapped._n_calls += 1
        return func(*args, **kwargs)

    wrapped._n_calls = 0

    return wrapped


# ######### Utility tools to test on both qt4 and wx

def get_children(node):
    if ETSConfig.toolkit == 'wx':
        return node.GetChildren()
    else:
        return node.children()


def press_ok_button(ui):
    """Press the OK button in a wx or qt dialog."""

    if is_current_backend_wx():
        import wx

        ok_button = ui.control.FindWindowByName('button')
        click_event = wx.CommandEvent(wx.wxEVT_COMMAND_BUTTON_CLICKED,
                                      ok_button.GetId())
        ok_button.ProcessEvent(click_event)

    elif is_current_backend_qt4():
        from pyface import qt

        # press the OK button and close the dialog
        ok_button = ui.control.findChild(qt.QtGui.QPushButton)
        ok_button.click()


def get_dialog_size(ui_control):
    """Return the size of the dialog.

    Return a tuple (width, height) with the size of the dialog in pixels.
    E.g.:

        >>> get_dialog_size(ui.control)
    """

    if is_current_backend_wx():
        return ui_control.GetSizeTuple()

    elif is_current_backend_qt4():
        return ui_control.size().width(), ui_control.size().height()


# ######### Debug tools

def apply_on_children(func, node, _level=0):
    """Print the result of applying a function on `node` and its children.
    """
    print '-'*_level + str(node)
    print ' '*_level + str(func(node)) + '\n'
    for child in get_children(node):
        apply_on_children(func, child, _level+1)


def wx_print_names(node):
    """Print the name and id of `node` and its children.

    Use as::

        >>> ui = xxx.edit_traits()
        >>> wx_print_names(ui.control)
    """
    apply_on_children(lambda n: (n.GetName(), n.GetId()), node)


def qt_print_names(node):
    """Print the name of `node` and its children.

    Use as::

        >>> ui = xxx.edit_traits()
        >>> qt_print_names(ui.control)
    """
    apply_on_children(lambda n: n.objectName(), node)


def wx_announce_when_destroyed(node):
    """Prints a message when `node` is destroyed.

    Use as:

        >>> ui = xxx.edit_traits()
        >>> apply_on_children(wx_announce_when_destroyed, ui.control)
    """

    _destroy_method = node.Destroy

    def destroy_wrapped():
        print 'Destroying:', node
        #print 'Stack is'
        #traceback.print_stack()
        _destroy_method()
        print 'Destroyed:', node

    node.Destroy = destroy_wrapped
    return 'Node {} decorated'.format(node.GetName())


def wx_find_event_by_number(evt_num):
    """Find all wx event names that correspond to a certain event number.

    Example:

        >>> wx_find_event_by_number(10010)
        ['wxEVT_COMMAND_MENU_SELECTED', 'wxEVT_COMMAND_TOOL_CLICKED']
    """

    import wx
    possible = [attr for attr in dir(wx)
                if attr.startswith('wxEVT') and getattr(wx, attr) == evt_num]

    return possible
