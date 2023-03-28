# (C) Copyright 2008-2023 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

# ------------------------------------------------------------------------------
# Copyright (c) 2007, Riverbank Computing Limited
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD license.
# However, when used with the GPL version of PyQt the additional terms
# described in the PyQt GPL exception also apply

#
# Author: Riverbank Computing Limited
# ------------------------------------------------------------------------------

""" Defines helper functions and classes used to define PyQt-based trait
    editors and trait editor factories.
"""

import os.path

from pyface.api import SystemMetrics
from pyface.qt import QtCore, QtGui, is_qt5, is_pyqt, qt_api
from pyface.ui_traits import convert_image
from traits.api import Enum, CTrait, BaseTraitHandler, TraitError

from traitsui.ui_traits import SequenceTypes


#: Layout orientation for a control and its associated editor
Orientation = Enum("horizontal", "vertical")

#: Dock-related stubs.
DockStyle = Enum("horizontal", "vertical", "tab", "fixed")


def pixmap_cache(name, path=None):
    """Convert an image file name to a cached QPixmap

    Returns the QPixmap corresponding to a filename. If the filename does not
    contain a path component, 'path' is used (or if 'path' is not specified,
    the local 'images' directory is used).
    """
    if name[:1] == "@":
        image = convert_image(name.replace(" ", "_").lower())
        if image is not None:
            return image.create_image()

    name_path, name = os.path.split(name)
    name = name.replace(" ", "_").lower()
    if name_path:
        filename = os.path.join(name_path, name)
    else:
        if path is None:
            filename = os.path.join(os.path.dirname(__file__), "images", name)
        else:
            filename = os.path.join(path, name)
    filename = os.path.abspath(filename)

    if is_qt5:
        pm = QtGui.QPixmapCache.find(filename)
        if pm is None:
            pm = QtGui.QPixmap(filename)
            QtGui.QPixmapCache.insert(filename, pm)
    else:
        pm = QtGui.QPixmap()
        if not QtGui.QPixmapCache.find(filename, pm):
            pm.load(filename)
            QtGui.QPixmapCache.insert(filename, pm)
    return pm


def position_window(window, width=None, height=None, parent=None):
    """Positions a window on the screen with a specified width and height so
    that the window completely fits on the screen if possible.
    """
    # Get the available geometry of the screen containing the window.
    system_metrics = SystemMetrics()
    screen_dx = system_metrics.screen_width
    screen_dy = system_metrics.screen_height

    # Use the frame geometry even though it is very unlikely that the X11 frame
    # exists at this point.
    fgeom = window.frameGeometry()
    width = width or fgeom.width()
    height = height or fgeom.height()

    if parent is None:
        parent = window._parent

    if parent is None:
        # Center the popup on the screen.
        window.move((screen_dx - width) // 2, (screen_dy - height) // 2)
        return

    # Calculate the desired size of the popup control:
    if isinstance(parent, QtGui.QWidget):
        gpos = parent.mapToGlobal(QtCore.QPoint())
        x = gpos.x()
        y = gpos.y()
        cdx = parent.width()
        cdy = parent.height()

        # Get the frame height of the parent and assume that the window will
        # have a similar frame.  Note that we would really like the height of
        # just the top of the frame.
        pw = parent.window()
        fheight = pw.frameGeometry().height() - pw.height()
    else:
        # Special case of parent being a screen position and size tuple (used
        # to pop-up a dialog for a table cell):
        x, y, cdx, cdy = parent

        fheight = 0

    x -= (width - cdx) / 2
    y += cdy + fheight

    # Position the window (making sure it will fit on the screen).
    window.move(
        max(0, min(x, screen_dx - width)), max(0, min(y, screen_dy - height))
    )


def restore_window(ui):
    """Restores the user preference items for a specified UI."""
    prefs = ui.restore_prefs()
    if prefs is not None:
        ui.control.setGeometry(*prefs)


def save_window(ui):
    """Saves the user preference items for a specified UI."""
    geom = ui.control.geometry()
    ui.save_prefs((geom.x(), geom.y(), geom.width(), geom.height()))


class IconButton(QtGui.QPushButton):
    """The IconButton class is a push button that contains a small image or a
    standard icon provided by the current style.
    """

    def __init__(self, icon, slot):
        """Initialise the button.  icon is either the name of an image file or
        one of the QtGui.QStyle.SP_* values.
        """
        QtGui.QPushButton.__init__(self)

        # Get the current style.
        sty = QtGui.QApplication.instance().style()

        # Get the minimum icon size to use.
        ico_sz = sty.pixelMetric(QtGui.QStyle.PixelMetric.PM_ButtonIconSize)

        if isinstance(icon, str):
            pm = pixmap_cache(icon)

            # Increase the icon size to accomodate the image if needed.
            pm_width = pm.width()
            pm_height = pm.height()

            if ico_sz < pm_width:
                ico_sz = pm_width

            if ico_sz < pm_height:
                ico_sz = pm_height

            ico = QtGui.QIcon(pm)
        else:
            ico = sty.standardIcon(icon)

        # Configure the button.
        self.setIcon(ico)
        self.setFlat(True)
        self.setFocusPolicy(QtCore.Qt.FocusPolicy.NoFocus)

        self.clicked.connect(slot)

    def sizeHint(self):
        """Reimplement sizeHint to return a recommended button size based on
        the size of the icon.

        Returns
        -------
        size : QtCore.QSize
        """
        self.ensurePolished()

        # We want the button to have a size similar to the icon.
        # Using the size computed for a tool button gives a desirable size.
        option = QtGui.QStyleOptionButton()
        self.initStyleOption(option)
        size = self.style().sizeFromContents(
            QtGui.QStyle.ContentsType.CT_ToolButton, option, option.iconSize
        )
        return size


# ------------------------------------------------------------------------
# Text Rendering helpers
# ------------------------------------------------------------------------


def wrap_text_with_elision(text, font, width, height):
    """Wrap paragraphs to fit inside a given size, eliding if too long.

    Parameters
    ----------
    text : unicode
        The text to wrap.
    font : QFont instance
        The font the text will be rendered in.
    width : int
        The width of the box the text will display in.
    height : int
        The height of the box the text will display in.

    Returns
    -------
    lines : list of unicode
        The lines of text to display, split
    """
    # XXX having an LRU cache on this might be useful

    font_metrics = QtGui.QFontMetrics(font)
    line_spacing = font_metrics.lineSpacing()
    y_offset = 0

    lines = []
    for paragraph in text.splitlines():
        line_start = 0
        text_layout = QtGui.QTextLayout(paragraph, font)
        text_layout.beginLayout()
        while y_offset + line_spacing <= height:
            line = text_layout.createLine()
            if not line.isValid():
                break
            line.setLineWidth(int(width))
            line_start = line.textStart()
            line_end = line_start + line.textLength()
            line_text = paragraph[line_start:line_end].rstrip()
            lines.append(line_text)
            y_offset += line_spacing
        text_layout.endLayout()
        if y_offset + line_spacing > height:
            break
    if lines and y_offset + line_spacing > height:
        # elide last line as we ran out of room
        last_line = paragraph[line_start:]
        lines[-1] = font_metrics.elidedText(
            last_line, QtCore.Qt.TextElideMode.ElideRight, width
        )

    return lines


# ------------------------------------------------------------------------
# Object lifetime helpers
# ------------------------------------------------------------------------

def qobject_is_valid(qobject):
    """Return whether the wrapped Qt object is still valid.

    Parameters
    ----------
    qobject : QObject instance
        The wrapped Qt QObject to inspect.

    Returns
    -------
    valid : bool
        Whether or not the underlying C++ object still exists.
    """
    if is_pyqt:
        from sip import isdeleted
        return not isdeleted(qobject)
    elif qt_api == 'pyside2':
        from shiboken2 import isValid
        return isValid(qobject)
    elif qt_api == 'pyside6':
        from shiboken6 import isValid
        return isValid(qobject)
    else:
        # unknown wrapper
        raise RuntimeError("Unknown Qt API {qt_api}")
