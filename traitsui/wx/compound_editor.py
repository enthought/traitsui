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

""" Defines the compound editor and the compound editor factory for the
    wxPython user interface toolkit.
"""

#-------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------

from __future__ import absolute_import
import wx

from traits.api \
    import Str

# FIXME: ToolkitEditorFactory is a proxy class defined here just for backward
# compatibility. The class has been moved to the
# traitsui.editors.compound_editor file.
from traitsui.editors.compound_editor \
    import ToolkitEditorFactory

from .editor \
    import Editor

from .helper \
    import TraitsUIPanel

#-------------------------------------------------------------------------
#  'CompoundEditor' class:
#-------------------------------------------------------------------------


class CompoundEditor(Editor):
    """ Editor for compound traits, which displays editors for each of the
    combined traits, in the appropriate style.
    """
    #-------------------------------------------------------------------------
    #  Trait definitions:
    #-------------------------------------------------------------------------

    # The kind of editor to create for each list item
    kind = Str

    #-------------------------------------------------------------------------
    #  Finishes initializing the editor by creating the underlying toolkit
    #  widget:
    #-------------------------------------------------------------------------

    def init(self, parent):
        """ Finishes initializing the editor by creating the underlying toolkit
            widget.
        """
        # Create a panel to hold all of the component trait editors:
        self.control = panel = TraitsUIPanel(parent, -1)
        sizer = wx.BoxSizer(wx.VERTICAL)

        # Add all of the component trait editors:
        self._editors = editors = []
        for factory in self.factory.editors:
            editor = getattr(
                factory,
                self.kind)(
                self.ui,
                self.object,
                self.name,
                self.description,
                panel)
            editor.prepare(panel)
            sizer.Add(editor.control, 1,
                      wx.TOP | wx.BOTTOM | editor.layout_style, 3)
            editors.append(editor)

        # Set-up the layout:
        panel.SetSizerAndFit(sizer)

        self.set_tooltip()

    #-------------------------------------------------------------------------
    #  Updates the editor when the object trait changes external to the editor:
    #-------------------------------------------------------------------------

    def update_editor(self):
        """ Updates the editor when the object trait changes externally to the
            editor.
        """
        pass

    #-------------------------------------------------------------------------
    #  Disposes of the contents of an editor:
    #-------------------------------------------------------------------------

    def dispose(self):
        """ Disposes of the contents of an editor.
        """
        for editor in self._editors:
            editor.dispose()

        super(CompoundEditor, self).dispose()

#-------------------------------------------------------------------------
#  'SimpleEditor' class:
#-------------------------------------------------------------------------


class SimpleEditor(CompoundEditor):

    # The kind of editor to create for each list item. This value overrides
    # the default.
    kind = 'simple_editor'

#-------------------------------------------------------------------------
#  'CustomEditor' class:
#-------------------------------------------------------------------------


class CustomEditor(CompoundEditor):

    # The kind of editor to create for each list item. This value overrides
    # the default.

    kind = 'custom_editor'

#-- EOF ----------------------------------------------------------------------
