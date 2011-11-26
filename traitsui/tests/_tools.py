from functools import partial
from contextlib import contextmanager
import nose

import sys
import traceback


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
    from traits.etsconfig.api import ETSConfig

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


# ######### Debug tools

def wx_apply_on_children(func, node, _level=0):
    """Print the result of applying a function on `node` and its children.
    """
    print '-'*_level + str(node)
    print ' '*_level + str(func(node)) + '\n'
    for child in node.GetChildren():
        wx_apply_on_children(func, child, _level+1)


def wx_print_names(node):
    """Print the name of `node` and its children.
    """
    wx_apply_on_children(lambda n: n.GetName(), node)


def wx_announce_when_destroyed(node):
    """Prints a message when `node` is destroyed.

    Use as:

       >>> ui = xxx.edit_traits()
       >>> wx_apply_on_children(wx_announce_when_destroyed, ui.control)
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
