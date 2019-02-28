#------------------------------------------------------------------------------
#
#  Copyright (c) 2006, Enthought, Inc.
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
#  Date:   06/25/2006
#
#------------------------------------------------------------------------------

""" Defines the various editors for a drag-and-drop editor,
    for the wxPython user interface toolkit. A drag-and-drop editor represents
    its value as a simple image which, depending upon the editor style, can be
    a drag source only, a drop target only, or both a drag source and a drop
    target.
"""

#-------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------

from __future__ import absolute_import
import wx
import numpy

from six.moves.cPickle \
    import load

from traits.api \
    import Bool

# FIXME: ToolkitEditorFactory is a proxy class defined here just for backward
# compatibility. The class has been moved to the
# traitsui.editors.dnd_editor file.
from traitsui.editors.dnd_editor \
    import ToolkitEditorFactory

from pyface.wx.drag_and_drop \
    import PythonDropSource, PythonDropTarget, clipboard
import six

try:
    from apptools.io import File
except ImportError:
    File = None

try:
    from apptools.naming.api import Binding
except ImportError:
    Binding = None

from pyface.image_resource \
    import ImageResource

from .editor \
    import Editor

#-------------------------------------------------------------------------
#  Constants:
#-------------------------------------------------------------------------

# The image to use when the editor accepts files:
file_image = ImageResource('file').create_image()

# The image to use when the editor accepts objects:
object_image = ImageResource('object').create_image()

# The image to use when the editor is disabled:
inactive_image = ImageResource('inactive').create_image()

# String types:
string_type = (str, six.text_type)

#-------------------------------------------------------------------------
#  'SimpleEditor' class:
#-------------------------------------------------------------------------


class SimpleEditor(Editor):
    """ Simply style of editor for a drag-and-drop editor, which is both a drag
        source and a drop target.
    """

    #-------------------------------------------------------------------------
    #  Trait definitions:
    #-------------------------------------------------------------------------

    # Is the editor a drop target?
    drop_target = Bool(True)

    # Is the editor a drag source?
    drag_source = Bool(True)

    #-------------------------------------------------------------------------
    #  Finishes initializing the editor by creating the underlying toolkit
    #  widget:
    #-------------------------------------------------------------------------

    def init(self, parent):
        """ Finishes initializing the editor by creating the underlying toolkit
            widget.
        """
        # Determine the drag/drop type:
        value = self.value
        self._is_list = isinstance(value, list)
        self._is_file = (isinstance(value, string_type) or
                         (self._is_list and (len(value) > 0) and
                          isinstance(value[0], string_type)))

        # Get the right image to use:
        image = self.factory.image
        if image is not None:
            image = image.create_image()
            disabled_image = self.factory.disabled_image
            if disabled_image is not None:
                disabled_image = disabled_image.create_image()
        else:
            disabled_image = inactive_image
            image = object_image
            if self._is_file:
                image = file_image

        self._image = image.ConvertToBitmap()
        if disabled_image is not None:
            self._disabled_image = disabled_image.ConvertToBitmap()
        else:
            data = numpy.reshape(numpy.fromstring(image.GetData(),
                                                  numpy.uint8),
                                 (-1, 3)) * numpy.array([[0.297, 0.589, 0.114]])
            g = data[:, 0] + data[:, 1] + data[:, 2]
            data[:, 0] = data[:, 1] = data[:, 2] = g
            image.SetData(numpy.ravel(data.astype(numpy.uint8)).tostring())
            image.SetMaskColour(0, 0, 0)
            self._disabled_image = image.ConvertToBitmap()

        # Create the control and set up the event handlers:
        self.control = control = wx.Window(
            parent, -1, size=wx.Size(image.GetWidth(), image.GetHeight()))
        self.set_tooltip()

        if self.drop_target:
            control.SetDropTarget(PythonDropTarget(self))

        wx.EVT_LEFT_DOWN(control, self._left_down)
        wx.EVT_LEFT_UP(control, self._left_up)
        wx.EVT_MOTION(control, self._mouse_move)
        wx.EVT_PAINT(control, self._on_paint)

    #-------------------------------------------------------------------------
    #  Disposes of the contents of an editor:
    #-------------------------------------------------------------------------

    def dispose(self):
        """ Disposes of the contents of an editor.
        """
        control = self.control
        wx.EVT_LEFT_DOWN(control, None)
        wx.EVT_LEFT_UP(control, None)
        wx.EVT_MOTION(control, None)
        wx.EVT_PAINT(control, None)

        super(SimpleEditor, self).dispose()

    #-------------------------------------------------------------------------
    #  Updates the editor when the object trait changes external to the editor:
    #-------------------------------------------------------------------------

    def update_editor(self):
        """ Updates the editor when the object trait changes externally to the
            editor.
        """
        return

#-- Private Methods ------------------------------------------------------

    #-------------------------------------------------------------------------
    #  Returns the processed version of a drag request's data:
    #-------------------------------------------------------------------------

    def _get_drag_data(self, data):
        """ Returns the processed version of a drag request's data.
        """
        if isinstance(data, list):

            if Binding is not None and isinstance(data[0], Binding):
                data = [item.obj for item in data]

            if File is not None and isinstance(data[0], File):
                data = [item.absolute_path for item in data]
                if not self._is_file:
                    result = []
                    for file in data:
                        item = self._unpickle(file)
                        if item is not None:
                            result.append(item)
                    data = result

        else:
            if Binding is not None and isinstance(data, Binding):
                data = data.obj

            if File is not None and isinstance(data, File):
                data = data.absolute_path
                if not self._is_file:
                    object = self._unpickle(data)
                    if object is not None:
                        data = object

        return data

    #-------------------------------------------------------------------------
    #  Returns the unpickled version of a specified file (if possible):
    #-------------------------------------------------------------------------

    def _unpickle(self, file_name):
        """ Returns the unpickled version of a specified file (if possible).
        """
        with open(file_name, 'rb') as fh:
            try:
                object = load(fh)
            except Exception:
                object = None

        return object

#-- wxPython Event Handlers ----------------------------------------------

    def _on_paint(self, event):
        """ Called when the control needs repainting.
        """
        image = self._image
        control = self.control
        if not control.IsEnabled():
            image = self._disabled_image

        wdx, wdy = control.GetClientSizeTuple()
        wx.PaintDC(control).DrawBitmap(
            image,
            (wdx - image.GetWidth()) / 2,
            (wdy - image.GetHeight()) / 2,
            True)

    def _left_down(self, event):
        """ Handles the left mouse button being pressed.
        """
        if self.control.IsEnabled() and self.drag_source:
            self._x, self._y = event.GetX(), event.GetY()
            self.control.CaptureMouse()

        event.Skip()

    def _left_up(self, event):
        """ Handles the left mouse button being released.
        """
        if self._x is not None:
            self._x = None
            self.control.ReleaseMouse()

        event.Skip()

    def _mouse_move(self, event):
        """ Handles the mouse being moved.
        """
        if self._x is not None:
            if ((abs(self._x - event.GetX()) +
                 abs(self._y - event.GetY())) >= 3):
                self.control.ReleaseMouse()
                self._x = None
                if self._is_file:
                    FileDropSource(self.control, self.value)
                else:
                    PythonDropSource(self.control, self.value)

        event.Skip()

#----- Drag and drop event handlers: -------------------------------------

    #-------------------------------------------------------------------------
    #  Handles a Python object being dropped on the control:
    #-------------------------------------------------------------------------

    def wx_dropped_on(self, x, y, data, drag_result):
        """ Handles a Python object being dropped on the tree.
        """
        try:
            self.value = self._get_drag_data(data)
            return drag_result
        except:
            return wx.DragNone

    #-------------------------------------------------------------------------
    #  Handles a Python object being dragged over the control:
    #-------------------------------------------------------------------------

    def wx_drag_over(self, x, y, data, drag_result):
        """ Handles a Python object being dragged over the tree.
        """
        try:
            self.object.base_trait(
                self.name).validate(
                self.object,
                self.name,
                self._get_drag_data(data))
            return drag_result
        except:
            return wx.DragNone

#-------------------------------------------------------------------------
#  'CustomEditor' class:
#-------------------------------------------------------------------------


class CustomEditor(SimpleEditor):
    """ Custom style of drag-and-drop editor, which is not a drag source.
    """
    #-------------------------------------------------------------------------
    #  Trait definitions:
    #-------------------------------------------------------------------------

    # Is the editor a drag source? This value overrides the default.
    drag_source = False

#-------------------------------------------------------------------------
#  'ReadonlyEditor' class:
#-------------------------------------------------------------------------


class ReadonlyEditor(SimpleEditor):
    """ Read-only style of drag-and-drop editor, which is not a drop target.
    """
    #-------------------------------------------------------------------------
    #  Trait definitions:
    #-------------------------------------------------------------------------

    # Is the editor a drop target? This value overrides the default.
    drop_target = False

#-------------------------------------------------------------------------
#  'FileDropSource' class:
#-------------------------------------------------------------------------


class FileDropSource(wx.DropSource):
    """ Represents a draggable file.
    """
    #-------------------------------------------------------------------------
    #  Initializes the object:
    #-------------------------------------------------------------------------

    def __init__(self, source, files):
        """ Initializes the object.
        """
        self.handler = None
        self.allow_move = True

        # Put the data to be dragged on the clipboard:
        clipboard.data = files
        clipboard.source = source
        clipboard.drop_source = self

        data_object = wx.FileDataObject()
        if isinstance(files, string_type):
            files = [files]

        for file in files:
            data_object.AddFile(file)

        # Create the drop source and begin the drag and drop operation:
        super(FileDropSource, self).__init__(source)
        self.SetData(data_object)
        self.result = self.DoDragDrop(True)

    #-------------------------------------------------------------------------
    #  Called when the data has been dropped:
    #-------------------------------------------------------------------------

    def on_dropped(self, drag_result):
        """ Called when the data has been dropped. """
        return

## EOF ########################################################################
