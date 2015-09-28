#------------------------------------------------------------------------------
# Copyright (c) 2007, Riverbank Computing Limited
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD license.
# However, when used with the GPL version of PyQt the additional terms described in the PyQt GPL exception also apply

#
# Author: Riverbank Computing Limited
#------------------------------------------------------------------------------

""" Defines helper functions and classes used to define PyQt-based trait
    editors and trait editor factories.
"""

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

import os.path

from pyface.qt import QtCore, QtGui

from traits.api \
    import Enum, CTrait, BaseTraitHandler, TraitError

from traitsui.ui_traits \
    import convert_image, SequenceTypes

#-------------------------------------------------------------------------------
#  Trait definitions:
#-------------------------------------------------------------------------------

# Layout orientation for a control and its associated editor
Orientation = Enum( 'horizontal', 'vertical' )

#-------------------------------------------------------------------------------
#  Convert an image file name to a cached QPixmap:
#-------------------------------------------------------------------------------

def pixmap_cache(name, path=None):
    """ Return the QPixmap corresponding to a filename. If the filename does not
        contain a path component, 'path' is used (or if 'path' is not specified,
        the local 'images' directory is used).
    """
    if name[:1] == '@':
        image = convert_image(name.replace(' ', '_').lower())
        if image is not None:
            return image.create_image()

    name_path, name = os.path.split(name)
    name = name.replace(' ', '_').lower()
    if name_path:
        filename = os.path.join(name_path, name)
    else:
        if path is None:
            filename = os.path.join(os.path.dirname(__file__), 'images', name)
        else:
            filename = os.path.join(path, name)
    filename = os.path.abspath(filename)

    pm = QtGui.QPixmap()
    if not QtGui.QPixmapCache.find(filename, pm):
        pm.load(filename)
        QtGui.QPixmapCache.insert(filename, pm)
    return pm

#-------------------------------------------------------------------------------
#  Positions a window on the screen with a specified width and height so that
#  the window completely fits on the screen if possible:
#-------------------------------------------------------------------------------

def position_window ( window, width = None, height = None, parent = None ):
    """ Positions a window on the screen with a specified width and height so
        that the window completely fits on the screen if possible.
    """
    # Get the available geometry of the screen containing the window.
    sgeom = QtGui.QApplication.desktop().availableGeometry(window)
    screen_dx = sgeom.width()
    screen_dy = sgeom.height()

    # Use the frame geometry even though it is very unlikely that the X11 frame
    # exists at this point.
    fgeom = window.frameGeometry()
    width = width or fgeom.width()
    height = height or fgeom.height()

    if parent is None:
        parent = window._parent

    if parent is None:
        # Center the popup on the screen.
        window.move((screen_dx - width) / 2, (screen_dy - height) / 2)
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
    window.move(max(0, min(x, screen_dx - width)),
                max(0, min(y, screen_dy - height)))

#-------------------------------------------------------------------------------
#  Restores the user preference items for a specified UI:
#-------------------------------------------------------------------------------

def restore_window ( ui ):
    """ Restores the user preference items for a specified UI.
    """
    prefs = ui.restore_prefs()
    if prefs is not None:
        ui.control.setGeometry( *prefs )

#-------------------------------------------------------------------------------
#  Saves the user preference items for a specified UI:
#-------------------------------------------------------------------------------

def save_window ( ui ):
    """ Saves the user preference items for a specified UI.
    """
    geom = ui.control.geometry()
    ui.save_prefs( (geom.x(), geom.y(), geom.width(), geom.height()) )

#-------------------------------------------------------------------------------
#  Safely tries to pop up an FBI window if etsdevtools.debug is installed
#-------------------------------------------------------------------------------

def open_fbi():
    try:
        from etsdevtools.developer.helper.fbi import if_fbi
        if not if_fbi():
            import traceback
            traceback.print_exc()
    except ImportError:
        pass

#-------------------------------------------------------------------------------
#  'IconButton' class:
#-------------------------------------------------------------------------------

class IconButton(QtGui.QPushButton):
    """ The IconButton class is a push button that contains a small image or a
        standard icon provided by the current style.
    """

    def __init__(self, icon, slot):
        """ Initialise the button.  icon is either the name of an image file or
            one of the QtGui.QStyle.SP_* values.
        """
        QtGui.QPushButton.__init__(self)

        # Get the current style.
        sty = QtGui.QApplication.instance().style()

        # Get the minimum icon size to use.
        ico_sz = sty.pixelMetric(QtGui.QStyle.PM_ButtonIconSize)

        if isinstance(icon, basestring):
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
        self.setMaximumSize(ico_sz, ico_sz)
        self.setFlat(True)
        self.setFocusPolicy(QtCore.Qt.NoFocus)

        self.clicked.connect(slot)

#-------------------------------------------------------------------------------
#  Dock-related stubs.
#-------------------------------------------------------------------------------

DockStyle = Enum('horizontal', 'vertical', 'tab', 'fixed')
