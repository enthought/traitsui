#------------------------------------------------------------------------------
# Copyright (c) 2005, Enthought, Inc.
# All rights reserved.
# 
# This software is provided without warranty under the terms of the BSD
# license included in enthought/LICENSE.txt and may be redistributed only
# under the conditions described in the aforementioned license.  The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
# Thanks for using Enthought open source!
# 
# Author: Enthought, Inc.
# Description: <Enthought pyface package component>
#------------------------------------------------------------------------------


# Major package imports.
import wx.stc

# Enthought library imports.
from enthought.traits.api import Bool, Event, implements, Unicode

# Local imports.
from enthought.pyface.i_python_editor import IPythonEditor, MPythonEditor
from enthought.pyface.key_pressed_event import KeyPressedEvent
from enthought.pyface.util.python_stc import PythonSTC, faces
from widget import Widget


class PythonEditor(MPythonEditor, Widget):
    """ The toolkit specific implementation of a PythonEditor.  See the
    IPythonEditor interface for the API documentation.
    """

    implements(IPythonEditor)

    #### 'IPythonEditor' interface ############################################

    dirty = Bool(False)

    path = Unicode

    show_line_numbers = Bool(True)
    
    #### Events ####

    changed = Event

    key_pressed = Event(KeyPressedEvent)
    
    ###########################################################################
    # 'object' interface.
    ###########################################################################
    
    def __init__(self, parent, **traits):
        """ Creates a new pager. """

        # Base class constructor.
        super(PythonEditor, self).__init__(**traits)

        # Create the toolkit-specific control that represents the widget.
        self.control = self._create_control(parent)

        return

    ###########################################################################
    # 'PythonEditor' interface.
    ###########################################################################
    
    def load(self, path=None):
        """ Loads the contents of the editor. """
        
        if path is None:
            path = self.path

        # We will have no path for a new script.
        if len(path) > 0:
            f = open(self.path, 'r')
            text = f.read()
            f.close()

        else:
            text = ''
        
        self.control.SetText(text)
        self.dirty = False

        return

    def save(self, path=None):
        """ Saves the contents of the editor. """

        if path is None:
            path = self.path

        f = file(path, 'w')
        f.write(self.control.GetText())
        f.close()
        
        self.dirty = False

        return

    def set_style(self, n, fore, back):

        self.control.StyleSetForeground(n, fore)
        #self.StyleSetBackground(n, '#c0c0c0')
        #self.StyleSetBackground(n, '#ffffff')
        self.control.StyleSetBackground(n, back)
        self.control.StyleSetFaceName(n, "courier new")
        self.control.StyleSetSize(n, faces['size'])

        #self.StyleSetForeground(n, "#f0f0f0")
        ##self.StyleSetBackground(n, "#000000")
        #self.StyleSetFaceName(n, "courier new")
        #self.StyleSetSize(n, 20)
        #self.StyleSetUnderline(n, 1)
        #self.StyleSetItalic(n, 1)
        #self.StyleSetBold(n, 1)
        #StyleClearAll
        #StyleResetDefault
        #StyleSetCase
        #StyleSetChangeable
        #StyleSetCharacterSet
        #StyleSetEOLFilled
        #StyleSetFont
        #StyleSetFontAttr
        #StyleSetHotSpot
        #StyleSetSpec --- batch
        #StyleSetVisible

        return

    def select_line(self, lineno):
        """ Selects the specified line. """

        start = self.control.PositionFromLine(lineno)
        end   = self.control.GetLineEndPosition(lineno)

        self.control.SetSelection(start, end)

        return

    ###########################################################################
    # Trait handlers.
    ###########################################################################

    def _path_changed(self):
        """ Handle a change to path. """

        self._changed_path()

        return

    ###########################################################################
    # Private interface.
    ###########################################################################

    def _create_control(self, parent):
        """ Creates the toolkit-specific control for the widget. """
        
        # Base-class constructor.
        self.control = stc = PythonSTC(parent, -1)
        
        # No folding!
        stc.SetProperty("fold", "0")

        # Mark the maximum line size.
        stc.SetEdgeMode(wx.stc.STC_EDGE_LINE)
        stc.SetEdgeColumn(79)

        # Display line numbers in the margin.
        if self.show_line_numbers:
            stc.SetMarginType(1, wx.stc.STC_MARGIN_NUMBER)
            stc.SetMarginWidth(1, 45)
            self.set_style(wx.stc.STC_STYLE_LINENUMBER, "#000000", "#c0c0c0")
        else:
            stc.SetMarginWidth(1, 4)
            self.set_style(wx.stc.STC_STYLE_LINENUMBER, "#ffffff", "#ffffff")

        # Create 'tabs' out of spaces!
        stc.SetUseTabs(False)

        # One 'tab' is 4 spaces.
        stc.SetIndent(4)

        # Line ending mode.
        stc.SetEOLMode(wx.stc.STC_EOL_LF) # Unix
        #self.SetEOLMode(wx.stc.STC_EOL_CR) # Apple Mac
        #self.SetEOLMode(wx.stc.STC_EOL_CRLF) # Windows

        ##########################################
        # Global styles for all languages.
        ##########################################

        self.set_style(wx.stc.STC_STYLE_DEFAULT, "#000000", "#ffffff")
        self.set_style(wx.stc.STC_STYLE_CONTROLCHAR, "#000000", "#ffffff")
        self.set_style(wx.stc.STC_STYLE_BRACELIGHT, "#000000", "#ffffff")
        self.set_style(wx.stc.STC_STYLE_BRACEBAD, "#000000", "#ffffff")
         
        ##########################################
        # Python styles.
        ##########################################
        
        # White space
        self.set_style(wx.stc.STC_P_DEFAULT, "#000000", "#ffffff")

        # Comment
        self.set_style(wx.stc.STC_P_COMMENTLINE, "#007f00", "#ffffff")

        # Number
        self.set_style(wx.stc.STC_P_NUMBER, "#007f7f", "#ffffff")

        # String
        self.set_style(wx.stc.STC_P_STRING, "#7f007f", "#ffffff")

        # Single quoted string
        self.set_style(wx.stc.STC_P_CHARACTER, "#7f007f", "#ffffff")

        # Keyword
        self.set_style(wx.stc.STC_P_WORD, "#00007f", "#ffffff")

        # Triple quotes
        self.set_style(wx.stc.STC_P_TRIPLE, "#7f0000", "#ffffff")

        # Triple double quotes
        self.set_style(wx.stc.STC_P_TRIPLEDOUBLE, "#ff0000", "#ffffff")

        # Class name definition
        self.set_style(wx.stc.STC_P_CLASSNAME, "#0000ff", "#ffffff")

        # Function or method name definition
        self.set_style(wx.stc.STC_P_DEFNAME, "#007f7f", "#ffffff")

        # Operators
        self.set_style(wx.stc.STC_P_OPERATOR, "#000000", "#ffffff")

        # Identifiers
        self.set_style(wx.stc.STC_P_IDENTIFIER, "#000000", "#ffffff")

        # Comment-blocks
        self.set_style(wx.stc.STC_P_COMMENTBLOCK, "#007f00", "#ffffff")

        # End of line where string is not closed
        self.set_style(wx.stc.STC_P_STRINGEOL, "#000000", "#ffffff")

        ##########################################
        # Events.
        ##########################################

        # Listen for changes to the file.
        wx.stc.EVT_STC_CHANGE(stc, stc.GetId(), self._on_stc_changed)

        # Listen for key press events.
        wx.EVT_CHAR(stc, self._on_char)

        # Load the editor's contents.
        self.load()
        
        return stc
    
    #### wx event handlers ####################################################

    def _on_stc_changed(self, event):
        """ Called whenever a change is made to the text of the document. """

        self.dirty = True
        self.changed = True
        
        # Give other event handlers a chance.
        event.Skip()
        
        return

    def _on_char(self, event):
        """ Called whenever a change is made to the text of the document. """

        self.key_pressed = KeyPressedEvent(
            alt_down     = event.m_altDown == 1,
            control_down = event.m_controlDown == 1,
            shift_down   = event.m_shiftDown == 1,
            key_code     = event.m_keyCode,
            event        = event
        )
        
        # Give other event handlers a chance.
        event.Skip()
        
        return

#### EOF ######################################################################
