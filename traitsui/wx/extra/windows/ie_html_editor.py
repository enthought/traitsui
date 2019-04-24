#-------------------------------------------------------------------------
#
#  Copyright (c) 2007, Enthought, Inc.
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
#  Date:   03/11/2007
#
#-------------------------------------------------------------------------

""" Traits UI MS Internet Explorer editor.
"""

#-------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------

from __future__ import absolute_import
import re
import webbrowser

import wx


if wx.Platform == '__WXMSW__':
    # The new version of IEHTMLWindow (wx 2.8.8.0) is mostly compatible with
    # the old one, but it has changed the API for handling COM events, so we
    # cannot use it.
    try:
        import wx.lib.iewin_old as iewin
    except ImportError:
        import wx.lib.iewin as iewin

from traits.api \
    import Bool, Event, Property, Str

from traitsui.wx.editor \
    import Editor

from traitsui.basic_editor_factory \
    import BasicEditorFactory

#-------------------------------------------------------------------------
#  Constants
#-------------------------------------------------------------------------

RELATIVE_OBJECTS_PATTERN = re.compile(
    r'src=["\'](?!https?:)([\s\w/\.]+?)["\']', re.IGNORECASE)

#-------------------------------------------------------------------------
#  '_IEHTMLEditor' class:
#-------------------------------------------------------------------------


class _IEHTMLEditor(Editor):
    """ Traits UI MS Internet Explorer editor.
    """

    #-------------------------------------------------------------------------
    #  Trait definitions:
    #-------------------------------------------------------------------------

    # Is the table editor is scrollable? This value overrides the default.
    scrollable = True

    # External objects referenced in the HTML are relative to this url
    base_url = Str

    # Event fired when the browser home page should be displayed:
    home = Event

    # Event fired when the browser should show the previous page:
    back = Event

    # Event fired when the browser should show the next page:
    forward = Event

    # Event fired when the browser should stop loading the current page:
    stop = Event

    # Event fired when the browser should refresh the current page:
    refresh = Event

    # Event fired when the browser should search the current page:
    search = Event

    # The current browser status:
    status = Str

    # The current browser page title:
    title = Str

    # The URL of the page that just finished loading:
    page_loaded = Str

    # The current page content as HTML:
    html = Property

    #-------------------------------------------------------------------------
    #  Finishes initializing the editor by creating the underlying toolkit
    #  widget:
    #-------------------------------------------------------------------------

    def init(self, parent):
        """ Finishes initializing the editor by creating the underlying toolkit
            widget.
        """
        self.control = ie = iewin.IEHtmlWindow(
            parent, -1, style=wx.NO_FULL_REPAINT_ON_RESIZE)
        self.set_tooltip()

        factory = self.factory
        self.base_url = factory.base_url
        self.sync_value(factory.home, 'home', 'from')
        self.sync_value(factory.back, 'back', 'from')
        self.sync_value(factory.forward, 'forward', 'from')
        self.sync_value(factory.stop, 'stop', 'from')
        self.sync_value(factory.refresh, 'refresh', 'from')
        self.sync_value(factory.search, 'search', 'from')
        self.sync_value(factory.status, 'status', 'to')
        self.sync_value(factory.title, 'title', 'to')
        self.sync_value(factory.page_loaded, 'page_loaded', 'to')
        self.sync_value(factory.html, 'html', 'to')
        self.sync_value(factory.base_url_name, 'base_url', 'from')

        parent.Bind(iewin.EVT_StatusTextChange, self._status_modified, ie)
        parent.Bind(iewin.EVT_TitleChange, self._title_modified, ie)
        parent.Bind(iewin.EVT_DocumentComplete, self._page_loaded_modified, ie)
        parent.Bind(iewin.EVT_NewWindow2, self._new_window_modified, ie)
        parent.Bind(iewin.EVT_BeforeNavigate2, self._navigate_requested, ie)

    #-------------------------------------------------------------------------
    #  Updates the editor when the object trait changes external to the editor:
    #-------------------------------------------------------------------------

    def update_editor(self):
        """ Updates the editor when the object trait changes externally to the
            editor.
        """
        value = self.str_value.strip()

        # We can correct URLs via the BeforeNavigate Event, but the COM
        # interface provides no such option for images. Sadly, we are forced
        # to take a more brute force approach.
        if self.base_url:
            rep = lambda m: r'src="%s%s"' % (self.base_url, m.group(1))
            value = re.sub(RELATIVE_OBJECTS_PATTERN, rep, value)

        if value == '':
            self.control.LoadString('<html><body></body></html>')

        elif value[:1] == '<':
            self.control.LoadString(value)

        elif (value[:4] != 'http') or (value.find('://') < 0):
            try:
                with open(value, 'rb') as file:
                    self.control.LoadStream(file)
            except:
                pass

        else:
            self.control.Navigate(value)

    #-- Property Implementations ---------------------------------------------

    def _get_html(self):
        return self.control.GetText()

    def _set_html(self, value):
        self.control.LoadString(value)

    #-- Event Handlers -------------------------------------------------------

    def _home_changed(self):
        self.control.GoHome()

    def _back_changed(self):
        self.control.GoBack()

    def _forward_changed(self):
        self.control.GoForward()

    def _stop_changed(self):
        self.control.Stop()

    def _search_changed(self):
        self.control.GoSearch()

    def _refresh_changed(self):
        self.control.Refresh(iewin.REFRESH_COMPLETELY)

    def _status_modified(self, event):
        self.status = event.Text

    def _title_modified(self, event):
        self.title = event.Text

    def _page_loaded_modified(self, event):
        self.page_loaded = event.URL
        self.trait_property_changed('html', '', self.html)

    def _new_window_modified(self, event):
        # If the event is cancelled, new windows can be disabled.
        # At this point we've opted to allow new windows
        pass

    def _navigate_requested(self, event):
        # The way NavigateToString works is to navigate to about:blank then
        # load the supplied HTML into the document property. This borks
        # relative URLs.
        if event.URL.startswith('about:'):
            base = self.base_url
            if not base.endswith('/'):
                base += '/'
            event.URL = base + event.URL[6:]

        if self.factory.open_externally:
            event.Cancel = True
            webbrowser.get('windows-default').open_new(event.URL)

#-------------------------------------------------------------------------
#  Create the editor factory object:
#-------------------------------------------------------------------------

# wxPython editor factory for MS Internet Explorer editors:


class IEHTMLEditor(BasicEditorFactory):

    # The editor class to be created:
    klass = _IEHTMLEditor

    # External objects referenced in the HTML are relative to this url
    base_url = Str

    # The object trait containing the base URL
    base_url_name = Str

    # Should links be opened in an external browser?
    open_externally = Bool(False)

    # Optional name of trait used to tell browser to show Home page:
    home = Str

    # Optional name of trait used to tell browser to view the previous page:
    back = Str

    # Optional name of trait used to tell browser to view the next page:
    forward = Str

    # Optional name of trait used to tell browser to stop loading page:
    stop = Str

    # Optional name of trait used to tell browser to refresh the current page:
    refresh = Str

    # Optional name of trait used to tell browser to search the current page:
    search = Str

    # Optional name of trait used to contain the current browser status:
    status = Str

    # Optional name of trait used to contain the current browser page title:
    title = Str

    # Optional name of trait used to contain the URL of the page that just
    # completed loading:
    page_loaded = Str

    # Optional name of trait used to get/set the page content as HTML:
    html = Str
