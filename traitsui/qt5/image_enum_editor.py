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

from pyface.qt import QtCore, QtGui

# FIXME: ToolkitEditorFactory is a proxy class defined here just for backward
# compatibility. The class has been moved to the
# traitsui.editors.image_enum_editor file.
from traitsui.editors.image_enum_editor  import ToolkitEditorFactory

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
        if name is None:
            return None
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
        control.setSizePolicy(QtGui.QSizePolicy.Maximum,
                              QtGui.QSizePolicy.Maximum)
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
        QtGui.QComboBox.__init__(self, parent)
        self._editor = editor

        model = ImageEnumModel(editor, self)
        self.setModel(model)

        delegate = ImageEnumItemDelegate(editor, self)
        if editor.factory.cols > 1:
            view = ImageEnumTablePopupView(self)
            view.setItemDelegate(delegate)
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

        editor = self._editor
        pixmap = editor.get_pixmap(editor.inverse_mapping[editor.value])
        arrow = self.style().subControlRect(QtGui.QStyle.CC_ComboBox, option,
                                            QtGui.QStyle.SC_ComboBoxArrow, None)
        option.rect.setWidth(option.rect.width() - arrow.width())
        target = QtGui.QStyle.alignedRect(QtCore.Qt.LeftToRight,
                                          QtCore.Qt.AlignCenter,
                                          pixmap.size(), option.rect)
        painter.drawPixmap(target, pixmap)

    def sizeHint(self):
        """ Reimplemented to set a size hint based on the size of the larget
            image.
        """
        size = QtCore.QSize()
        for name in self._editor.names:
            size = size.expandedTo(self._editor.get_pixmap(name).size())

        option = QtGui.QStyleOptionComboBox()
        self.initStyleOption(option)
        size = self.style().sizeFromContents(QtGui.QStyle.CT_ComboBox, option,
                                             size, self)
        return size


class ImageEnumTablePopupView(QtGui.QTableView):

    def __init__(self, parent):
        """ Configure the appearence of the table view.
        """
        QtGui.QTableView.__init__(self, parent)
        hheader = self.horizontalHeader()
        hheader.setResizeMode(QtGui.QHeaderView.ResizeToContents)
        hheader.hide()
        vheader = self.verticalHeader()
        vheader.setResizeMode(QtGui.QHeaderView.ResizeToContents)
        vheader.hide()
        self.setShowGrid(False)


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
        return ''

    def paint(self, painter, option, mi):
        """ Reimplemented to draw images.
        """
        # Delegate to our superclass to draw the background
        QtGui.QStyledItemDelegate.paint(self, painter, option, mi)

        # Now draw the pixmap
        name = mi.data(QtCore.Qt.DisplayRole)
        pixmap = self._get_pixmap(name)
        if pixmap is not None:
            target = QtGui.QStyle.alignedRect(QtCore.Qt.LeftToRight,
                                              QtCore.Qt.AlignCenter,
                                              pixmap.size(), option.rect)
            painter.drawPixmap(target, pixmap)

    def sizeHint(self, option, mi):
        """ Reimplemented to define a size hint based on the size of the pixmap.
        """
        name = mi.data(QtCore.Qt.DisplayRole)
        pixmap = self._get_pixmap(name)
        if pixmap is None:
            return QtCore.QSize()
        return pixmap.size()

    def _get_pixmap(self, name):
        return self._editor.get_pixmap(name)


class ImageEnumModel(QtCore.QAbstractTableModel):
    """ A table model for use with the 'simple' style ImageEnumEditor.
    """

    def __init__(self, editor, parent):
        """ Reimplemented to store the editor.
        """
        super(ImageEnumModel, self).__init__(parent)
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
        """ Reimplemented to return the data.
        """
        if role == QtCore.Qt.DisplayRole:
            index = mi.row() * self._editor.factory.cols + mi.column()
            if index < len(self._editor.names):
                return self._editor.names[index]

        return None
