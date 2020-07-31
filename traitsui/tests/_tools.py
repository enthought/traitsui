# ------------------------------------------------------------------------------
#
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#
#  This software is provided without warranty under the terms of the BSD
#  license included in LICENSE.txt and may be redistributed only
#  under the conditions described in the aforementioned license.  The license
#  is also available online at http://www.enthought.com/licenses/BSD.txt
#
#  Author: Pietro Berkes
#  Date:   Jan 2012
#
# ------------------------------------------------------------------------------

import enum
import re
import sys
import traceback
from functools import partial
from contextlib import contextmanager
from unittest import skipIf, TestSuite
import warnings

from pyface.api import GUI
from pyface.toolkit import toolkit_object
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
        message = "Uncaught exception:\n"
        message += "".join(traceback.format_exception(type, value, tb))
        print(message)

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
        sys.excepthook = sys.__excepthook__
        traits.trait_notifiers.handle_exception = _original_handle_exception
        if len(exceptions) > 0:
            raise exceptions[0]


# Toolkit constants

class ToolkitName(enum.Enum):
    wx = "wx"
    qt = "qt"
    null = "null"


def is_wx():
    """ Return true if the toolkit backend is wx. """
    return ETSConfig.toolkit == ToolkitName.wx.name


def is_qt():
    """ Return true if the toolkit backend is Qt
    (that includes Qt4 or Qt5, etc.)
    """
    return ETSConfig.toolkit.startswith(ToolkitName.qt.name)


def is_null():
    """ Return true if the toolkit backend is null.
    """
    return ETSConfig.toolkit == ToolkitName.null.name


def requires_toolkit(toolkits):
    """ Decorator factory for skipping tests if the current toolkit is not
    one of the given values.

    Parameters
    ----------
    toolkits : iterable of members of ToolkitName
        e.g. ``list(ToolkitName)`` to include all toolkits.
    """
    mapping = {
        ToolkitName.null: is_null,
        ToolkitName.qt: is_qt,
        ToolkitName.wx: is_wx,
    }
    return skipIf(
        not any(mapping[toolkit]() for toolkit in toolkits),
        "Test requires one of these toolkits: {}".format(toolkits)
    )


def _deprecated(func):
    # Emit warning to ease tension across pending pull requests.
    # This function should be removed when no more active PRs are relying
    # on this.
    def wrapped(*args, **kwargs):
        warnings.warn(
            "{!r} will be removed. "
            "Use is_wx, is_qt or is_null or requires_toolkit instead.".format(
                func
            ),
            DeprecationWarning,
            stacklevel=3,
        )
        return func(*args, **kwargs)
    return wrapped


def _is_current_backend(backend_name=""):
    return ETSConfig.toolkit == backend_name


#: Return True if current backend is 'wx'
is_current_backend_wx = _deprecated(
    partial(_is_current_backend, backend_name="wx")
)

#: Return True if current backend is 'qt4'
is_current_backend_qt4 = _deprecated(
    partial(_is_current_backend, backend_name="qt4")
)

#: Return True if current backend is 'null'
is_current_backend_null = _deprecated(
    partial(_is_current_backend, backend_name="null")
)

#: Test decorator: Skip test if backend is not wx
skip_if_not_wx = _deprecated(requires_toolkit([ToolkitName.wx]))

#: Test decorator: Skip test if backend is not qt
skip_if_not_qt4 = _deprecated(requires_toolkit([ToolkitName.qt]))

#: Test decorator: Skip test if backend is not null
skip_if_not_null = _deprecated(requires_toolkit([ToolkitName.null]))

#: Test decorator: Skip test if backend is 'null'
#: For future proofing tests in case of new toolkits, consider using
#: requires_toolkit instead.
skip_if_null = _deprecated(
    skipIf(is_null(), "Test not working on the 'null' backend")
)

#: True if current platform is MacOS
is_mac_os = sys.platform.startswith("darwin")


def count_calls(func):
    """Decorator that stores the number of times a function is called.

    The counter is stored in func._n_counts.
    """

    def wrapped(*args, **kwargs):
        wrapped._n_calls += 1
        return func(*args, **kwargs)

    wrapped._n_calls = 0

    return wrapped


def filter_tests(test_suite, exclusion_pattern):
    filtered_test_suite = TestSuite()
    for item in test_suite:
        if isinstance(item, TestSuite):
            filtered = filter_tests(item, exclusion_pattern)
            filtered_test_suite.addTest(filtered)
        else:
            match = re.search(exclusion_pattern, item.id())
            if match is not None:
                skip_msg = "Test excluded via pattern '{}'".format(
                    exclusion_pattern
                )
                setattr(item, 'setUp', lambda: item.skipTest(skip_msg))
            filtered_test_suite.addTest(item)
    return filtered_test_suite


def process_cascade_events():
    """ Process all posted events, and attempt to process new events posted by
    the processed events.

    Cautions:
    - An infinite cascade of events will cause this function to enter an
      infinite loop.
    - There still exists technical difficulties with Qt. On Qt4 + OSX,
      QEventLoop.processEvents may report false saying it had found no events
      to process even though it actually had processed some.
      Consequently the internal loop breaks too early such that there are
      still cascaded events unprocessed. Problems are also observed on
      Qt5 + Appveyor occasionally. At the very least, events that are already
      posted prior to calling this function will be processed.
      See enthought/traitsui#951
    """
    if is_current_backend_qt4():
        from pyface.qt import QtCore
        event_loop = QtCore.QEventLoop()
        while event_loop.processEvents(QtCore.QEventLoop.AllEvents):
            pass
    else:
        GUI.process_events()


@contextmanager
def create_ui(object, ui_kwargs=None):
    """ Context manager for creating a UI and then dispose it when exiting
    the context.

    Parameters
    ----------
    object : HasTraits
        An object from which ``edit_traits`` can be called to create a UI
    ui_kwargs : dict or None
        Keyword arguments to be provided to ``edit_traits``.

    Yields
    ------
    ui: UI
    """
    ui_kwargs = {} if ui_kwargs is None else ui_kwargs
    ui = object.edit_traits(**ui_kwargs)
    try:
        yield ui
    finally:
        # At the end of a test, there may be events to be processed.
        # If dispose happens first, those events will be processed after
        # various editor states are removed, causing errors.
        process_cascade_events()
        try:
            ui.dispose()
        finally:
            # dispose is not atomic and may push more events to the event
            # queue. Flush those too.
            process_cascade_events()


# ######### Utility tools to test on both qt4 and wx


def get_children(node):
    if ETSConfig.toolkit == "wx":
        return node.GetChildren()
    else:
        return node.children()


def press_ok_button(ui):
    """Press the OK button in a wx or qt dialog."""

    if is_current_backend_wx():
        import wx

        ok_button = ui.control.FindWindowByName("button", ui.control)
        click_event = wx.CommandEvent(
            wx.wxEVT_COMMAND_BUTTON_CLICKED, ok_button.GetId()
        )
        ok_button.ProcessEvent(click_event)

    elif is_current_backend_qt4():
        from pyface import qt

        # press the OK button and close the dialog
        ok_button = ui.control.findChild(qt.QtGui.QPushButton)
        ok_button.click()


def click_button(button):
    """Click the button given its control."""

    if is_current_backend_wx():
        import wx

        event = wx.CommandEvent(wx.EVT_BUTTON.typeId, button.GetId())
        event.SetEventObject(button)
        wx.PostEvent(button, event)

    elif is_current_backend_qt4():
        button.click()

    else:
        raise NotImplementedError()


def is_control_enabled(control):
    """Return if the given control is enabled or not."""

    if is_current_backend_wx():
        return control.IsEnabled()

    elif is_current_backend_qt4():
        return control.isEnabled()

    else:
        raise NotImplementedError()


def get_dialog_size(ui_control):
    """Return the size of the dialog.

    Return a tuple (width, height) with the size of the dialog in pixels.
    E.g.:

        >>> get_dialog_size(ui.control)
    """

    if is_current_backend_wx():
        return ui_control.GetSize()

    elif is_current_backend_qt4():
        return ui_control.size().width(), ui_control.size().height()


def get_all_button_status(control):
    """Get status of all 2-state (wx) or checkable (qt) buttons under given
    control.

    Assumes all sizer children (wx) or layout items (qt) are buttons.
    """
    button_status = []

    if is_current_backend_wx():
        for item in control.GetSizer().GetChildren():
            button = item.GetWindow()
            # Ignore empty buttons (assumption that they are invisible)
            if button.value != "":
                button_status.append(button.GetValue())

    elif is_current_backend_qt4():
        layout = control.layout()
        for i in range(layout.count()):
            button = layout.itemAt(i).widget()
            button_status.append(button.isChecked())

    else:
        raise NotImplementedError()

    return button_status

# ######### Debug tools


def apply_on_children(func, node, _level=0):
    """Print the result of applying a function on `node` and its children.
    """
    print("-" * _level + str(node))
    print(" " * _level + str(func(node)) + "\n")
    for child in get_children(node):
        apply_on_children(func, child, _level + 1)


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
        print("Destroying:", node)
        # print 'Stack is'
        # traceback.print_stack()
        _destroy_method()
        print("Destroyed:", node)

    node.Destroy = destroy_wrapped
    return "Node {} decorated".format(node.GetName())


def wx_find_event_by_number(evt_num):
    """Find all wx event names that correspond to a certain event number.

    Example:

        >>> wx_find_event_by_number(10010)
        ['wxEVT_COMMAND_MENU_SELECTED', 'wxEVT_COMMAND_TOOL_CLICKED']
    """

    import wx

    possible = [
        attr
        for attr in dir(wx)
        if attr.startswith("wxEVT") and getattr(wx, attr) == evt_num
    ]

    return possible


GuiTestAssistant = toolkit_object("util.gui_test_assistant:GuiTestAssistant")
no_gui_test_assistant = GuiTestAssistant.__name__ == "Unimplemented"
if no_gui_test_assistant:

    # ensure null toolkit has an inheritable GuiTestAssistant
    class GuiTestAssistant(object):
        pass
