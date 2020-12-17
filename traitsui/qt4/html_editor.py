# ------------------------------------------------------------------------------
#
#  Copyright (c) 2009, Enthought, Inc.
#  All rights reserved.
#
#  This software is provided without warranty under the terms of the BSD
#  license included in LICENSE.txt and may be redistributed only
#  under the conditions described in the aforementioned license.  The license
#  is also available online at http://www.enthought.com/licenses/BSD.txt
#
#  Thanks for using Enthought open source!
#
# ------------------------------------------------------------------------------

""" Defines the HTML "editor" for the QT4 user interface toolkit.
    HTML editors interpret and display HTML-formatted text, but do not
    modify it.
"""


import webbrowser

from pyface.qt import QtCore, QtGui, QtWebKit

from traits.api import Str

from .editor import Editor


# Subclass of QWebPage for QtWebEngine support

class ExternallyOpeningWebPage(QtWebKit.QWebPage):
    """ QWebEnginePage subclass that opens links in system browser

    This subclass is only used when we are given a QWebEnginePage which is
    pretending to be a QWebPage and we want the open_external feature
    of the Editor.

    This overrides the acceptNavigationRequest method to open links
    in an external browser.  All other navigation requests are handled
    internally as per the base class.
    """

    def acceptNavigationRequest(self, url, type, isMainFrame):
        if type == QtWebKit.QWebPage.NavigationType:
            webbrowser.open_new(url.toString())
            return False
        else:
            return super().acceptNavigationRequest(url, type, isMainFrame)


# -------------------------------------------------------------------------
#  'SimpleEditor' class:
# -------------------------------------------------------------------------


class SimpleEditor(Editor):
    """ Simple style editor for HTML.
    """

    # -------------------------------------------------------------------------
    #  Trait definitions:
    # -------------------------------------------------------------------------

    #: Is the HTML editor scrollable? This values override the default.
    scrollable = True

    #: External objects referenced in the HTML are relative to this URL
    base_url = Str()

    def init(self, parent):
        """ Finishes initializing the editor by creating the underlying toolkit
            widget.
        """
        self.control = QtWebKit.QWebView()
        self.control.setSizePolicy(
            QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding
        )

        if self.factory.open_externally:
            page = self.control.page()
            if hasattr(page, 'setLinkDelegationPolicy'):
                # QtWebKit
                page.setLinkDelegationPolicy(
                    QtWebKit.QWebPage.DelegateAllLinks
                )
                page.linkClicked.connect(self._link_clicked)
            else:
                # QtWebEngine pretending to be QtWebKit
                # We need the subclass defined above instead of the regular
                # we page so that links are opened externally
                page = ExternallyOpeningWebPage()
                self.control.setPage(page)

        self.base_url = self.factory.base_url
        self.sync_value(self.factory.base_url_name, "base_url", "from")

    def dispose(self):
        """ Disposes of the contents of an editor.
        """
        if self.control is not None and self.factory.open_externally:
            page = self.control.page()
            if hasattr(page, 'setLinkDelegationPolicy'):
                # QtWebKit-only cleanup
                page.linkClicked.disconnect(self._link_clicked)
        super().dispose()

    def update_editor(self):
        """ Updates the editor when the object trait changes external to the
            editor.
        """
        text = self.str_value
        if self.factory.format_text:
            text = self.factory.parse_text(text)
        if self.base_url:
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
