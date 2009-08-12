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
#  Author: Evan Patterson
#  Date:   08/11/2009
#
#------------------------------------------------------------------------------

""" Defines the various image enumeration editors for the PyQt user interface
    toolkit.
"""

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from PyQt4 import QtCore, QtGui

# FIXME: ToolkitEditorFactory is a proxy class defined here just for backward
# compatibility. The class has been moved to the 
# enthought.traits.ui.editors.image_enum_editor file.
from enthought.traits.ui.editors.image_enum_editor  import ToolkitEditorFactory

from editor import Editor
from enum_editor import BaseEditor as BaseEnumEditor
from enum_editor import SimpleEditor as SimpleEnumEditor
from enum_editor import RadioEditor as CustomEnumEditor
from helper import pixmap_cache

#-------------------------------------------------------------------------------
#  'BaseImageEnumEditor' class:
#-------------------------------------------------------------------------------

class BaseEditor(object):
    """ The base class for the different styles of ImageEnumEditor.
    """

    def get_pixmap(self, name):
        """ Get a pixmap representing a possible object traits value.
        """
        factory = self.factory
        name = ''.join((factory.prefix, name, factory.suffix))
        return pixmap_cache(name, factory._image_path)

#-------------------------------------------------------------------------------
#  'ReadonlyEditor' class:
#-------------------------------------------------------------------------------
                               
class ReadonlyEditor(BaseEditor, BaseEnumEditor):
    """ Read-only style of image enumeration editor, which displays a single
        static image representing the object trait's value.
    """

    #---------------------------------------------------------------------------
    #  Finishes initializing the editor by creating the underlying toolkit
    #  widget:
    #---------------------------------------------------------------------------
        
    def init(self, parent):
        """ Finishes initializing the editor by creating the underlying toolkit
            widget.
        """
        self.control = QtGui.QLabel()
        self.control.setPixmap(self.get_pixmap(self.str_value))
        self.set_tooltip()
        
    #---------------------------------------------------------------------------
    #  Updates the editor when the object trait changes external to the editor:
    #---------------------------------------------------------------------------
        
    def update_editor(self):
        """ Updates the editor when the object trait changes externally to the 
            editor.
        """
        self.control.setPixmap(self.get_pixmap(self.str_value))

#-------------------------------------------------------------------------------
#  'SimpleEditor' class:
#-------------------------------------------------------------------------------
                               
class SimpleEditor(BaseEditor, SimpleEnumEditor):
    """ Simple style of image enumeration editor, which displays a combo box.
    """

    #---------------------------------------------------------------------------
    #  Finishes initializing the editor by creating the underlying toolkit
    #  widget:
    #---------------------------------------------------------------------------
        
    def init(self, parent):
        """ Finishes initializing the editor by creating the underlying toolkit
            widget.
        """
        super(SimpleEditor, self).init(parent)
        control = self.control

        # Compute the size of the largest image
        size = QtCore.QSize()
        for name in self.names:
            size = size.expandedTo(self.get_pixmap(name).size())

        # Compute and set the optimal size of the combo box
        option = QtGui.QStyleOptionComboBox()
        control.initStyleOption(option)
        size = control.style().sizeFromContents(QtGui.QStyle.CT_ComboBox,
                                                option, size, control)
        control.setMaximumSize(size)
        control.setSizePolicy(QtGui.QSizePolicy.Expanding, 
                              QtGui.QSizePolicy.Expanding)

        # Set a delegate for drawing the combo box
        control.installEventFilter(ImageEnumComboPainter(self, control))

        # Set a delegate for drawing the items in the popup menu
        control.setItemDelegate(ImageEnumItemDelegate(self, control))

#-------------------------------------------------------------------------------
#  'CustomEditor' class:
#-------------------------------------------------------------------------------
                               
class CustomEditor(BaseEditor, CustomEnumEditor):
    """ Simple style of image enumeration editor, which displays a combo box.
    """

    #---------------------------------------------------------------------------
    #  Returns the QAbstractButton used for the radio button:
    #---------------------------------------------------------------------------

    def create_button(self, name):
        """ Returns the QAbstractButton used for the radio button.
        """
        button = QtGui.QToolButton()
        button.setAutoExclusive(True)
        button.setCheckable(True)

        pixmap = self.get_pixmap(name)
        button.setIcon(QtGui.QIcon(pixmap))
        button.setIconSize(pixmap.size())

        return button
        
#-------------------------------------------------------------------------------
#  Custom renderers used in the SimpleEditor:
#-------------------------------------------------------------------------------

class ImageEnumComboPainter(QtCore.QObject):
    """ An event filter which reimplements paintEvent for QComboBoxes to draw
        images.
    """

    def __init__(self, editor, parent):
        """ Reimplemented to store the editor.
        """
        QtCore.QObject.__init__(self, parent)
        self._editor = editor

    def eventFilter(self, obj, event):
        """ Draw the ComboBox frame and paint the image centered in it.
        """
        if (not isinstance(obj, QtGui.QComboBox) or 
            event.type() != QtCore.QEvent.Paint):
            return False

        painter = QtGui.QStylePainter(obj)
        painter.setPen(obj.palette().color(QtGui.QPalette.Text))
        
        option = QtGui.QStyleOptionComboBox()
        obj.initStyleOption(option)
        painter.drawComplexControl(QtGui.QStyle.CC_ComboBox, option)

        pixmap = self._editor.get_pixmap(self._editor.str_value)
        arrow = obj.style().subControlRect(QtGui.QStyle.CC_ComboBox, option,
                                           QtGui.QStyle.SC_ComboBoxArrow)
        option.rect.setWidth(option.rect.width() - arrow.width())
        target = QtGui.QStyle.alignedRect(QtCore.Qt.LeftToRight, 
                                          QtCore.Qt.AlignCenter,
                                          pixmap.size(), option.rect)
        painter.drawPixmap(target, pixmap)

        event.accept()
        return True

class ImageEnumItemDelegate(QtGui.QStyledItemDelegate):
    """ An item delegate which draws only images.
    """

    def __init__(self, editor, parent):
        """ Reimplemented to store the editor.
        """
        QtGui.QStyledItemDelegate.__init__(self, parent)
        self._editor = editor

    def displayText(self, value, locale):
        """ Reimplemented to display nothing.
        """
        return QtCore.QString()

    def paint(self, painter, option, index):
        """ Reimplemented to draw images.
        """
        # Delegate to our superclass to draw the background
        QtGui.QStyledItemDelegate.paint(self, painter, option, index)
        
        # Now draw the pixmap
        pixmap = self._editor.get_pixmap(self._editor.names[index.row()])
        target = QtGui.QStyle.alignedRect(QtCore.Qt.LeftToRight, 
                                          QtCore.Qt.AlignCenter,
                                          pixmap.size(), option.rect)
        painter.drawPixmap(target, pixmap)

    def sizeHint(self, option, index):
        """ Reimplemented to define a size hint based on the size of the pixmap.
        """
        pixmap = self._editor.get_pixmap(self._editor.names[index.row()])
        return pixmap.size()
