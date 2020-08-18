import contextlib
import logging
import sys
import traceback

from traits.api import (
    pop_exception_handler,
    push_exception_handler,
)

_TRAITSUI_LOGGER = logging.getLogger("traitsui")


def serialize_exception(exc_type, value, tb):
    return (
        str(exc_type),
        str(value),
        str("".join(traceback.format_exception(exc_type, value, tb)))
    )


@contextlib.contextmanager
def reraise_exception():
    """ Context manager to capture errors from traits change notification and
    then reraise when re-raise the first one (if any) when exiting the context
    manager.
    """
    serialized_exceptions = []

    def excepthook(type, value, tb):
        serialized_exceptions.append(serialize_exception(type, value, tb))
        _TRAITSUI_LOGGER.exception(
            "Unexpected error occurred from sys excepthook.",
            exc_info=True,
        )

    def handler(object, name, old, new):
        type, value, tb = sys.exc_info()
        serialized_exceptions.append(serialize_exception(type, value, tb))
        _TRAITSUI_LOGGER.exception(
            "Unexpected error occurred from change handler "
            "(object: %r, name: %r, old: %r, new: %r).",
            object, name, old, new,
            exc_info=True,
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
