from functools import partial
from contextlib import contextmanager
import nose

import sys
import traceback

from traits.etsconfig.api import ETSConfig

# ######### Testing tools

@contextmanager
def store_exceptions_on_all_threads():
    """Context manager that captures all exceptions, even those coming from
    the UI thread. On exit, the first exception is raised (if any).
    """

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

    if ETSConfig.toolkit != backend_name:
        # preserve original name so that it appears in the report
        orig_name = test_func.__name__
        def test_func():
            raise nose.SkipTest
        test_func.__name__ = orig_name

    return test_func


#: Test decorator: Skip test if backend is not 'wx'
skip_if_not_wx = partial(skip_if_not_backend, backend_name='wx')

#: Test decorator: Skip test if backend is not 'qt4'
skip_if_not_qt4 = partial(skip_if_not_backend, backend_name='qt4')


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
    """
    apply_on_children(lambda n: (n.GetName(), n.GetId()), node)


def qt_print_names(node):
    """Print the name of `node` and its children.
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
    """Find all wx event names that correspond to a ceratin event number.

    Example:

        >>> wx_find_event_by_number(10010)
        ['wxEVT_COMMAND_MENU_SELECTED', 'wxEVT_COMMAND_TOOL_CLICKED']
    """

    import wx
    possible = [attr for attr in dir(wx)
                if attr.startswith('wxEVT') and getattr(wx, attr) == evt_num]

    return possible
