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

""" Defines the base wxPython EditorFactory class and classes the various
    styles of editors used in a Traits-based user interface.
"""

#-------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------

from __future__ import absolute_import
import warnings

import wx

from traits.api \
    import TraitError, Any, Bool, Event, Str

from traitsui.editor_factory \
    import EditorFactory as BaseEditorFactory

from .editor \
    import Editor

from .constants \
    import WindowColor

#-------------------------------------------------------------------------
#  'EditorFactory' class
#   Deprecated alias for traitsui.editor_factory.EditorFactory
#-------------------------------------------------------------------------


class EditorFactory(BaseEditorFactory):
    """ Deprecated alias for traitsui.editor_factory.EditorFactory.
    """

    def __init__(self, *args, **kwds):
        super(EditorFactory, self).__init__(*args, **kwds)
        warnings.warn("DEPRECATED: Use traitsui.editor_factory."
                      ".EditorFactory instead.", DeprecationWarning)

#-------------------------------------------------------------------------
#  'SimpleEditor' class:
#-------------------------------------------------------------------------


class SimpleEditor(Editor):
    """ Base class for simple style editors, which displays a text field
        containing the text representation of the object trait value. Clicking
        in the text field displays an editor-specific dialog box for changing
        the value.
    """

    # Has the left mouse button been pressed:
    left_down = Bool(False)

    #-------------------------------------------------------------------------
    #  Finishes initializing the editor by creating the underlying toolkit
    #  widget:
    #-------------------------------------------------------------------------

    def init(self, parent):
        """ Finishes initializing the editor by creating the underlying toolkit
            widget.
        """
        self.control = self.create_control(parent)
        wx.EVT_LEFT_DOWN(self.control, self._enable_popup_editor)
        wx.EVT_LEFT_UP(self.control, self._show_popup_editor)
        self.set_tooltip()

    #-------------------------------------------------------------------------
    #  Creates the control to use for the simple editor:
    #-------------------------------------------------------------------------

    def create_control(self, parent):
        """ Creates the control to use for the simple editor.
        """
        return wx.TextCtrl(parent, -1, self.str_value, style=wx.TE_READONLY)

    #-------------------------------------------------------------------------
    #  Invokes the pop-up editor for an object trait:
    #
    #  (Normally overridden in a subclass)
    #-------------------------------------------------------------------------

    def popup_editor(self, event):
        """ Invokes the pop-up editor for an object trait.
        """
        pass

    def _enable_popup_editor(self, event):
        """ Mark the left mouse button as being pressed currently.
        """
        self.left_down = True

    def _show_popup_editor(self, event):
        """ Display the popup editor if the left mouse button was pressed
            previously.
        """
        if self.left_down:
            self.left_down = False
            self.popup_editor(event)

#-------------------------------------------------------------------------
#  'TextEditor' class:
#-------------------------------------------------------------------------


class TextEditor(Editor):
    """ Base class for text style editors, which displays an editable text
        field, containing a text representation of the object trait value.
    """

    #-------------------------------------------------------------------------
    #  Finishes initializing the editor by creating the underlying toolkit
    #  widget:
    #-------------------------------------------------------------------------

    def init(self, parent):
        """ Finishes initializing the editor by creating the underlying toolkit
            widget.
        """
        self.control = wx.TextCtrl(parent, -1, self.str_value,
                                   style=wx.TE_PROCESS_ENTER)
        wx.EVT_KILL_FOCUS(self.control, self.update_object)
        wx.EVT_TEXT_ENTER(parent, self.control.GetId(), self.update_object)
        self.set_tooltip()

    #-------------------------------------------------------------------------
    #  Handles the user changing the contents of the edit control:
    #-------------------------------------------------------------------------

    def update_object(self, event):
        """ Handles the user changing the contents of the edit control.
        """
        if isinstance(event, wx.FocusEvent):
            event.Skip()
        try:
            self.value = self.control.GetValue()
        except TraitError as excp:
            pass

#-------------------------------------------------------------------------
#  'ReadonlyEditor' class:
#-------------------------------------------------------------------------


class ReadonlyEditor(Editor):
    """ Base class for read-only style editors, which displays a read-only text
        field, containing a text representation of the object trait value.
    """

    #-------------------------------------------------------------------------
    #  Trait definitions:
    #-------------------------------------------------------------------------

    # layout_style = 0  # Style for imbedding control in a sizer (override)

    #-------------------------------------------------------------------------
    #  Finishes initializing the editor by creating the underlying toolkit
    #  widget:
    #-------------------------------------------------------------------------

    def init(self, parent):
        """ Finishes initializing the editor by creating the underlying toolkit
            widget.
        """
        if (self.item.resizable is True) or (self.item.height != -1.0):
            self.control = wx.TextCtrl(
                parent, -1, self.str_value, style=wx.NO_BORDER | wx.TE_MULTILINE | wx.TE_READONLY)
            self.control.SetBackgroundColour(WindowColor)
        else:
            self.control = wx.StaticText(parent, -1, self.str_value,
                                         style=wx.ALIGN_LEFT)
            self.layout_style = 0

        self.set_tooltip()

    #-------------------------------------------------------------------------
    #  Updates the editor when the object trait changes external to the editor:
    #-------------------------------------------------------------------------

    def update_editor(self):
        """ Updates the editor when the object trait changes externally to the
            editor.
        """
        new_value = self.str_value
        if (self.item.resizable is True) or (self.item.height != -1.0):
            if self.control.GetValue() != new_value:
                self.control.SetValue(new_value)
        elif self.control.GetLabel() != new_value:
            self.control.SetLabel(new_value)
