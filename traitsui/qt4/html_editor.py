#------------------------------------------------------------------------------
#
#  Copyright (c) 2009, Enthought, Inc.
#  All rights reserved.
#
#  This software is provided without warranty under the terms of the BSD
#  license included in enthought/LICENSE.txt and may be redistributed only
#  under the conditions described in the aforementioned license.  The license
#  is also available online at http://www.enthought.com/licenses/BSD.txt
#
#  Thanks for using Enthought open source!
#
#------------------------------------------------------------------------------

""" Defines the HTML "editor" for the QT4 user interface toolkit.
    HTML editors interpret and display HTML-formatted text, but do not
    modify it.
"""

#-------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------

from __future__ import absolute_import
import webbrowser

from pyface.qt import QtCore, QtGui, QtWebKit

from traits.api import Str

from .editor import Editor

#-------------------------------------------------------------------------
#  'SimpleEditor' class:
#-------------------------------------------------------------------------


class SimpleEditor(Editor):
    """ Simple style editor for HTML.
    """

    #-------------------------------------------------------------------------
    #  Trait definitions:
    #-------------------------------------------------------------------------

    # Is the HTML editor scrollable? This values override the default.
    scrollable = True

    # External objects referenced in the HTML are relative to this URL
    base_url = Str

    #-------------------------------------------------------------------------
    #  Finishes initializing the editor by creating the underlying toolkit
    #  widget:
    #-------------------------------------------------------------------------

    def init(self, parent):
        """ Finishes initializing the editor by creating the underlying toolkit
            widget.
        """
        self.control = QtWebKit.QWebView()
        self.control.setSizePolicy(QtGui.QSizePolicy.Expanding,
                                   QtGui.QSizePolicy.Expanding)

        if self.factory.open_externally:
            page = self.control.page()
            page.setLinkDelegationPolicy(QtWebKit.QWebPage.DelegateAllLinks)
            page.linkClicked.connect(self._link_clicked)

        self.base_url = self.factory.base_url
        self.sync_value(self.factory.base_url_name, 'base_url', 'from')

    #-------------------------------------------------------------------------
    #  Updates the editor when the object trait changes external to the editor:
    #-------------------------------------------------------------------------

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

    #-- Event Handlers -------------------------------------------------------

    def _base_url_changed(self):
        self.update_editor()

    def _link_clicked(self, url):
        webbrowser.open_new(url.toString())

#-EOF--------------------------------------------------------------------------
