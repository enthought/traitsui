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

import wx.html as wh
    
# FIXME: ToolkitEditorFactory is a proxy class defined here just for backward
# compatibility. The class has been moved to the 
# enthought.traits.ui.editors.html_editor file.
from enthought.traits.ui.editors.html_editor \
    import ToolkitEditorFactory
    
from editor  \
    import Editor
    
#-------------------------------------------------------------------------------
#  Constants:
#-------------------------------------------------------------------------------

# Template used to create code blocks embedded in the module comment
block_template = """<center><table width="95%%"><tr><td bgcolor="#ECECEC"><tt>
%s</tt></td></tr></table></center>"""

# Template used to create lists embedded in the module comment
list_template = """<%s>
%s
</%s>"""
                                      
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
        
    #---------------------------------------------------------------------------
    #  Finishes initializing the editor by creating the underlying toolkit
    #  widget:
    #---------------------------------------------------------------------------
        
    def init ( self, parent ):
        """ Finishes initializing the editor by creating the underlying toolkit
            widget.
        """
        self.control = wh.HtmlWindow( parent )
        self.control.SetBorders( 2 )
        
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

#--EOF-------------------------------------------------------------------------
