#  Copyright (c) 2005-2020, Enthought, Inc.
#  All rights reserved.
#
#  This software is provided without warranty under the terms of the BSD
#  license included in LICENSE.txt and may be redistributed only
#  under the conditions described in the aforementioned license.  The license
#  is also available online at http://www.enthought.com/licenses/BSD.txt
#
#  Thanks for using Enthought open source!

import unittest
from unittest import mock

from traits.api import HasTraits, Str
from traitsui.api import HTMLEditor, Item, View
from traitsui.tests._tools import (
    BaseTestMixin,
    create_ui,
    is_qt,
    requires_toolkit,
    reraise_exceptions,
    ToolkitName,
)
from traitsui.testing.api import MouseClick, TargetRegistry, UITester


class HTMLModel(HasTraits):
    """ Dummy class for testing HTMLEditor."""

    content = Str()

    model_base_url = Str()


def get_view(base_url_name):
    return View(
        Item(
            "content",
            editor=HTMLEditor(
                format_text=True,
                base_url_name=base_url_name,
            )
        )
    )


class CurrentURL:
    """ Represent a query to obtain the current URL displayed by the
    web page.
    Implementation should return a str.
    """
    pass


class HTMLContent:
    """ Action to retrieve the HTML content currently displayed.
    Implementation should return a str, whose content conforms to HTML markup.
    """
    pass


def _is_webkit_page(page):
    """ Return true if the given page is a QWebPage from QtWebKit.

    Intended for handling the compatibility between QtWebKit and QtWebEngine.

    Parameters
    ----------
    page : QWebEnginePage or QWebPage
    """
    return hasattr(page, "setLinkDelegationPolicy")


def qt_get_page_url(page):
    """ Return the URL (in string format) currently being viewed.

    Parameters
    ----------
    page : QWebEnginePage or QWebPage

    Returns
    -------
    html : str
    """
    qt_allow_page_to_load(page)
    if _is_webkit_page(page):
        return page.mainFrame().url().toString()
    return page.url().toString()


def qt_get_page_html_content(page):
    """ Return the HTML content currently being viewed.

    Parameters
    ----------
    page : QWebEnginePage or QWebPage

    Returns
    -------
    html : str
    """
    qt_allow_page_to_load(page)
    if _is_webkit_page(page):
        return page.mainFrame().toHtml()

    content = []
    page.toHtml(content.append)
    return "".join(content)


def wait_for_qt_signal(qt_signal, timeout):
    """ Wait for the given Qt signal to fire, or timeout.

    A mock implementation of QSignalSpy.wait, which is one of the missing
    bindings in PySide2, and is not available in Qt4.

    Parameters
    ----------
    qt_signal : signal
        Qt signal to wait for
    timeout : int
        Timeout in milliseconds, to match Qt API.

    Raises
    ------
    RuntimeError
    """
    from pyface.qt import QtCore, QtGui

    qt_app = QtGui.QApplication.instance()

    def exit(*args, **kwargs):
        qt_app.quit()

    timeout_timer = QtCore.QTimer()
    timeout_timer.setSingleShot(True)
    timeout_timer.setInterval(timeout)
    timeout_timer.timeout.connect(exit)
    qt_signal.connect(exit)

    timeout_timer.start()
    qt_app.exec_()

    qt_signal.disconnect(exit)
    if timeout_timer.isActive():
        timeout_timer.stop()
    else:
        raise RuntimeError("Timeout waiting for signal.")


def qt_allow_page_to_load(page, step_timeout=0.1):
    """ Allow QWebPage/QWebEnginePage to finish loading.

    Out of context, this function does not know if the page has started
    loading. Therefore it tries to see if the page is busy by watching its
    loadStarted or loadProgress signal. If the loadStarted signal has been
    emitted before this function is called, and/or the loadProgress is taking
    too long to be emitted, then it is possible that the page is not in a
    loaded state when this function returns.

    However for most testing purposes, this function should be good enough to
    avoid interacting with the Qt web page before it has finished loading, at
    a cost of a slower test.

    Parameters
    ----------
    page : QWebPage or QWebEnginePage
        The page to allow loading to finish.
    step_timeout : float
        Timeout in seconds for each signal being observed.
    """

    step_timeout_ms = round(step_timeout * 1000)
    try:
        wait_for_qt_signal(page.loadStarted, timeout=step_timeout_ms)
    except RuntimeError:
        # It might have been started before this function is called.
        # Check for progress too.
        try:
            wait_for_qt_signal(page.loadProgress, timeout=step_timeout_ms)
        except RuntimeError:
            # Probably haven't started.
            return

    wait_for_qt_signal(page.loadFinished, timeout=step_timeout_ms)


def qt_mouse_click_web_view(view, delay):
    """ Perform a mouse click at the center of the web view.

    Note that the page is allowed time to load before and after the mouse
    click.

    Parameters
    ----------
    view : QWebView or QWebEngineView
    """
    from pyface.qt import QtCore
    from pyface.qt.QtTest import QTest

    qt_allow_page_to_load(view.page())

    if view.focusProxy() is not None:
        # QWebEngineView
        widget = view.focusProxy()
    else:
        # QWebView
        widget = view

    try:
        QTest.mouseClick(
            widget,
            QtCore.Qt.LeftButton,
            QtCore.Qt.NoModifier,
            delay=delay,
        )
    finally:
        qt_allow_page_to_load(view.page())


def qt_target_registry():
    """ Return an instance of TargetRegistry for testing Qt + HTMLEditor

    Returns
    -------
    target_registry : TargetRegistry
    """
    from traitsui.qt4.html_editor import SimpleEditor

    registry = TargetRegistry()
    registry.register_interaction(
        target_class=SimpleEditor,
        interaction_class=MouseClick,
        handler=lambda wrapper, _: qt_mouse_click_web_view(
            wrapper._target.control, wrapper.delay
        )
    )
    registry.register_interaction(
        target_class=SimpleEditor,
        interaction_class=CurrentURL,
        handler=lambda wrapper, _: (
            qt_get_page_url(wrapper._target.control.page())
        )
    )
    registry.register_interaction(
        target_class=SimpleEditor,
        interaction_class=HTMLContent,
        handler=lambda wrapper, _: (
            qt_get_page_html_content(wrapper._target.control.page())
        )
    )
    return registry


def get_custom_ui_tester():
    """ Return an instance of UITester that contains extended testing
    functionality for HTMLEditor. These implementations are used by
    TraitsUI only, are more ad hoc than they would have been if they were made
    public.
    """
    if is_qt():
        return UITester(registries=[qt_target_registry()])
    return UITester()


# Run this against wx as well once enthought/traitsui#752 is fixed.
@requires_toolkit([ToolkitName.qt])
class TestHTMLEditor(BaseTestMixin, unittest.TestCase):
    """ Test HTMLEditor """

    def setUp(self):
        BaseTestMixin.setUp(self)
        self.tester = get_custom_ui_tester()

    def tearDown(self):
        BaseTestMixin.tearDown(self)

    def test_init_and_dispose(self):
        # Smoke test to check init and dispose do not fail.
        model = HTMLModel()
        view = get_view(base_url_name="")
        with reraise_exceptions(), \
                create_ui(model, dict(view=view)):
            pass

    def test_base_url_changed(self):
        # Test if the base_url is changed after the UI closes, nothing
        # fails because sync_value is unhooked in the base class.
        model = HTMLModel()
        view = get_view(base_url_name="model_base_url")
        with reraise_exceptions():
            with create_ui(model, dict(view=view)):
                pass
            # It is okay to modify base_url after the UI is closed
            model.model_base_url = "/new_dir"

    @requires_toolkit([ToolkitName.qt])
    def test_open_internal_link(self):
        # this test requires Qt because it relies on the link filling up
        # the entire page through the use of CSS, which isn't supported
        # by Wx.
        model = HTMLModel(content="""
        <html>
            <a
              href='/#'
              target='_self'
              style='display:block; width: 100%; height: 100%'>
                Internal Link
            </a>
        </html>
        """)
        view = View(
            Item("content", editor=HTMLEditor())
        )

        with self.tester.create_ui(model, dict(view=view)) as ui:
            html_view = self.tester.find_by_name(ui, "content")
            self.assertFalse(
                html_view.inspect(CurrentURL()).startswith("about:blank")
            )

            # when
            with mock.patch("webbrowser.open_new") as mocked_browser:
                html_view.perform(MouseClick())

            # then
            self.assertTrue(
                html_view.inspect(CurrentURL()).startswith("about:blank")
            )
        mocked_browser.assert_not_called()

    @requires_toolkit([ToolkitName.qt])
    def test_open_external_link(self):
        # this test requires Qt because it relies on the link filling up
        # the entire page through the use of CSS, which isn't supported
        # by Wx.
        model = HTMLModel(content="""
        <html>
            <a
              href='test://testing'
              target='_blank'
              style='display:block; width: 100%; height: 100%'>
                External Link
            </a>
        </html>
        """)
        view = View(
            Item("content", editor=HTMLEditor())
        )

        with self.tester.create_ui(model, dict(view=view)) as ui:
            html_view = self.tester.find_by_name(ui, "content")
            with mock.patch("webbrowser.open_new") as mocked_browser:
                html_view.perform(MouseClick())
            self.assertIn(
                "External Link",
                html_view.inspect(HTMLContent()),
            )

        # See enthought/traitsui#1464
        # This is the expected behaviour:
        # mocked_browser.assert_called_once_with("test://testing")
        # However, this is the current unexpected behaviour
        mocked_browser.assert_not_called()

    @requires_toolkit([ToolkitName.qt])
    def test_open_internal_link_externally(self):
        # this test requires Qt because it relies on the link filling up
        # the entire page through the use of CSS, which isn't supported
        # by Wx.
        model = HTMLModel(content="""
        <html>
            <a
              href='test://testing'
              target='_self'
              style='display:block; width: 100%; height: 100%'>
                Internal Link
            </a>
        </html>
        """)
        view = View(
            Item("content", editor=HTMLEditor(open_externally=True))
        )

        with self.tester.create_ui(model, dict(view=view)) as ui:
            html_view = self.tester.find_by_name(ui, "content")
            with mock.patch("webbrowser.open_new") as mocked_browser:
                html_view.perform(MouseClick())
            self.assertIn(
                "Internal Link",
                html_view.inspect(HTMLContent()),
            )

        mocked_browser.assert_called_once_with("test://testing")

    @requires_toolkit([ToolkitName.qt])
    def test_open_externally_link_externally(self):
        model = HTMLModel(content="""
        <html>
            <a
              href='test://testing'
              target='_blank'
              style='display:block; width: 100%; height: 100%'>
                External Link
            </a>
        </html>
        """)
        view = View(
            Item("content", editor=HTMLEditor(open_externally=True))
        )

        with self.tester.create_ui(model, dict(view=view)) as ui:
            html_view = self.tester.find_by_name(ui, "content")
            with mock.patch("webbrowser.open_new") as mocked_browser:
                html_view.perform(MouseClick())
            self.assertIn(
                "External Link",
                html_view.inspect(HTMLContent()),
            )

            is_webkit = _is_webkit_page(html_view._target.control.page())

        if is_webkit:
            # This is the expected behavior.
            mocked_browser.assert_called_once_with("test://testing")
        else:
            # Expected failure:
            # See enthought/traitsui#1464
            # This is the current unexpected behavior if QtWebEngine is used.
            mocked_browser.assert_not_called()
