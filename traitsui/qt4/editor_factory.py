#------------------------------------------------------------------------------
# Copyright (c) 2007, Riverbank Computing Limited
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD license.
# However, when used with the GPL version of PyQt the additional terms described in the PyQt GPL exception also apply

#
# Author: Riverbank Computing Limited
#------------------------------------------------------------------------------

""" Defines the base PyQt classes the various styles of editors used in a
Traits-based user interface.
"""

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from pyface.qt import QtCore, QtGui

from traits.api \
    import TraitError

from traitsui.editor_factory \
    import EditorFactory as BaseEditorFactory

from editor \
    import Editor

#-------------------------------------------------------------------------------
#  'EditorFactory' class
#   Deprecated alias for traitsui.editor_factory.EditorFactory
#-------------------------------------------------------------------------------

class EditorFactory(BaseEditorFactory):
    """ Deprecated alias for traitsui.editor_factory.EditorFactory.
    """

    def __init__(self, *args, **kwds):
        super(EditorFactory, self).__init__(*args, **kwds)
        warnings.warn("DEPRECATED: Use traitsui.editor_factory."
            ".EditorFactory instead.", DeprecationWarning)

#-------------------------------------------------------------------------------
#  'SimpleEditor' class:
#-------------------------------------------------------------------------------

class SimpleEditor ( Editor ):
    """ Base class for simple style editors, which displays a text field
    containing the text representation of the object trait value. Clicking in
    the text field displays an editor-specific dialog box for changing the
    value.
    """
    #---------------------------------------------------------------------------
    #  Finishes initializing the editor by creating the underlying toolkit
    #  widget:
    #---------------------------------------------------------------------------

    def init ( self, parent ):
        """ Finishes initializing the editor by creating the underlying toolkit
            widget.
        """
        self.control = _SimpleField(self)
        self.set_tooltip()

    #---------------------------------------------------------------------------
    #  Invokes the pop-up editor for an object trait:
    #
    #  (Normally overridden in a subclass)
    #---------------------------------------------------------------------------

    def popup_editor(self):
        """ Invokes the pop-up editor for an object trait.
        """
        pass

#-------------------------------------------------------------------------------
#  'TextEditor' class:
#-------------------------------------------------------------------------------

class TextEditor ( Editor ):
    """ Base class for text style editors, which displays an editable text
    field, containing a text representation of the object trait value.
    """
    #---------------------------------------------------------------------------
    #  Finishes initializing the editor by creating the underlying toolkit
    #  widget:
    #---------------------------------------------------------------------------

    def init ( self, parent ):
        """ Finishes initializing the editor by creating the underlying toolkit
            widget.
        """
        self.control = QtGui.QLineEdit(self.str_value)
        QtCore.QObject.connect(self.control,
                QtCore.SIGNAL('editingFinished()'), self.update_object)
        self.set_tooltip()

    #---------------------------------------------------------------------------
    #  Handles the user changing the contents of the edit control:
    #---------------------------------------------------------------------------

    def update_object(self):
        """ Handles the user changing the contents of the edit control.
        """
        try:
            self.value = unicode(self.control.text())
        except TraitError as excp:
            pass

#-------------------------------------------------------------------------------
#  'ReadonlyEditor' class:
#-------------------------------------------------------------------------------

class ReadonlyEditor ( Editor ):
    """ Base class for read-only style editors, which displays a read-only text
    field, containing a text representation of the object trait value.
    """
    #---------------------------------------------------------------------------
    #  Finishes initializing the editor by creating the underlying toolkit
    #  widget:
    #---------------------------------------------------------------------------

    text_alignment_map = {
        'left'    : QtCore.Qt.AlignLeft,
        'right'   : QtCore.Qt.AlignRight,
        'just'    : QtCore.Qt.AlignJustify,
        'top'     : QtCore.Qt.AlignLeft,
        'bottom'  : QtCore.Qt.AlignBottom,
        'vcenter' : QtCore.Qt.AlignVCenter,
        'hcenter' : QtCore.Qt.AlignHCenter,
        'center'  : QtCore.Qt.AlignVCenter | QtCore.Qt.AlignHCenter
    }

    def init ( self, parent ):
        """ Finishes initializing the editor by creating the underlying toolkit
            widget.
        """
        self.control = QtGui.QLabel(self.str_value)

        if self.item.resizable is True or self.item.height != -1.0:
            self.control.setSizePolicy(QtGui.QSizePolicy.Expanding,
                                       QtGui.QSizePolicy.Expanding)
            self.control.setWordWrap(True)

        alignment = None
        for item in self.factory.text_alignment.split(",") :
            item_alignment = self.text_alignment_map.get(item, None)
            if item_alignment :
                if alignment :
                    alignment = alignment | item_alignment
                else :
                    alignment = item_alignment

        if alignment :
            self.control.setAlignment(alignment)

        self.set_tooltip()

    #---------------------------------------------------------------------------
    #  Updates the editor when the object trait changes external to the editor:
    #---------------------------------------------------------------------------

    def update_editor ( self ):
        """ Updates the editor when the object trait changes externally to the
            editor.
        """
        self.control.setText(self.str_value)

#-------------------------------------------------------------------------------
#  '_SimpleField' class:
#-------------------------------------------------------------------------------

class _SimpleField(QtGui.QLineEdit):

    def __init__(self, editor):
        QtGui.QLineEdit.__init__(self, editor.str_value)

        self.setReadOnly(True)
        self._editor = editor

    def mouseReleaseEvent(self, e):
        QtGui.QLineEdit.mouseReleaseEvent(self, e)

        if e.button() == QtCore.Qt.LeftButton:
            self._editor.popup_editor()
