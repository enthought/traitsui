# (C) Copyright 2004-2023 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

""" Defines the HTML "editor" for the QT4 user interface toolkit.
    HTML editors interpret and display HTML-formatted text, but do not
    modify it.
"""


import webbrowser

from pyface.qt import QtCore, QtGui

from traits.api import Str

from .editor import Editor

try:
    from pyface.qt import QtWebKit

    # Subclass of QWebPage for QtWebEngine support

    class ExternallyOpeningWebPage(QtWebKit.QWebPage):
        """QWebEnginePage subclass that opens links in system browser

        This subclass is only used when we are given a QWebEnginePage which is
        pretending to be a QWebPage and we want the open_external feature
        of the Editor.

        This overrides the acceptNavigationRequest method to open links
        in an external browser.  All other navigation requests are handled
        internally as per the base class.
        """

        def acceptNavigationRequest(self, url, type, isMainFrame):
            if type == QtWebKit.QWebPage.NavigationTypeLinkClicked:
                webbrowser.open_new(url.toString())
                return False
            else:
                return super().acceptNavigationRequest(url, type, isMainFrame)

    WebView = QtWebKit.QWebView
    HAS_WEB_VIEW = True

except Exception:
    WebView = QtGui.QTextBrowser
    HAS_WEB_VIEW = False


# -------------------------------------------------------------------------
#  'SimpleEditor' class:
# -------------------------------------------------------------------------


class SimpleEditor(Editor):
    """Simple style editor for HTML."""

    # -------------------------------------------------------------------------
    #  Trait definitions:
    # -------------------------------------------------------------------------

    #: Is the HTML editor scrollable? This values override the default.
    scrollable = True

    #: External objects referenced in the HTML are relative to this URL
    base_url = Str()

    def init(self, parent):
        """Finishes initializing the editor by creating the underlying toolkit
        widget.
        """
        self.control = WebView()
        self.control.setSizePolicy(
            QtGui.QSizePolicy.Policy.Expanding, QtGui.QSizePolicy.Policy.Expanding
        )

        if self.factory.open_externally:
            if HAS_WEB_VIEW:
                page = self.control.page()
                if hasattr(page, 'setLinkDelegationPolicy'):
                    # QtWebKit
                    page.setLinkDelegationPolicy(
                        QtWebKit.QWebPage.DelegateAllLinks
                    )
                    page.linkClicked.connect(self._link_clicked)
                else:
                    # QtWebEngine pretending to be QtWebKit
                    # We need the subclass defined above instead of the
                    # regular web page so that links are opened externally
                    page = ExternallyOpeningWebPage(self.control)
                    self.control.setPage(page)
            else:
                # take over handling clicks on links
                self.control.setOpenLinks(False)
                self.control.anchorClicked.connect(self._link_clicked)

        self.base_url = self.factory.base_url
        self.sync_value(self.factory.base_url_name, "base_url", "from")

    def dispose(self):
        """Disposes of the contents of an editor."""
        if self.control is not None and self.factory.open_externally:
            if HAS_WEB_VIEW:
                page = self.control.page()
                if hasattr(page, 'setLinkDelegationPolicy'):
                    # QtWebKit-only cleanup
                    page.linkClicked.disconnect(self._link_clicked)
            else:
                # QTextBrowser clean-up
                self.control.anchorClicked.disconnect(self._link_clicked)

        super().dispose()

    def update_editor(self):
        """Updates the editor when the object trait changes external to the
        editor.
        """
        text = self.str_value
        if self.factory.format_text:
            text = self.factory.parse_text(text)
        if self.base_url and HAS_WEB_VIEW:
            url = self.base_url
            if not url.endswith("/"):
                url += "/"
            self.control.setHtml(text, QtCore.QUrl.fromLocalFile(url))
        else:
            self.control.setHtml(text)

    # -- Event Handlers -------------------------------------------------------

    def _base_url_changed(self):
        self.update_editor()

    def _link_clicked(self, url):
        webbrowser.open_new(url.toString())
