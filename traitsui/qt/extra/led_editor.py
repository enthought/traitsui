# (C) Copyright 2004-2023 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

from pyface.qt import QtGui
from traitsui.qt.editor import Editor
from traitsui.basic_editor_factory import BasicEditorFactory
from traits.api import Any, Undefined


class _LEDEditor(Editor):
    def init(self, parent):
        self.control = QtGui.QLCDNumber()
        self.control.setSegmentStyle(QtGui.QLCDNumber.SegmentStyle.Flat)
        self.set_tooltip()

    def update_editor(self):
        self.control.display(self.str_value)


class LEDEditor(BasicEditorFactory):

    #: The editor class to be created
    klass = _LEDEditor
    #: Alignment is not supported for QT backend
    alignment = Any(Undefined)
