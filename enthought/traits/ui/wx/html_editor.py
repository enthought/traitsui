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

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

import webbrowser

import wx.html as wh

from enthought.traits.api import Str
    
# FIXME: ToolkitEditorFactory is a proxy class defined here just for backward
# compatibility. The class has been moved to the 
# enthought.traits.ui.editors.html_editor file.
from enthought.traits.ui.editors.html_editor import ToolkitEditorFactory
    
from editor import Editor

#-------------------------------------------------------------------------------
#  URLResolvingHtmlWindow class:
#-------------------------------------------------------------------------------

class URLResolvingHtmlWindow( wh.HtmlWindow ):
    """ Overrides OnOpeningURL method of HtmlWindow to append the base URL
        local links.
    """

    def __init__( self, parent, base_url ):
        wh.HtmlWindow.__init__( self, parent )
        self.base_url = base_url

    def OnOpeningURL( self, url_type, url ):
        if (not self.base_url or
            url.startswith( ( 'http://', 'https://', self.base_url ) )):
            return wh.HTML_OPEN
        else:
            return self.base_url + url 
                                      
#-------------------------------------------------------------------------------
#  'SimpleEditor' class:
#-------------------------------------------------------------------------------
                               
class SimpleEditor ( Editor ):
    """ Simple style of editor for HTML, which displays interpreted HTML.
    """
    #---------------------------------------------------------------------------
    #  Trait definitions:  
    #---------------------------------------------------------------------------
        
    # Is the HTML editor scrollable? This values override the default.
    scrollable = True

    # External objects referenced in the HTML are relative to this URL
    base_url = Str
        
    #---------------------------------------------------------------------------
    #  Finishes initializing the editor by creating the underlying toolkit
    #  widget:
    #---------------------------------------------------------------------------
        
    def init ( self, parent ):
        """ Finishes initializing the editor by creating the underlying toolkit
            widget.
        """
        self.base_url = self.factory.base_url
        self.sync_value( self.factory.base_url_name, 'base_url', 'from' )
        
        self.control = URLResolvingHtmlWindow( parent , self.base_url )
        self.control.SetBorders( 2 )

        wh.EVT_HTML_LINK_CLICKED( self.control, self.control.GetId(), 
                                  self._link_clicked )
        
    #---------------------------------------------------------------------------
    #  Updates the editor when the object trait changes external to the editor:
    #---------------------------------------------------------------------------
        
    def update_editor ( self ):
        """ Updates the editor when the object trait changes external to the 
            editor.
        """
        text = self.str_value
        if self.factory.format_text:
            text = self.factory.parse_text( text )
        self.control.SetPage( text )
        
    #-- Event Handlers ---------------------------------------------------------

    def _base_url_changed(self):
        if self.control:
            self.control.base_url = self.base_url
            self.update_editor()

    def _link_clicked(self, event):
        if self.factory.open_externally:
            url = event.GetLinkInfo().GetHref()
            webbrowser.open_new( url )
        else:
            event.Skip()

#--EOF-------------------------------------------------------------------------
