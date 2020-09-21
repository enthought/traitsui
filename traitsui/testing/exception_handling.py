#  Copyright (c) 2005-2020, Enthought, Inc.
#  All rights reserved.
#
#  This software is provided without warranty under the terms of the BSD
#  license included in LICENSE.txt and may be redistributed only
#  under the conditions described in the aforementioned license.  The license
#  is also available online at http://www.enthought.com/licenses/BSD.txt
#
#  Thanks for using Enthought open source!
#

from contextlib import contextmanager
import logging
import sys
import traceback

from traits.api import (
    pop_exception_handler,
    push_exception_handler,
)

_TRAITSUI_LOGGER = logging.getLogger("traitsui")


def _serialize_exception(exc_type, value, tb):
    """ Serialize exception and traceback for reporting.
    This is such that the stack frame is not prevented from being garbage
    collected.
    """
    return (
        str(exc_type),
        str(value),
        str("".join(traceback.format_exception(exc_type, value, tb)))
    )


@contextmanager
def reraise_exceptions(logger=_TRAITSUI_LOGGER):
    """ Context manager to capture all exceptions occurred in the context and
    then reraise a RuntimeError if there are any exceptions captured.

    Exceptions from traits change notifications are also captured and reraised.

    Depending on the GUI toolkit backend, unexpected exceptions occurred in the
    GUI event loop may (1) cause fatal early exit of the test suite or (2) be
    printed to the console without causing the test to error. This context
    manager is intended for testing purpose such that unexpected exceptions
    will result in a test error.

    Parameters
    ----------
    logger : logging.Logger
        Logger to use for logging errors.
    """
    serialized_exceptions = []

    def excepthook(type, value, tb):
        serialized = _serialize_exception(type, value, tb)
        serialized_exceptions.append(serialized)
        logger.error(
            "Unexpected error captured in sys excepthook. \n%s",
            serialized[-1]
        )

    def handler(object, name, old, new):
        type, value, tb = sys.exc_info()
        serialized_exceptions.append(_serialize_exception(type, value, tb))
        logger.exception(
            "Unexpected error occurred from change handler "
            "(object: %r, name: %r, old: %r, new: %r).",
            object, name, old, new,
        )

    push_exception_handler(handler=handler)
    sys.excepthook = excepthook
    try:
        yield
    finally:
        sys.excepthook = sys.__excepthook__
        pop_exception_handler()
        if serialized_exceptions:
            msg = "Uncaught exceptions found.\n"
            msg += "\n".join(
                "=== Exception (type: {}, value: {}) ===\n"
                "{}".format(*record)
                for record in serialized_exceptions
            )
            raise RuntimeError(msg)
