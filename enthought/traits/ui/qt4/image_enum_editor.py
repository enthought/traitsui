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
    #  Returns the QComboBox used for the editor control:
    #---------------------------------------------------------------------------

    def create_combo_box(self):
        """ Returns the QComboBox used for the editor control.
        """
        control = ImageEnumComboBox(self)

        # Compute the size of the largest image
        size = QtCore.QSize()
        for name in self.names:
            size = size.expandedTo(self.get_pixmap(name).size())
        
        # Use this to set the optimal size of the combo box
        option = QtGui.QStyleOptionComboBox()
        control.initStyleOption(option)
        size = control.style().sizeFromContents(QtGui.QStyle.CT_ComboBox,
                                                option, size, control)
        control.setMaximumSize(size)
        control.setSizePolicy(QtGui.QSizePolicy.Expanding, 
                              QtGui.QSizePolicy.Expanding)

        return control

    #---------------------------------------------------------------------------
    #  Updates the editor when the object trait changes external to the editor:
    #---------------------------------------------------------------------------
        
    def update_editor ( self ):
        """ Updates the editor when the object trait changes externally to the 
            editor.
        """
        if self._no_enum_update == 0:
            self._no_enum_update += 1
            try:
                index = self.names.index(self.inverse_mapping[self.value])
            except:
                self.control.setCurrentIndex(-1)
            else:
                cols = self.factory.cols
                rows = (len(self.names) + cols - 1) / cols
                row, col = index / cols, index % cols
                self.control.setModelColumn(col)
                self.control.setCurrentIndex(row)
            self._no_enum_update -= 1

    #---------------------------------------------------------------------------
    #  Rebuilds the contents of the editor whenever the original factory 
    #  object's 'values' trait changes:  
    #---------------------------------------------------------------------------
                        
    def rebuild_editor(self):
        """ Rebuilds the contents of the editor whenever the original factory
            object's **values** trait changes.
        """
        self.control.model().reset()

#-------------------------------------------------------------------------------
#  'CustomEditor' class:
#-------------------------------------------------------------------------------
                               
class CustomEditor(BaseEditor, CustomEnumEditor):
    """ Simple style of image enumeration editor, which displays a combo box.
    """

    # Is the button layout row-major or column-major? This value overrides the
    # default.
    row_major = True

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
#  Custom Qt objects used in the SimpleEditor:
#-------------------------------------------------------------------------------

class ImageEnumComboBox(QtGui.QComboBox):
    """ A combo box which displays images instead of text.
    """

    def __init__(self, editor, parent=None):
        """ Reimplemented to store the editor and set a delegate for drawing the
            items in the popup menu. If there is more than one column, use a
            TableView instead of ListView for the popup.
        """
        QtCore.QObject.__init__(self, parent)
        self._editor = editor

        model = ImageEnumModel(editor, self)
        self.setModel(model)

        delegate = ImageEnumItemDelegate(editor, self)
        if editor.factory.cols > 1:
            view = QtGui.QTableView(self)
            view.setItemDelegate(delegate)
            hheader = view.horizontalHeader()
            hheader.setResizeMode(QtGui.QHeaderView.ResizeToContents)
            hheader.hide()
            view.verticalHeader().hide()
            view.setShowGrid(False)
            self.setView(view)

            # Unless we force it, the popup for a combo box will not be wider
            # than the box itself, so we set a high minimum width.
            width = 0
            for col in xrange(self._editor.factory.cols):
                width += view.sizeHintForColumn(col)
            view.setMinimumWidth(width)

        else:
            self.setItemDelegate(delegate)
    
    def paintEvent(self, event):
        """ Reimplemented to draw the ComboBox frame and paint the image 
            centered in it.
        """
        painter = QtGui.QStylePainter(self)
        painter.setPen(self.palette().color(QtGui.QPalette.Text))
        
        option = QtGui.QStyleOptionComboBox()
        self.initStyleOption(option)
        painter.drawComplexControl(QtGui.QStyle.CC_ComboBox, option)

        pixmap = self._editor.get_pixmap(self._editor.str_value)
        arrow = self.style().subControlRect(QtGui.QStyle.CC_ComboBox, option,
                                            QtGui.QStyle.SC_ComboBoxArrow)
        option.rect.setWidth(option.rect.width() - arrow.width())
        target = QtGui.QStyle.alignedRect(QtCore.Qt.LeftToRight, 
                                          QtCore.Qt.AlignCenter,
                                          pixmap.size(), option.rect)
        painter.drawPixmap(target, pixmap)
      
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

    def paint(self, painter, option, mi):
        """ Reimplemented to draw images.
        """
        # Delegate to our superclass to draw the background
        QtGui.QStyledItemDelegate.paint(self, painter, option, mi)
        
        # Now draw the pixmap
        index = mi.row() * self._editor.factory.cols + mi.column()
        pixmap = self._editor.get_pixmap(self._editor.names[index])
        target = QtGui.QStyle.alignedRect(QtCore.Qt.LeftToRight, 
                                          QtCore.Qt.AlignCenter,
                                          pixmap.size(), option.rect)
        painter.drawPixmap(target, pixmap)

    def sizeHint(self, option, mi):
        """ Reimplemented to define a size hint based on the size of the pixmap.
        """
        index = mi.row() * self._editor.factory.cols + mi.column()
        pixmap = self._editor.get_pixmap(self._editor.names[index])
        return pixmap.size()

class ImageEnumModel(QtCore.QAbstractTableModel):
    """ A table model for use with the 'simple' style ImageEnumEditor.
    """

    def __init__(self, editor, parent):
        """ Reimplemented to store the editor.
        """
        QtGui.QStyledItemDelegate.__init__(self, parent)
        self._editor = editor

    def rowCount(self, mi):
        """ Reimplemented to return the number of rows.
        """
        cols = self._editor.factory.cols
        result = (len(self._editor.names) + cols - 1) / cols
        return result

    def columnCount(self, mi):
        """ Reimplemented to return the number of columns.
        """
        return self._editor.factory.cols
    
    def data(self, mi, role):
        """ Reimplemented to return the data. Although we don't care about the
            text, this needs to be implemented for the view on this model to
            function properly.
        """
        if role == QtCore.Qt.DisplayRole:
            index = mi.row() * self._editor.factory.cols + mi.column()
            return QtCore.QVariant(self._editor.names[index])

        return QtCore.QVariant()
