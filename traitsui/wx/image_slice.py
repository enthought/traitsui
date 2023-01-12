# (C) Copyright 2004-2023 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

""" Class to aid in automatically computing the 'slice' points for a specified
    ImageResource and then drawing it that it can be 'stretched' to fit a larger
    region than the original image.
"""


import wx

from colorsys import rgb_to_hls

from numpy import reshape, fromstring, uint8

from traits.api import HasPrivateTraits, Instance, Int, List, Color, Enum, Bool

from pyface.image_resource import ImageResource

from .constants import WindowColor

from .constants import is_mac
import traitsui.wx.constants


# -------------------------------------------------------------------------
#  Recursively paint the parent's background if they have an associated image
#  slice.
# -------------------------------------------------------------------------


def paint_parent(dc, window):
    """Recursively paint the parent's background if they have an associated
    image slice.
    """
    parent = window.GetParent()
    slice = getattr(parent, "_image_slice", None)
    if slice is not None:
        x, y = window.GetPosition()
        dx, dy = parent.GetSize()
        slice.fill(dc, -x, -y, dx, dy)
    else:
        # Otherwise, just paint the normal window background color:
        dx, dy = window.GetClientSize()
        if is_mac and hasattr(window, "_border") and window._border:
            dc.SetBackgroundMode(wx.TRANSPARENT)
            dc.SetBrush(wx.Brush(wx.Colour(0, 0, 0, 0)))
        else:
            dc.SetBrush(wx.Brush(parent.GetBackgroundColour()))
        dc.SetPen(wx.TRANSPARENT_PEN)
        dc.DrawRectangle(0, 0, dx, dy)

    return slice


# -------------------------------------------------------------------------
#  'ImageSlice' class:
# -------------------------------------------------------------------------


class ImageSlice(HasPrivateTraits):

    # -- Trait Definitions ----------------------------------------------------

    #: The ImageResource to be sliced and drawn:
    image = Instance(ImageResource)

    #: The minimum number of adjacent, identical rows/columns needed to identify
    #: a repeatable section:
    threshold = Int(10)

    #: The maximum number of 'stretchable' rows and columns:
    stretch_rows = Enum(1, 2)
    stretch_columns = Enum(1, 2)

    #: Width/height of the image borders:
    top = Int()
    bottom = Int()
    left = Int()
    right = Int()

    #: Width/height of the extended image borders:
    xtop = Int()
    xbottom = Int()
    xleft = Int()
    xright = Int()

    #: The color to use for content text:
    content_color = Instance(wx.Colour)

    #: The color to use for label text:
    label_color = Instance(wx.Colour)

    #: The background color of the image:
    bg_color = Color

    #: Should debugging slice lines be drawn?
    debug = Bool(False)

    # -- Private Traits -------------------------------------------------------

    #: The current image's opaque bitmap:
    opaque_bitmap = Instance(wx.Bitmap)

    #: The current image's transparent bitmap:
    transparent_bitmap = Instance(wx.Bitmap)

    #: Size of the current image:
    dx = Int()
    dy = Int()

    #: Size of the current image's slices:
    dxs = List()
    dys = List()

    #: Fixed minimum size of current image:
    fdx = Int()
    fdy = Int()

    # -- Public Methods -------------------------------------------------------

    def fill(self, dc, x, y, dx, dy, transparent=False):
        """'Stretch fill' the specified region of a device context with the
        sliced image.
        """
        # Create the source image dc:
        idc = wx.MemoryDC()
        if transparent:
            idc.SelectObject(self.transparent_bitmap)
        else:
            idc.SelectObject(self.opaque_bitmap)

        # Set up the drawing parameters:
        sdx, sdy = self.dx, self.dx
        dxs, dys = self.dxs, self.dys
        tdx, tdy = dx - self.fdx, dy - self.fdy

        # Calculate vertical slice sizes to use for source and destination:
        n = len(dxs)
        if n == 1:
            pdxs = [
                (0, 0),
                (1, max(1, tdx // 2)),
                (sdx - 2, sdx - 2),
                (1, max(1, tdx - (tdx // 2))),
                (0, 0),
            ]
        elif n == 3:
            pdxs = [
                (dxs[0], dxs[0]),
                (dxs[1], max(0, tdx)),
                (0, 0),
                (0, 0),
                (dxs[2], dxs[2]),
            ]
        else:
            pdxs = [
                (dxs[0], dxs[0]),
                (dxs[1], max(0, tdx // 2)),
                (dxs[2], dxs[2]),
                (dxs[3], max(0, tdx - (tdx // 2))),
                (dxs[4], dxs[4]),
            ]

        # Calculate horizontal slice sizes to use for source and destination:
        n = len(dys)
        if n == 1:
            pdys = [
                (0, 0),
                (1, max(1, tdy // 2)),
                (sdy - 2, sdy - 2),
                (1, max(1, tdy - (tdy // 2))),
                (0, 0),
            ]
        elif n == 3:
            pdys = [
                (dys[0], dys[0]),
                (dys[1], max(0, tdy)),
                (0, 0),
                (0, 0),
                (dys[2], dys[2]),
            ]
        else:
            pdys = [
                (dys[0], dys[0]),
                (dys[1], max(0, tdy // 2)),
                (dys[2], dys[2]),
                (dys[3], max(0, tdy - (tdy // 2))),
                (dys[4], dys[4]),
            ]

        # Iterate over each cell, performing a stretch fill from the source
        # image to the destination window:
        last_x, last_y = x + dx, y + dy
        y0, iy0 = y, 0
        for idy, wdy in pdys:
            if y0 >= last_y:
                break

            if wdy != 0:
                x0, ix0 = x, 0
                for idx, wdx in pdxs:
                    if x0 >= last_x:
                        break

                    if wdx != 0:
                        self._fill(
                            idc, ix0, iy0, idx, idy, dc, x0, y0, wdx, wdy
                        )
                        x0 += wdx
                    ix0 += idx
                y0 += wdy
            iy0 += idy

        if self.debug:
            dc.SetPen(wx.Pen(wx.RED))
            dc.DrawLine(x, y + self.top, last_x, y + self.top)
            dc.DrawLine(
                x, last_y - self.bottom - 1, last_x, last_y - self.bottom - 1
            )
            dc.DrawLine(x + self.left, y, x + self.left, last_y)
            dc.DrawLine(
                last_x - self.right - 1, y, last_x - self.right - 1, last_y
            )

    # -- Event Handlers -------------------------------------------------------

    def _image_changed(self, image):
        """Handles the 'image' trait being changed."""
        # Save the original bitmap as the transparent version:
        self.transparent_bitmap = (
            bitmap
        ) = image.create_image().ConvertToBitmap()

        # Save the bitmap size information:
        self.dx = dx = bitmap.GetWidth()
        self.dy = dy = bitmap.GetHeight()

        # Create the opaque version of the bitmap:
        self.opaque_bitmap = wx.Bitmap(dx, dy)
        mdc2 = wx.MemoryDC()
        mdc2.SelectObject(self.opaque_bitmap)
        mdc2.SetBrush(wx.Brush(WindowColor))
        mdc2.SetPen(wx.TRANSPARENT_PEN)
        mdc2.DrawRectangle(0, 0, dx, dy)
        mdc = wx.MemoryDC()
        mdc.SelectObject(bitmap)
        mdc2.Blit(0, 0, dx, dy, mdc, 0, 0, useMask=True)
        mdc.SelectObject(wx.NullBitmap)
        mdc2.SelectObject(wx.NullBitmap)

        # Finally, analyze the image to find out its characteristics:
        self._analyze_bitmap()

    # -- Private Methods ------------------------------------------------------

    def _analyze_bitmap(self):
        """Analyzes the bitmap."""
        # Get the image data:
        threshold = self.threshold
        bitmap = self.opaque_bitmap
        dx, dy = self.dx, self.dy
        image = bitmap.ConvertToImage()

        # Convert the bitmap data to a numpy array for analysis:
        data = reshape(image.GetData(), (dy, dx, 3)).astype(uint8)

        # Find the horizontal slices:
        matches = []
        y, last = 0, dy - 1
        max_diff = 0.10 * dx
        while y < last:
            y_data = data[y]
            for y2 in range(y + 1, dy):
                if abs(y_data - data[y2]).sum() > max_diff:
                    break

            n = y2 - y
            if n >= threshold:
                matches.append((y, n))

            y = y2

        n = len(matches)
        if n == 0:
            if dy > 50:
                matches = [(0, dy)]
            else:
                matches = [(dy // 2, 1)]
        elif n > self.stretch_rows:
            matches.sort(key=lambda x: x[1], reverse=True)
            matches = matches[: self.stretch_rows]

        # Calculate and save the horizontal slice sizes:
        self.fdy, self.dys = self._calculate_dxy(dy, matches)

        # Find the vertical slices:
        matches = []
        x, last = 0, dx - 1
        max_diff = 0.10 * dy
        while x < last:
            x_data = data[:, x]
            for x2 in range(x + 1, dx):
                if abs(x_data - data[:, x2]).sum() > max_diff:
                    break

            n = x2 - x
            if n >= threshold:
                matches.append((x, n))

            x = x2

        n = len(matches)
        if n == 0:
            if dx > 50:
                matches = [(0, dx)]
            else:
                matches = [(dx // 2, 1)]
        elif n > self.stretch_columns:
            matches.sort(key=lambda x: x[1], reverse=True)
            matches = matches[: self.stretch_columns]

        # Calculate and save the vertical slice sizes:
        self.fdx, self.dxs = self._calculate_dxy(dx, matches)

        # Save the border size information:
        self.top = min(dy // 2, self.dys[0])
        self.bottom = min(dy // 2, self.dys[-1])
        self.left = min(dx // 2, self.dxs[0])
        self.right = min(dx // 2, self.dxs[-1])

        # Find the optimal size for the borders (i.e. xleft, xright, ... ):
        self._find_best_borders(data)

        # Save the background color:
        x, y = (dx // 2), (dy // 2)
        r, g, b = data[y, x]
        self.bg_color = (0x10000 * r) + (0x100 * g) + b

        # Find the best contrasting text color (black or white):
        self.content_color = self._find_best_color(data, x, y)

        # Find the best contrasting label color:
        if self.xtop >= self.xbottom:
            self.label_color = self._find_best_color(data, x, self.xtop // 2)
        else:
            self.label_color = self._find_best_color(
                data, x, dy - (self.xbottom // 2) - 1
            )

    def _fill(self, idc, ix, iy, idx, idy, dc, x, y, dx, dy):
        """Performs a stretch fill of a region of an image into a region of a
        window device context.
        """
        last_x, last_y = x + dx, y + dy
        while y < last_y:
            ddy = min(idy, last_y - y)
            x0 = x
            while x0 < last_x:
                ddx = min(idx, last_x - x0)
                dc.Blit(x0, y, ddx, ddy, idc, ix, iy, useMask=True)
                x0 += ddx
            y += ddy

    def _calculate_dxy(self, d, matches):
        """Calculate the size of all image slices for a specified set of
        matches.
        """
        if len(matches) == 1:
            d1, d2 = matches[0]

            return (d - d2, [d1, d2, d - d1 - d2])

        d1, d2 = matches[0]
        d3, d4 = matches[1]

        return (d - d2 - d4, [d1, d2, d3 - d1 - d2, d4, d - d3 - d4])

    def _find_best_borders(self, data):
        """Find the best set of image slice border sizes (e.g. for images with
        rounded corners, there should exist a better set of borders than
        the ones computed by the image slice algorithm.
        """
        # Make sure the image size is worth bothering about:
        dx, dy = self.dx, self.dy
        if (dx < 5) or (dy < 5):
            return

        # Calculate the starting point:
        left = right = dx // 2
        top = bottom = dy // 2

        # Calculate the end points:
        last_y = dy - 1
        last_x = dx - 1

        # Mark which edges as 'scanning':
        t = b = l = r = True

        # Keep looping while at last one edge is still 'scanning':
        while l or r or t or b:

            # Calculate the current core area size:
            height = bottom - top + 1
            width = right - left + 1

            # Try to extend all edges that are still 'scanning':
            nl = (
                l
                and (left > 0)
                and self._is_equal(data, left - 1, top, left, top, 1, height)
            )

            nr = (
                r
                and (right < last_x)
                and self._is_equal(data, right + 1, top, right, top, 1, height)
            )

            nt = (
                t
                and (top > 0)
                and self._is_equal(data, left, top - 1, left, top, width, 1)
            )

            nb = (
                b
                and (bottom < last_y)
                and self._is_equal(
                    data, left, bottom + 1, left, bottom, width, 1
                )
            )

            # Now check the corners of the edges:
            tl = (
                (not nl)
                or (not nt)
                or self._is_equal(data, left - 1, top - 1, left, top, 1, 1)
            )

            tr = (
                (not nr)
                or (not nt)
                or self._is_equal(data, right + 1, top - 1, right, top, 1, 1)
            )

            bl = (
                (not nl)
                or (not nb)
                or self._is_equal(
                    data, left - 1, bottom + 1, left, bottom, 1, 1
                )
            )

            br = (
                (not nr)
                or (not nb)
                or self._is_equal(
                    data, right + 1, bottom + 1, right, bottom, 1, 1
                )
            )

            # Calculate the new edge 'scanning' values:
            l = nl and tl and bl
            r = nr and tr and br
            t = nt and tl and tr
            b = nb and bl and br

            # Adjust the coordinate of an edge if it is still 'scanning':
            left -= l
            right += r
            top -= t
            bottom += b

        # Now compute the best set of image border sizes using the current set
        # and the ones we just calculated:
        self.xleft = min(self.left, left)
        self.xright = min(self.right, dx - right - 1)
        self.xtop = min(self.top, top)
        self.xbottom = min(self.bottom, dy - bottom - 1)

    def _find_best_color(self, data, x, y):
        """Find the best contrasting text color for a specified pixel
        coordinate.
        """
        r, g, b = data[y, x]
        h, l, s = rgb_to_hls(r / 255.0, g / 255.0, b / 255.0)
        text_color = wx.Colour(wx.BLACK)
        if l < 0.50:
            text_color = wx.Colour(wx.WHITE)

        return text_color

    def _is_equal(self, data, x0, y0, x1, y1, dx, dy):
        """Determines if two identically sized regions of an image array are
        'the same' (i.e. within some slight color variance of each other).
        """
        return (
            abs(
                data[y0 : y0 + dy, x0 : x0 + dx]
                - data[y1 : y1 + dy, x1 : x1 + dx]
            ).sum()
            < 0.10 * dx * dy
        )


# -------------------------------------------------------------------------
#  Returns a (possibly cached) ImageSlice:
# -------------------------------------------------------------------------

image_slice_cache = {}


def image_slice_for(image):
    """Returns a (possibly cached) ImageSlice."""
    global image_slice_cache

    result = image_slice_cache.get(image)
    if result is None:
        image_slice_cache[image] = result = ImageSlice(image=image)

    return result
