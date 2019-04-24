#------------------------------------------------------------------------------
#
#  Copyright (c) 2005, Enthought, Inc.
#  All rights reserved.
#
#  This software is provided without warranty under the terms of the BSD
#  license included in enthought/LICENSE.txt and may be redistributed only
#  under the conditions described in the aforementioned license.  The license
#  is also available online at http://www.enthought.com/licenses/BSD.txt
#
#  Thanks for using Enthought open source!
#
#  Author: David C. Morrill
#  Date:   10/21/2004
#
#------------------------------------------------------------------------------

""" Defines the HTML "editor" for the wxPython user interface toolkit.
    HTML editors interpret and display HTML-formatted text, but do not
    modify it.
"""

#-------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------

from __future__ import absolute_import
import os.path
import webbrowser

import wx.html as wh

from traits.api import Str

# FIXME: ToolkitEditorFactory is a proxy class defined here just for backward
# compatibility. The class has been moved to the
# traitsui.editors.html_editor file.
from traitsui.editors.html_editor import ToolkitEditorFactory

from .editor import Editor

#-------------------------------------------------------------------------
#  URLResolvingHtmlWindow class:
#-------------------------------------------------------------------------


class URLResolvingHtmlWindow(wh.HtmlWindow):
    """ Overrides OnOpeningURL method of HtmlWindow to append the base URL
        local links.
    """

    def __init__(self, parent, open_externally, base_url):
        wh.HtmlWindow.__init__(self, parent)
        self.open_externally = open_externally
        self.base_url = base_url

    def OnLinkClicked(self, link_info):
        """ Handle the base url and opening in a new browser window for links.
        """
        if self.open_externally:
            url = link_info.GetHref()
            if (self.base_url and
                    not url.startswith(('http://', 'https://'))):
                url = self.base_url + url
            if not url.startswith(('file://', 'http://', 'https://')):
                url = 'file://' + url
            webbrowser.open_new(url)

    def OnOpeningURL(self, url_type, url):
        """ According to the documentation, this method is supposed to be called
            for both images and link clicks, but it appears to only be called
            for image loading, hence the base url handling code in
            OnLinkClicked.
        """
        if (self.base_url and not os.path.isabs(url) and
                not url.startswith(('http://', 'https://', self.base_url))):
            return self.base_url + url
        else:
            return wh.HTML_OPEN

#-------------------------------------------------------------------------
#  'SimpleEditor' class:
#-------------------------------------------------------------------------


class SimpleEditor(Editor):
    """ Simple style of editor for HTML, which displays interpreted HTML.
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
        self.control = URLResolvingHtmlWindow(parent,
                                              self.factory.open_externally,
                                              self.base_url)
        self.control.SetBorders(2)

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
        self.control.SetPage(text)

    #-- Event Handlers -------------------------------------------------------

    def _base_url_changed(self):
        url = self.base_url
        if not url.endswith('/'):
            url += '/'
        self.control.base_url = url
        self.update_editor()

#--EOF-------------------------------------------------------------------------
