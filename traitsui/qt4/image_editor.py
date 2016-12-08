#-------------------------------------------------------------------------
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
#  Date:   07/21/2009
#
#-------------------------------------------------------------------------

""" Traits UI 'display only' image editor.
"""

#-------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------

from __future__ import absolute_import

from pyface.qt.QtGui import QFrame, QPainter, QPalette

from pyface.image_resource import ImageResource
from pyface.ui_traits import convert_bitmap

# FIXME: ImageEditor is a proxy class defined here just for backward
# compatibility. The class has been moved to the
# traitsui.editors.image_editor file.
from traitsui.editors.image_editor import ImageEditor

from .editor import Editor

#-------------------------------------------------------------------------
#  'QImageView' class:
#-------------------------------------------------------------------------

# backported and modified from Enaml ImageView


class QImageView(QFrame):
    """ A custom QFrame that will paint a QPixmap as an image. The
    api is similar to QLabel, but with a few more options to control
    how the image scales.

    """

    def __init__(self, parent=None):
        """ Initialize a QImageView.

        Parameters
        ----------
        parent : QWidget or None, optional
            The parent widget of this image viewer.

        """
        super(QImageView, self).__init__(parent)
        self._pixmap = None
        self._scaled_contents = False
        self._allow_upscaling = False
        self._preserve_aspect_ratio = False
        self._allow_clipping = False

        self.setBackgroundRole(QPalette.Window)

    #--------------------------------------------------------------------------
    # Private API
    #--------------------------------------------------------------------------
    def paintEvent(self, event):
        """ A custom paint event handler which draws the image according
        to the current size constraints.

        """
        pixmap = self._pixmap
        if pixmap is None:
            return

        pm_size = pixmap.size()
        pm_width = pm_size.width()
        pm_height = pm_size.height()
        if pm_width == 0 or pm_height == 0:
            return

        width = self.size().width()
        height = self.size().height()

        if not self._scaled_contents:
            # If the image isn't scaled, it is centered if possible.
            # Otherwise, it's painted at the origin and clipped.
            paint_x = max(0, int(width / 2. - pm_width / 2.))
            paint_y = max(0, int(height / 2. - pm_height / 2.))
            paint_width = pm_width
            paint_height = pm_height
        else:
            # If the image *is* scaled, it's scaled size depends on the
            # size of the paint area as well as the other scaling flags.
            if self._preserve_aspect_ratio:
                pm_ratio = float(pm_width) / pm_height
                ratio = float(width) / height
                if ratio >= pm_ratio:
                    if self._allow_upscaling:
                        paint_height = height
                    else:
                        paint_height = min(pm_height, height)
                    paint_width = int(paint_height * pm_ratio)
                else:
                    if self._allow_upscaling:
                        paint_width = width
                    else:
                        paint_width = min(pm_width, width)
                    paint_height = int(paint_width / pm_ratio)
            else:
                if self._allow_upscaling:
                    paint_height = height
                    paint_width = width
                else:
                    paint_height = min(pm_height, height)
                    paint_width = min(pm_width, width)
            # In all cases of scaling, we know that the scaled image is
            # no larger than the paint area, and can thus be centered.
            paint_x = int(width / 2. - paint_width / 2.)
            paint_y = int(height / 2. - paint_height / 2.)

        # Finally, draw the pixmap into the calculated rect.
        painter = QPainter(self)
        painter.setRenderHint(QPainter.SmoothPixmapTransform)
        painter.drawPixmap(paint_x, paint_y, paint_width, paint_height, pixmap)

    #--------------------------------------------------------------------------
    # Public API
    #--------------------------------------------------------------------------
    def sizeHint(self):
        """ Returns a appropriate size hint for the image based on the
        underlying QPixmap.

        """
        pixmap = self._pixmap
        if pixmap is not None:
            return pixmap.size()
        return super(QImageView, self).sizeHint()

    def minimumSizeHint(self):
        """ Returns a appropriate minimum size hint for the image based on the
        underlying QPixmap.

        """
        pixmap = self._pixmap
        if pixmap is not None and not self._allow_clipping and not self._scaled_contents:
            return pixmap.size()
        return super(QImageView, self).sizeHint()

    def pixmap(self):
        """ Returns the underlying pixmap for the image view.

        """
        return self._pixmap

    def setPixmap(self, pixmap):
        """ Set the pixmap to use as the image in the widget.

        Parameters
        ----------
        pixamp : QPixmap
            The QPixmap to use as the image in the widget.

        """
        self._pixmap = pixmap
        self.update()

    def scaledContents(self):
        """ Returns whether or not the contents scale with the widget
        size.

        """
        return self._scaled_contents

    def setScaledContents(self, scaled):
        """ Set whether the contents scale with the widget size.

        Parameters
        ----------
        scaled : bool
            If True, the image will be scaled to fit the widget size,
            subject to the other sizing constraints in place. If False,
            the image will not scale and will be clipped as required.

        """
        self._scaled_contents = scaled
        self.update()

    def allowUpscaling(self):
        """ Returns whether or not the image can be scaled greater than
        its natural size.

        """
        return self._allow_upscaling

    def setAllowUpscaling(self, allow):
        """ Set whether or not to allow the image to be scaled beyond
        its natural size.

        Parameters
        ----------
        allow : bool
            If True, then the image may be scaled larger than its
            natural if it is scaled to fit. If False, the image will
            never be scaled larger than its natural size. In either
            case, the image may be scaled smaller.

        """
        self._allow_upscaling = allow
        self.update()

    def preserveAspectRatio(self):
        """ Returns whether or not the aspect ratio of the image is
        maintained during a resize.

        """
        return self._preserve_aspect_ratio

    def setPreserveAspectRatio(self, preserve):
        """ Set whether or not to preserve the image aspect ratio.

        Parameters
        ----------
        preserve : bool
            If True then the aspect ratio of the image will be preserved
            if it is scaled to fit. Otherwise, the aspect ratio will be
            ignored.

        """
        self._preserve_aspect_ratio = preserve
        self.update()

    def allowClipping(self):
        """ Returns whether or not the image should be clipped in the view.

        """
        return self._preserve_aspect_ratio

    def setAllowClipping(self, allow):
        """ Set whether or not the image should be clipped in the view.

        Parameters
        ----------
        allow : bool
            If True then clipping will be allowed.  Otherwise the minimum
            size hint will be the image size.

        """
        self._allow_clipping = allow
        self.update()


#-------------------------------------------------------------------------
#  '_ImageEditor' class:
#-------------------------------------------------------------------------

class _ImageEditor(Editor):
    """ Traits UI 'display only' image editor.
    """

    #-------------------------------------------------------------------------
    #  Finishes initializing the editor by creating the underlying toolkit
    #  widget:
    #-------------------------------------------------------------------------

    def init(self, parent):
        """ Finishes initializing the editor by creating the underlying toolkit
            widget.
        """
        image = self.factory.image
        if image is None:
            image = self.value

        self.control = QImageView()
        self.control.setPixmap(convert_bitmap(image))
        self.control.setScaledContents(self.factory.scale)
        self.control.setAllowUpscaling(self.factory.allow_upscaling)
        self.control.setPreserveAspectRatio(self.factory.preserve_aspect_ratio)
        self.control.setAllowClipping(self.factory.allow_clipping)

        self.set_tooltip()

    #-------------------------------------------------------------------------
    #  Updates the editor when the object trait changes external to the editor:
    #-------------------------------------------------------------------------

    def update_editor(self):
        """ Updates the editor when the object trait changes externally to the
            editor.
        """
        if self.factory.image is None:
            value = self.value
            if isinstance(value, ImageResource):
                self.control.setPixmap(convert_bitmap(value))
        self.control.setScaledContents(self.factory.scale)
        self.control.setAllowUpscaling(self.factory.allow_upscaling)
        self.control.setPreserveAspectRatio(self.factory.preserve_aspect_ratio)
        self.control.setAllowClipping(self.factory.allow_clipping)
