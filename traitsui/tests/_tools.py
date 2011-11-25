from functools import partial
from contextlib import contextmanager
import nose

import sys
import traceback


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
        def test_func():
            raise nose.SkipTest
    return test_func


skip_if_not_wx = partial(skip_if_not_backend, backend_name='wx')
skip_if_not_qt4 = partial(skip_if_not_backend, backend_name='qt4')
